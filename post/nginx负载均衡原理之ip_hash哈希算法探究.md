关于 `ip_hash` `nginx` 官网是这样定义的：

> Specifies that a group should use a load balancing method where requests are distributed between servers based on client IP addresses. The first three octets of the client IPv4 address, or the entire IPv6 address, are used as a hashing key. The method ensures that requests from the same client will always be passed to the same server except when this server is unavailable. In the latter case client requests will be passed to another server. Most probably, it will always be the same server as well.

翻译过来就是：

> 指定组应使用负载平衡方法，其中根据客户端IP地址在服务器之间分配请求。 客户端IPv4地址的前三个八位位组或整个IPv6地址用作哈希密钥。 该方法确保了来自同一客户端的请求将始终传递到同一服务器，除非该服务器不可用。 在后一种情况下，客户端请求将传递到另一台服务器。 最有可能的是，它也将永远是同一台服务器。

假设目前有三台服务器，采用 nginx 的`ip_hash`负载均衡策略，假设现在有三台 Tomcat 服务器，其对应的节点 index 分别是：0、1、2，此时有四个客户端访问 nginx，那根据哈希算法：`hash(ip)%node_counts = index`，最终得到的各个客户端的请求会落到如下的机器上（假设四个客户端ip的哈希值分别为：5、6、7、8）：

- `ip`：指的是客户端的 ip 地址的前三个八位位组，打个比方：`138.23.324.13`，那就是取`138.23.324`，所以如果同一个局域网内访问 nginx 的时候，如果机器的前三个八位一致，比如这两个ip：`138.23.324.13`、`138.23.324.14`的请求最终只会落在同一台的节点上
- `node_counts`：节点数量
- `index`：节点的标识

![](https://raw.githubusercontent.com/superleeyom/blog/main/img/hash.jpg)

但是使用哈希算法会存在一些问题，比如要删除一个节点3，这时候用户的请求落地情况会变成这样：

![](https://raw.githubusercontent.com/superleeyom/blog/main/img/hash2.jpg)

原本用户4是访问的节点3，这时候就会转为访问节点1，这时候在之前节点3上的用户会话就会丢失，增加一个节点也是同理，同样会存在用户会话丢失的情况。如何正确让一台服务器下线？那在 nginx 官网的文档中写道：如果需要临时删除其中一个服务器，则应该使用 down 参数标记它，以便保存当前客户机 IP 地址的散列。

> If one of the servers needs to be temporarily removed, it should be marked with the `down` parameter in order to preserve the current hashing of client IP addresses.

示例：

```nginx
upstream backend {
    ip_hash;

    server backend1.example.com;
    server backend2.example.com;
    server backend3.example.com down;
    server backend4.example.com;
}
```

如果采用一致性哈希算法，出现以上问题的概率就会低很多。

![](https://raw.githubusercontent.com/superleeyom/blog/main/img/iShot2020-11-05%E4%B8%8B%E5%8D%8812.22.28.png)

如上图，圆环上有 `0-2^32-1` 个节点，每个节点，按顺时针方向排列递增，用户的请求 ip，通过哈希算法，会落在圆环上的某个节点上。按顺时针方向，用户1、用户2会访问节点1，用户3、用户4会访问节点2，用户5、用户6会访问节点3，用户7访问到节点4。假如此时删除了节点3，那么原本的用户5和用户6的请求，则会落到节点4上，其他用户的访问均不会受到影响，只会有用户5和用户6的会话信息会丢失，不会造成全局的变动。

![](https://raw.githubusercontent.com/superleeyom/blog/main/img/iShot2020-11-05%E4%B8%8B%E5%8D%8802.05.03.png)

另外还有一个优点，如果发现节点1访问量很大，负载高于其他节点，这就说明节点1存储的数据是热点数据。这时候，为了减少节点1的负载，我们可以在热点数据位置再加入一个node，用来分担热点数据的压力。