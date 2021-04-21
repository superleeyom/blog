# [k8s实现Spring Cloud服务平滑升级解决方案](https://github.com/superleeyom/blog/issues/27)

## 背景

目前公司的服务是用 Spring Cloud 框架，且服务采用 k8s 进行部署，但是有新的服务需要升级的时候，虽然采用目前采用的滚动更新的方式，但是由于服务注册到 Eureka 上去的时候，会有30秒到1分钟左右不等的时间，这段时间会造成线上服务短时间的不能访问，所以在服务升级的时候，让服务能平滑升级达到用户无感的效果这是非常有必要的。

## 原因分析

在 Spring Cloud 的服务中，用户访问的一般都是网关（Gateway 或 Zuul），通过网关进行一次中转再去访问内部的服务，但是通过网关访问内部服务时需要一个过程，一般流程是这样的：服务启动好了后会先将自己注册信息（服务名->ip:端口）注册（上报）到 Eureka 注册中心，以便其他服务能访问到它，然后其他服务会定时访问（轮询 fetch 的默认时间间隔是 30s ）注册中心以获取到 Eureka 中最新的服务注册列表。

那么通过k8s按照滚动更新新的方式来更新服务的话，就可能出现这样的情况：

> 在 T 时刻，serverA_1（老服务）已经 down 了，serverA_2（新服务）已经启动好，并已注册到了 eureka 中，但是对于 gateway 中缓存的注册列表中存在的仍是 serverA_1（老服务）的注册信息，那么此时用户去访问 serverA 就会报错的，因为serverA_1 所在的容器都已经 stop 了。

## 解决办法

### Eureka参数优化

#### Client端

```yml
eureka:
  client:
    # 表示eureka client间隔多久去拉取服务注册信息，默认为30秒
    registryFetchIntervalSeconds: 5
ribbon:
  # ribbon本地服务列表刷新间隔时间，默认为30秒
  ServerListRefreshInterval: 5000
```

#### Server端

```yml
eureka:
  server:
    # eureka server清理无效节点的时间间隔，默认60秒
    eviction-interval-timer-in-ms: 5000
    # eureka server刷新readCacheMap（二级缓存）的时间，默认时间30秒
    response-cache-update-interval-ms: 5000
```

以上两个优化主要是缩短服务上线下线的时候，尽可能快的刷新 eureka client 端和 server 端服务注册列表的缓存。

### 网关开启重试机制

因为我们用的是 zuul 网关，开启重试机制，防止在滚动更新的时候，由于网关层 server list 的缓存，将请求打到已下线的节点，zuul 请求失败后，会自动重试一次，重试其他节点，不至于直接报错给用户：

```yml
ribbon:
  # 同一实例最大重试次数，不包括首次调用
  MaxAutoRetries: 0
  # 重试其他实例的最大重试次数，不包括首次所选的server
  MaxAutoRetriesNextServer: 1
  # 是否所有操作都进行重试
  OkToRetryOnAllOperations: false
zuul:
  # 开启Zuul重试功能
  retryable: true
```

关于 OkToRetryOnAllOperations 属性，默认值是 false，只有在请求是 GET 的时候会重试，但是如果设置为 true的话，这样设置之后所有的类型的方法（GET、POST、PUT、DELETE等）都会进行重试，server 端需要保证接口的幂等性，例如发生 read timeout 时，若接口不是幂等的，则可能会造成脏数据，这个是需要注意的点！

### 需要下线的服务主动从注册中心里移除

利用k8s的容器回调 PreStop 钩子，在容器被stop终止之前，将需要被 down 的服务主动从注册中心进行移除，针对容器，有两种类型的回调处理程序可供实现：

- Exec - 在容器的 cgroups 和名称空间中执行特定的命令（例如 `pre-stop.sh`）， 命令所消耗的资源计入容器的资源消耗。

  ```yml
  lifecycle:
    preStop:
      exec:
        command:
          - bash
          - -c                
          - 'curl -X "POST" "http://127.0.0.1:9401/ticket/actuator/service-registry?status=DOWN" -H "Content-Type: application/vnd.spring-boot.actuator.v2+json;charset=UTF-8";sleep 90'
  ```

  同时指定一下 k8s 优雅终止宽限期：`terminationGracePeriodSeconds: 90`，配置中添加了一个 sleep 时间，主要是作为服务停止的缓冲时间，解决可能有部分的请求存在未处理完成，就被停止的问题。这里采用的是 Eurek Client 自带的强制下线接口，这里需要注意的是，此方式需要服务引入`spring-boot-starter-actuator`组件，要求该服务对`/actuator/service-registry`加入白名单，同时基础镜像得安装 `curl` 命令才行。

- HTTP - 对容器上的特定端点执行 HTTP 请求。

  ```yml
	lifecycle:
	  preStop:
	    httpGet:
		path: /eureka/stop/client
		port: 8080
  ```

  用 http 的方式，则需要我们在每个服务的里面，在代码层面将当前服务主动从注册中心进行移除：

  ```java
  @RestController
  public class EurekaShutdownController {
  
      @Autowired
      private EurekaClient eurekaClient;
  
      @GetMapping("/eureka/stop/client")
      public ResultDto stopEurekaClient() {
          eurekaClient.shutdown();
          return new ResultDto(Consts.ErrCode.SUCCESS, "服务下线成功！");
      }
  }
  ```

  需要注意的是，如果有的服务需有黑白名单，记得要把`/eureka/stop/client`加入白名单，如果有的服务有设置 context-path，注意需要加前缀，否则被拦截，就没有什么作用了。

### 延迟就绪探针首次探针时间

在服务的 k8s 的 deployment 配置文件中添加 redainessProbe 和 livenessProbe，这两个有什么区别呢？

- LivenessProbe（存活探针）：存活探针主要作用是，**用指定的方式进入容器检测容器中的应用是否正常运行**，如果检测失败，则认为容器不健康，那么 `Kubelet` 将根据 `Pod` 中设置的 `restartPolicy` （重启策略）来判断，Pod 是否要进行重启操作，如果容器配置中没有配置 `livenessProbe` 存活探针，`Kubelet` 将认为存活探针探测一直为成功状态。

  ```yml
  livenessProbe:
      initialDelaySeconds: 35
      periodSeconds: 5
      timeoutSeconds: 10
      httpGet:
          scheme: HTTP
          port: 8081
          path: /actuator/health
  ```

  上面 Pod 中启动的容器是一个 SpringBoot 应用，其中引用了 `Actuator` 组件，提供了 `/actuator/health` 健康检查地址，存活探针可以使用 `HTTPGet` 方式向服务发起请求，请求 `8081` 端口的 `/actuator/health` 路径来进行存活判断。

- ReadinessProbe（就绪探针）：用于判断容器中应用是否启动完成，**当探测成功后才使 Pod 对外提供网络访问**，设置容器 `Ready` 状态为 `true`，如果探测失败，则设置容器的 `Ready` 状态为 `false`。对于被 Service 管理的 Pod，`Service` 与 `Pod`、`EndPoint` 的关联关系也将基于 Pod 是否为 `Ready` 状态进行设置，如果 Pod 运行过程中 `Ready` 状态变为 `false`，则系统自动从 `Service` 关联的 `EndPoint` 列表中移除，如果 Pod 恢复为 `Ready` 状态。将再会被加回 `Endpoint` 列表。**通过这种机制就能防止将流量转发到不可用的 Pod 上**。

  ```yml
  readinessProbe:
      initialDelaySeconds: 30
      periodSeconds: 10
      httpGet:
          scheme: HTTP
          port: 8081
          path: /actuator/health
  ```

  `periodSeconds` 参数表示探针每隔多久检测一次，这里设置为 10s，参数` initialDelaySeconds` 代表首次探针的延迟时间，这里的 30 就是指待 pod 启动好了后，再等待 30 秒再进行存活性检测，跟存活指针一样，使用 `HTTPGet` 方式向服务发起请求，请求 `8081` 端口（不同的服务端口可能不一样，按照实际端口进行修改）的 `/actuator/health` （如果有的服务有设置 context-path，注意需要加前缀）路径来进行存活判断，若请求成功，代表服务已就绪，这样配置的话就会达到新的服务启动好了30秒后 k8s 才会让旧服务 down 掉，而30秒后，经过优化Eureka配置后，基本上所有的服务都已经从 Eureka 获取到了新服务的注册信息了。

这里在实际操作的时候，LivenessProbe 的 initialDelaySeconds 的值要大于 ReadinessProbe 的 initialDelaySeconds 的值，否则pod节点会起不起来，因为此时 pod 还没有就绪，存活指针就去探测的话，肯定是会失败的，这时候 k8s 会认为此 pod 已经不存活，就会把 pod 销毁重建。

### 优雅停机保证正在执行的业务操作不受影响

首先先明确旧 Pod 是怎么下线的，如果是 linux 系统，会默认执行`kill -15`的命令，通知 web 应用停止，最后 Pod 删除。那什么叫优雅停机？他的作用是什么？简单说就是，在对应用进程发送停止指令之后，能保证正在执行的业务操作不受影响。应用接收到停止指令之后的步骤应该是，停止接收访问请求，等待已经接收到的请求处理完成，并能成功返回，这时才真正停止应用。`SpringBoot 2.3` 目前已支持了优雅停机，当使用`server.shutdown=graceful`启用时，在 web 容器关闭时，web 服务器将不再接收新请求，并将等待活动请求完成的缓冲期。但是我们公司使用的 SpringBoot 版本为 `2.1.5.RELEASE`，需要通过编写部分额外的代码去实现优雅停机，根据 web 容器的不同，有分为` tomcat` 和 `undertow` 的解决方案：

#### tomcat 方案

```java
/**
 * 优雅关闭 Spring Boot tomcat
 */
@Slf4j
@Component
public class GracefulShutdownTomcat implements TomcatConnectorCustomizer, ApplicationListener<ContextClosedEvent> {
    private volatile Connector connector;
    private final int waitTime = 30;

    @Override
    public void customize(Connector connector) {
        this.connector = connector;
    }

    @Override
    public void onApplicationEvent(ContextClosedEvent contextClosedEvent) {
        this.connector.pause();
        Executor executor = this.connector.getProtocolHandler().getExecutor();
        if (executor instanceof ThreadPoolExecutor) {
            try {
                ThreadPoolExecutor threadPoolExecutor = (ThreadPoolExecutor) executor;
                threadPoolExecutor.shutdown();
                if (!threadPoolExecutor.awaitTermination(waitTime, TimeUnit.SECONDS)) {
                    log.warn("Tomcat thread pool did not shut down gracefully within " + waitTime + " seconds. Proceeding with forceful shutdown");
                }
            } catch (InterruptedException ex) {
                Thread.currentThread().interrupt();
            }
        }
    }
}
```

```java
@EnableDiscoveryClient
@SpringBootApplication
public class ShutdownApplication {

    public static void main(String[] args) {
        SpringApplication.run(ShutdownApplication.class, args);
    }

    @Autowired
    private GracefulShutdownTomcat gracefulShutdownTomcat;

    @Bean
    public ServletWebServerFactory servletContainer() {
        TomcatServletWebServerFactory tomcat = new TomcatServletWebServerFactory();
        tomcat.addConnectorCustomizers(gracefulShutdownTomcat);
        return tomcat;
    }
}
```

#### undertow方案

```java
/**
 * 优雅关闭 Spring Boot undertow
 */
@Component
public class GracefulShutdownUndertow implements ApplicationListener<ContextClosedEvent> {

    @Autowired
    private GracefulShutdownUndertowWrapper gracefulShutdownUndertowWrapper;

    @Autowired
    private ServletWebServerApplicationContext context;

    @Override
    public void onApplicationEvent(ContextClosedEvent contextClosedEvent) {
        gracefulShutdownUndertowWrapper.getGracefulShutdownHandler().shutdown();
        try {
            UndertowServletWebServer webServer = (UndertowServletWebServer)context.getWebServer();
            Field field = webServer.getClass().getDeclaredField("undertow");
            field.setAccessible(true);
            Undertow undertow = (Undertow) field.get(webServer);
            List<Undertow.ListenerInfo> listenerInfo = undertow.getListenerInfo();
            Undertow.ListenerInfo listener = listenerInfo.get(0);
            ConnectorStatistics connectorStatistics = listener.getConnectorStatistics();
            while (connectorStatistics.getActiveConnections() > 0){}
        } catch (Exception e) {
            // Application Shutdown
        }
    }
}
```

```java
@Component
public class GracefulShutdownUndertowWrapper implements HandlerWrapper {
    private GracefulShutdownHandler gracefulShutdownHandler;
    @Override
    public HttpHandler wrap(HttpHandler handler) {
        if(gracefulShutdownHandler == null) {
            this.gracefulShutdownHandler = new GracefulShutdownHandler(handler);
        }
        return gracefulShutdownHandler;
    }
    public GracefulShutdownHandler getGracefulShutdownHandler() {
        return gracefulShutdownHandler;
    }
}
```

```java
public class UnipayProviderApplication {
    public static void main(String[] args) {
        SpringApplication.run(UnipayProviderApplication.class);
    }
    @Autowired
    private GracefulShutdownUndertowWrapper gracefulShutdownUndertowWrapper;
    @Bean
    public UndertowServletWebServerFactory servletWebServerFactory() {
        UndertowServletWebServerFactory factory = new UndertowServletWebServerFactory();
        factory.addDeploymentInfoCustomizers(deploymentInfo -> deploymentInfo.addOuterHandlerChainWrapper(gracefulShutdownUndertowWrapper));
        factory.addBuilderCustomizers(builder -> builder.setServerOption(UndertowOptions.ENABLE_STATISTICS, true));
        return factory;
    }
}
```

## 参考资料

- [详解k8s中的liveness和readiness的原理和区别](https://xuxinkun.github.io/2019/10/28/liveness-readiness/)
- [Spring Boot 内嵌容器 Tomcat / Undertow / Jetty 优雅停机实现](http://www.spring4all.com/article/1022)
- [Spring Boot 2.0 之优雅停机](https://www.appblog.cn/2019/11/21/Spring%20Boot%202.0%20%E4%B9%8B%E4%BC%98%E9%9B%85%E5%81%9C%E6%9C%BA/#Spring-boot-%E4%BC%98%E9%9B%85%E5%81%9C%E6%9C%BA)
- [k8s + spring boot + Eureka如何平滑上下线服务](https://blog.csdn.net/zk18286047195/article/details/106054003)
- [kubernetes实现spring cloud服务平滑升级的一种解决方案](https://blog.csdn.net/puhaiyang/article/details/104649289)
- [在 k8s 中配置 Spring Cloud 服务 (Eureka 客户端) 优雅下线](https://ld246.com/article/1600336699372)
- [pod健康检查（LivenessProbe和ReadinessProbe）](https://www.cnblogs.com/normanlin/p/10630889.html)
- [Kubernetes Pod 健康检查机制 LivenessProbe 与 ReadinessProbe](http://www.mydlq.club/article/39/)
- [Spring Cloud Zuul重试机制探秘](https://blog.didispace.com/spring-cloud-zuul-retry-detail/)
- [Ribbon超时与重试](https://www.xiefayang.com/2019/04/26/Ribbon%E2%80%94%E2%80%94%E8%B6%85%E6%97%B6%E4%B8%8E%E9%87%8D%E8%AF%95/)