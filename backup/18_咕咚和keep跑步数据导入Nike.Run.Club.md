# [咕咚和keep跑步数据导入Nike Run Club](https://github.com/superleeyom/blog/issues/18)

起初是 [yihong](https://github.com/yihong0618) 在v站推广他的开源跑步项目 [running_page](https://github.com/yihong0618/running_page)，我那天在v站刷帖无无意看到了，就点进去了解了下，发现确实挺不错的项目，可以抓取各个平台的跑步数据，汇总聚合在一起，生成一个精美的跑步主页。后面通过 `twitter` 联系上了 yihong，yihong 是个非常热情，乐于助人的人，在他的帮助下，我成功了拿到了咕咚和 keep 上的跑步数据，并且在他的安利下，加上本身实在是受不了国内运动软件上各种广告，正式从 keep 换到了 `Nike Run Club`（后面简称 nrc）。

切换到 nrc 后，之前其实我有折腾过想把之前在咕咚和 keep 上的数据导入到 nrc，毕竟积累了好几千公里的跑量，放弃掉实在太可惜。后面通过 yihong 的提供的思路，可以尝试将咕咚、keep 的跑步数据导出 [gpx](https://zh.wikipedia.org/wiki/GPX)，然后再把 gpx 导入到类似
 `Garmin Connect` 等平台，然后在 nrc 上与佳明进行绑定，通过曲线救国，就可以将数据导入进 nrc。

> gpx 是一种 XML 格式，专门为应用软件设计的通用 GPS 数据格式，它可以用来描述路点、轨迹、路程，大部分的运动类软件都支持此类通用格式的导入。

早在一个月前，我尝试如下的的步骤：

1. 利用 [running_page](https://github.com/yihong0618/running_page) 项目，导出 gpx 数据
2. 创建一个国区 [garmin connect](https://connect.garmin.cn/) 的账号，将 gpx 数据一次性导入 Garmin Connect
3. 在 nrc 上关联 Garmin，然后数据就会自动同步过来

但是很遗憾并没有成功，后面我就没有在弄了。就在这两天，yihong 说他和另外一个网友，搞定了咕咚数据的抓取，所以又开始着手重新尝试。我仔细想了下，我当时的步骤是先创建 `Garmin Connect` 的账号，然后把 gpx 数据上传到佳明，最后再到 `nrc` 上关联 `Garmin`。是不是我的步骤不对？是不是 `Garmin` 是主动把数据推送给 `Nike` 的？所以在我没关联之前，就把数据上传了，没有触发推送？带着这些疑问，所以我又尝试了如下的步骤（最好全程都开启代理的情况下进行）：

1.  创建一个**国区** [garmin connect](https://connect.garmin.cn/) 的账号，非国区可能不太行，若已有账号不需要重复创建
2.  在 nrc 上关联 Garmin，出现如下的界面说明绑定成功：
    -  ![关联成功](https://raw.githubusercontent.com/superleeyom/blog/main/img/20210127153147.png)
    -  ![garmin](https://raw.githubusercontent.com/superleeyom/blog/main/img/telegram-cloud-photo-size-5-6089317861500758842-y.jpg)
3.  在 Garmin Connect 上传 gpx 数据
    - ![上传 gpx 数据](https://raw.githubusercontent.com/superleeyom/blog/main/img/telegram-cloud-photo-size-5-6089317861500758841-y.jpg)
    - ![上传 gpx 数据](https://raw.githubusercontent.com/superleeyom/blog/main/img/telegram-cloud-photo-size-5-6089317861500758843-y.jpg)
4.  打开 nrc，然后刷新数据，同步的时候可能会费点时间，如果刷新后总里程数增加了，那么恭喜你，同步成功，由于缓存的缘故，nrc 的总里程会显示不对，最好退出重新登录几次。
    - ![同步成功](https://raw.githubusercontent.com/superleeyom/blog/main/img/20210127155351.png)
    - ![同步成功](https://raw.githubusercontent.com/superleeyom/blog/main/img/20210127155423.png)

以上便是我整个同步过程的一些记录，如果导入后，没啥动静，建议在佳明那边删除掉已导入的 gpx 数据，在佳明那边解除 nike 绑定，然后再重新绑定，再重新导入。我觉得要想保证导入成功需要注意如下几点：
1. 确保 gpx 数据的准确性
2. 找个好的梯子，在全局代理环境下操作
3. 注意操作顺序，绑定一定要在导入 gpx 数据之前
4. 佳明账号选择国区：`connect.garmin.cn`

由于在通过 `running_page` 项目生成 keep 和咕咚的 gpx 数据的时候，由于 keep 数据不完整性，实际生成的 gpx 文件不是很完整，丢失了差不多 1000 公里的数据，但是也无所谓了，能拿到 80% 的数据我已经很开心了，哈哈。

最后贴下:
- 我的跑步主页：[https://running.leeyom.top/](https://running.leeyom.top/)
- 我的 `Nike Run Club` id：`635709492@qq.com`，欢迎互相关注鼓励

---

> 把用Strava跑步的记录成功导入了NRC！感谢

恭喜哇 @zill057 

---

> Keep 成功导入了NRC 👍🏻

Cool 

---

@AhianZhang 可以可以，已添加