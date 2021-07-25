# [对k8s中Service的理解](https://github.com/superleeyom/blog/issues/36)

以下是我基于实际生产实践，对于k8s里关于Service的一些比较粗浅的理解，如果有些不对的地方，欢迎指出，这些理解基于腾讯云的容器服务TKE，之前一直对这个概念比较模糊，结合腾讯云TKE上的文档，后面请教了同事鲲鹏后，总算是有点清晰了，首先先明确Service的基本概念：

> 用户在 Kubernetes 中可以部署各种容器，其中一部分是通过 HTTP、HTTPS 协议对外提供七层网络服务，另一部分是通过 TCP、UDP 协议提供四层网络服务。而 Kubernetes 定义的 Service 资源就是用来管理集群中四层网络的服务访问。


Kubernetes 的 `ServiceTypes` 允许指定 Service 类型，默认为 `ClusterIP` 类型。`ServiceTypes` 的可取值如下：

## **ClusterIP** 

通过集群的内部 `IP` 暴露服务。当我们的服务只需要在集群内部被访问时，可以使用该类型。打个比方吧（实际生产不推荐这样做），比如你的一个服务调用另外一个服务，需要明确知道另外一个服务的ip，那这个时候，就可以为该被调用方Pod创建一个service，固定一个ip，此时这个ip只能是在这个集群内部访问，创建一个Service的时候，无论是那种的`ServiceTypes`都会生成一个虚拟ip，腾讯云TKE上叫服务ip。

![](http://image.leeyom.top/blog/20210723175013.png)

## NodePort

通过每个集群节点上的 `IP` 和静态端口（NodePort）暴露服务。`NodePort` 服务会路由到 `ClusterIP` 服务，该 `ClusterIP` 服务会自动创建。通过请求 `<NodeIP>:<NodePort>`，可从集群的外部访问该 `NodePort` 服务。

![](http://image.leeyom.top/blog/20210723180336.png)

假设现在有一个集群，集群内有四个节点，这个四个节点对外的节点ip分别是：`10.21.2.10、10.21.2.11、10.21.2.12、10.21.2.13`。假设现在为某个工作负载pod 创建了service，设置主机端口为30003，那这个时候，我们可以通过任意一个节点ip+主机端口号，就可以访问该pod上的服务，比如：10.21.2.10:30003、10.21.2.11:30003 都可以访问。这种的使用场景，比如说某个pod上的服务是属于网关类型的，需要将ip+端口号配置到nginx上进行反向代理，则可以考虑使用这种方式。

## **LoadBalancer** 

也叫负载均衡器，可以向公网或者内网暴露服务。负载均衡器可以路由到 `NodePort` 服务，或直接转发到处于 VPC-CNI 网络条件下的容器中。这种类型的使用场景，比如内网需要和公网打通的情况下，即可通过内网ip直接访问到公网后端的pod。创建完成后的服务在集群外可通过**负载均衡域名或 IP + 服务端口** 访问服务，集群内可通过**服务名 + 服务端口** 访问服务。

![](http://image.leeyom.top/blog/20210723182111.png)

腾讯云上内网和公网的打通是通过构建子网的方式，对应pod的service创建后，会生成一个ipv4地址，在内网直接ping该ipv4地址，是可以ping通的。LoadBalancer 就感觉有点像是 ClusterIP 和NodePort的超集，用这张图可以理解下：

![](http://image.leeyom.top/blog/20210723184516.png)


