# [Postman如何配置动态端口和IP](https://github.com/superleeyom/blog/issues/56)

## 背景

起因是每次使用 Postman 调试服务接口的时候，如果服务一旦被重启，对应服务的ip和端口就会改变，就需要重新配置服务的ip和端口，非常的繁琐以及麻烦。所以就针对这个问题，做了一点研究，简单的记录下。

## 步骤

### 1、维护多套环境及相应的环境变量

实际开发中，我们一般会有多套环境，比如：开发环境dev、测试环境test、生产环境prod等等。每个环境，我们配置好对应的consul（注册中心）环境变量、对应服务名环境变量，如图所示：


![image.png](https://cdn.jsdelivr.net/gh/superleeyom/blog/images/1702553954147.png)

### 2、维护collection目录层级以及脚本

建议以服务名为目录，在对应的目录层级，维护如下的脚本，动态的获取注册中心上对应的指定服务的ip和端口：
```js
pm.sendRequest(pm.environment.get("consul_service") + "trade-assets-service",
function(err, res) {
    if (err) {
        console.log(err);
    } else {
        pm.environment.set("trade-assets-service", res.json()[0].ServiceAddress + ":" + res.json()[0].ServicePort);
    }
});
```

![image.png](https://cdn.jsdelivr.net/gh/superleeyom/blog/images/1702554291804.png)
注： "trade-assets-service" 根据自己目录名变化

### 3、在对应的collection目录模拟request请求

维护好了动态获取脚本后，就可以正常的模拟对应的request请求，请求里面的ip和端口只需要填充对应的服务的占位符即可：

![image.png](https://cdn.jsdelivr.net/gh/superleeyom/blog/images/1702554459873.png)