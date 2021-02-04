# [为Git和Maven设置代理加速](https://github.com/superleeyom/blog/issues/20)

## Git
由于 `GFW` 的缘故，有时候要去 `Github` 上克隆代码，半天 `git clone` 不下来，改过 `host`，设置过代理镜像，发现根本不管用，最后整来整去，花钱买个好点的梯子，设置好 `Git` 代理，要省不少事情。

### 全局代理

为 `Git` 设置全局代理（前提你已经买了比较好的梯子），根据代理协议的不同，在终端执行如下命令：

```sh
# 代理协议是socket5，我这里监听端口是1086，实际改成你自己的监听端口
git config --global http.proxy socks5://127.0.0.1:1086
git config --global https.proxy socks5://127.0.0.1:1086
# 代理协议是http，用这个，实际改成你自己的监听端口
git config --global http.proxy http://127.0.0.1:1080
git config --global https.proxy https://127.0.0.1:1080
```

在哪里可以查看梯子的代理协议？比如我用的是 [ClashX](https://github.com/yichengchen/clashX)，截图如下：

![](https://raw.githubusercontent.com/superleeyom/blog/main/img/20210203160705.png)

如果是 [Shadowsocks](https://github.com/paradiseduo/ShadowsocksX-NG-R8) 截图如下：

![](https://raw.githubusercontent.com/superleeyom/blog/main/img/20210203161326.png)

### 部分代理

我们大部分情况下，由于 `GFW` 的缘故，只需要对 `Github` 设置代理，国内的比如 `Gitee` 其实没有必要走代理，推荐这样设置，只针对 `Github` 设置部分代理：

```shell
# 代理协议是socket5（推荐）
git config --global http.https://github.com.proxy socks5://127.0.0.1:1086
git config --global https.https://github.com.proxy socks5://127.0.0.1:1086
# 代理协议是http
git config --global http.https://github.com.proxy http://127.0.0.1:1080
git config --global https.https://github.com.proxy http://127.0.0.1:1080
```

### 取消代理

取消 `Git` 的全局/部分代理：

```shell
git config --global --unset http.proxy
git config --global --unset https.proxy
```

### 速度对比

没有设置代理前，平均 `6.00 KiB/s`：

```
$ git clone https://github.com/mybatis/mybatis-3.git
Cloning into 'mybatis-3'...
remote: Enumerating objects: 3, done.
remote: Counting objects: 100% (3/3), done.
remote: Compressing objects: 100% (3/3), done.
^Cceiving objects:   0% (86/352273), 44.00 KiB | 6.00 KiB/s
```

设置代理后，平均 `6.90 MiB/s`：

```
$ git clone https://github.com/mybatis/mybatis-3.git
Cloning into 'mybatis-3'...
remote: Enumerating objects: 3, done.
remote: Counting objects: 100% (3/3), done.
remote: Compressing objects: 100% (3/3), done.
remote: Total 352273 (delta 0), reused 0 (delta 0), pack-reused 352270
Receiving objects: 100% (352273/352273), 104.22 MiB | 6.90 MiB/s, done.
Resolving deltas: 100% (302817/302817), done.
```

没有对比就没有伤害，`fuck GFW！！！`

## Maven

`Maven` 也是跟 `Git` 一样，拉取中央仓库的依赖时候，由于 `GFW` 的缘故，不设置代理的情况下，半天依赖是拉取不下来，通过设置 `settings.xml` ，配置代理也可以解决依赖下载速度过慢的问题：

```xml
<proxies>
    <proxy>
        <id>ClashX</id>
        <active>true</active>
        <protocol>socks5</protocol>
        <host>127.0.0.1</host>
        <port>1086</port>
      	<!--不需要设置代理的ip或域名，多个用|分隔，比如公司自己搭建的maven私服镜像，阿里云镜像等-->
        <nonProxyHosts>172.16.xx.xx|maven.aliyun.com</nonProxyHosts>
    </proxy>
</proxies>
```

设置完毕后，依赖下载丝滑流畅😂，更加具体配置的可以参考 `Maven` 官方配置文档：[Configuring a proxy](https://maven.apache.org/guides/mini/guide-proxies.html)，`fuck GFW！！！`


