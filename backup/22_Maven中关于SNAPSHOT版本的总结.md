# [Maven中关于SNAPSHOT版本的总结](https://github.com/superleeyom/blog/issues/22)

## Maven中的SNAPSHOT版本

假设有两个小组负责维护两个组件，`example-service` 和 `example-ui`，这两个组件不在同一个代码仓库，`example-service` 的版本号信息：

```xml
<artifactId>example-service</artifactId>
	<version>1.0</version>
<packaging>jar</packaging>
```

其中 `example-ui` 项目依赖于 `example-service`：

```xml
<dependency>
	<groupId>com.xxx.yyy</groupId>
	<artifactId>example-service</artifactId>
	<version>1.0</version>
</dependency>
```

而这两个项目每天都会构建多次，我们知道，**maven 的依赖管理是基于版本管理的，对于发布状态的 artifact，如果版本号相同，即使我们内部的镜像服务器上的组件比本地新，maven 也不会主动下载的。** 假如 `example-service` 增加了一些新的功能，这时候就得升级 `example-service` 的版本号，然后 deploy 到 maven 私服上去，由于升级了 `example-service` 的版本号为 1.1，example-ui 由于是依赖方，开发阶段，它想要使用`example-service`的新功能，则要跟着把 `example-service` 的版本号到 1.1，如果`example-service`更新的很频繁，每次构建你都要升级 `example-service` 的版本，效率就非常低。

那引入 `SNAPSHOT` 和 `RELEASE` 版本控制，这两种版本是分别在不同的 maven 仓库，前者是快照版本，用于开发环境，后者是稳定正式版本，用于生产环境，那在开发阶段，我们需要将 `example-service` 的版本号改为：

```xml
<artifactId>example-service</artifactId>
	<version>1.0-SNAPSHOT</version>
<packaging>jar</packaging>
```

在该模块的版本号后加上 `-SNAPSHOT `即可（注意这里必须是大写），然后 deploy 到私服，在 `maven-snapshots` 仓库下，`version` 列根据发布时间不同自动在 1.0 后面加上了当前时间，以此区别不同的快照版本：

![](https://raw.githubusercontent.com/superleeyom/blog/main/img/20210223170842.png)

`example-ui` 项目里，引入 `example-service` 快照版本：

```xml
<dependency>
	<groupId>com.xxx.yyy</groupId>
	<artifactId>example-service</artifactId>
	<version>1.0-SNAPSHOT</version>
</dependency>
```

这样的话，每次 `example-ui` 构建时，会优先去远程仓库中查看是否有最新的 `example-service-1.0-SNAPSHOT.jar`，不需要频繁的去修改`example-service` 的版本号。等到两个组件要正式上线，`example-service` 的版本号改为：

```xml
<artifactId>example-service</artifactId>
<version>1.1-RELEASE</version>
<packaging>jar</packaging>
```

然后 deploy 到私服，`example-ui` 项目里，引入 `example-service` 正式升级版本：

```xml
<dependency>
	<groupId>com.xxx.yyy</groupId>
	<artifactId>example-service</artifactId>
	<version>1.1-RELEASE</version>
</dependency>
```

所以总的来说，对于 Maven 版本号，我们最好这样约定：

1. 【强制】开发阶段版本号定义为 SNAPSHOT，发布后版本改为 RELEASE。
2. 【强制】线上应用不要依赖 SNAPSHOT 版本(安全包除外)；正式发布的类库必须先去中央仓库进行查证，使 RELEASE 版本号有延续性，版本号不允许覆盖升级。

## 参考资料

- [理解Maven中的SNAPSHOT版本和正式版本](http://www.huangbowen.net/blog/2016/01/29/understand-official-version-and-snapshot-version-in-maven/)
- [maven(15)，快照与发布，RELEASE与SNAPSHOT](https://blog.csdn.net/wangb_java/article/details/66000956)
- [MAVEN规约](https://caosg.gitbooks.io/java-devepment-rules/content/project/maven.html)

