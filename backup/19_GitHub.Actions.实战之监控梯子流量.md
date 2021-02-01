# [GitHub Actions 实战之监控梯子流量](https://github.com/superleeyom/blog/issues/19)

![](https://raw.githubusercontent.com/superleeyom/blog/main/img/20210131124723.png)

## 起因

最近也开通了 Netflix，Netflix 其实挺费流量的，为了防止梯子的流量超标，所以打算借助 Github Actions + telegram 做一个简单的监控，整体的思路其实很简单，没啥太大的难度，就是模拟梯子服务网站的登录，然后爬取页面的流量汇总数据，然后每天 9:30 将流量的使用情况发送到 telegram，同时如果可使用的流量少于 20% 的时候，推送报警到 telegram，代码目前放到了 github 上 [proxy-traffic-monitor](https://github.com/superleeyom/proxy-traffic-monitor)，实现细节就不讲了，代码比较简单，直接看代码就行。

## 开发环境

- springboot 2.0+
- jdk 1.8+

## 准备工作

1. 创建一个 telegram bot 🤖，如果不会创建的话，参见 telegram 的官方文档：[Creating a new bot](https://core.telegram.org/bots#6-botfather)，或者直接谷歌搜下，一大堆的教程，保存 `telegram bot` 的 `token`，这个很重要。

2. 创建好机器人🤖后，接下来就是要获取聊天id，也就是 `chatId`

    - 打开你创建的机器人，随便发点啥，比如发个：`hello world`

    - 浏览器输入：`https://api.telegram.org/bot(这里加上你的token)/getUpdates`，会返回如下示例：

      ```json
      {
        "ok": true,
        "result": {
          "message_id": 3,
          "from": {
            "id": 1432925625,
            "is_bot": true,
            "first_name": "SuperLeeyom",
            "username": "SuperLeeyomBot"
          },
          "chat": {
            "id": 599877436,
            "first_name": "Leeyom",
            "username": "super_leeyom",
            "type": "private"
          },
          "date": 1612000615,
          "text": "这是一条神奇的消息~"
        }
      }
      ```

      取到 chat 下面的 id ，这个就是聊天 id 了，比如我这里的就是 `599877436`。

    - 然后打开浏览器，输入：`https://api.telegram.org/bot(这里加上你的token)/sendMessage?chat_id=(你的chatId)&text=这是一条神奇的消息~`，不出意外你应该能收到一条消息，注意一定要是代理情况下你才能收到，毕竟 telegram 在国内无法使用的。

3. 准备`MonoCloud`和`ByWave`这两家的代理的账号和密码，目前我使用时这两家的服务，还行吧，价格比较贵，但是比较稳定吧。

## 如何使用

- fork 项目[proxy-traffic-monitor](https://github.com/superleeyom/proxy-traffic-monitor)

  - 在项目的`Settings-Secrets`选项下，点击`New repository secret`，创建我们准备工作的几个工作常量，如果只用其中一家，另外一家的可以账号密码可设置为空：
     - `BY_WAVE_USER_NAME`：bywave 账号
     - `BY_WAVE_PASSWORD`：bywave 密码
     - `MONO_CLOUD_USER_NAME`：monoCloud 账号
     - `MONO_CLOUD_PASSWORD`：monoCloud 密码
     - `TG_CHAT_ID`：telegram 聊天 id
     - `TG_TOKEN`：telegram bot token

- 目前有两个定时，分别是`daily.yml`和`warn.yml`，前者是每天 9:30 点执行一次，汇总流量使用情况发送到 telegram，后者是每隔 2 个小时执行一次，监控可用流量的是否已经少于 20%，若少于 20% 会推送到telegram 进行预警，若要调整时间，可以修改这两个 yml 的 `cron` 表达式。

  - 我这里默认关闭`warn.yml`这个自动化任务了，因为我发现，ByWave 好像已经对对 github actions 的 ip做限制了，可能我测试的太频繁了吧😂，自己有需要的再打开这个注释吧

     ```yml
     on:
       workflow_dispatch:
     #  schedule:
     #    - cron: "0 */2 * * *"
     ```

  - ByWave 有防爬虫机制，所以定时任务太频繁，有可能会被限制 ip 地址，导致 github actions 自动化执行的时候，无法登录，如果被限制了，可以通过更换代理 ip 的方式：

     ```java
     Proxy proxy = new Proxy(Proxy.Type.HTTP, new InetSocketAddress("xxx.xxx.xxx.xxx", 80));
     loginRequest.setProxy(proxy);
     ```

- 如果喜欢，就点个 star 吧，以上就是这些了！Enjoy!

## 声明

本源码只用于学习和交流，禁止用于商业目的。