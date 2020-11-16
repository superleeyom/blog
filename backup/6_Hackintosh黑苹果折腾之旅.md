# [Hackintosh黑苹果折腾之旅](https://github.com/superleeyom/blog/issues/6)

![](https://raw.githubusercontent.com/superleeyom/blog/main/img/iShot20201115.png)


## 硬件配置
其实我这台黑苹果，今年年初三月份的时候就装好了，周末趁着有空，把系统升级到了 `macOS Big Sur` ，在此总结下自己的整个的安装的一些心得。

我这台黑苹果主机的整体配置清单如下：

- `cpu`：intel i5 9400  散片 淘宝 1300元
- `主板`：华擎B365M-ITX/AC 淘宝 659元
- `显卡`：盈通 rx580 4g 2304sp 满血版 508元
- `硬盘`：海康威视 C2000 pro 256g SSD 京东 335 元 +  「自用剩余的闪迪」 SATA3 256g SSD 
- `内存条`：宇瞻 DDR4 2666 16g*2 天猫 978元
- `散热器`：ID-COOLING IS-40X 淘宝 89元
- `显卡延长线`：傻瓜超人 ADT01 淘宝 99元（方便后期加显卡）
- `电源`：海盗船 sf450 金牌  + 定制线 淘宝 728元
- `机箱`：傻瓜超人 K55 + 定制铝侧板两块  淘宝 405 元
- `无线网卡`：BCM94360CS2 无线网卡+转接卡  淘宝 160元
- `总计`：5261 元

由于我是第一次装机，一来就装 `ITX` 主机，各种懵逼，好在说明书也挺全的，从下午一直装到晚上凌晨三四点，终于顺利点亮。

## 组装初衷

那为啥要组装一台黑苹果呢？而不直接买白的呢？这个嘛，迫于入了苹果生态的坑，加上老笔记本 MacBook Pro (Retina, 13-inch, Early 2015) 性能已经逐渐跟不上了，所以就萌生了组台 itx 黑苹果主机，那说到底，其实就是「穷」。

黑苹果有优点也有缺点，优点是：
- **省钱呀**，性价比高，同样的配置，可能只要白苹果的1/3的价格
- 可扩展性强，可以自己随意diy硬件

缺点：
- 如果硬件选的不好，比较折腾，没有合适的EFI的话，需要自己去摸索
- 版本升级麻烦，每次大版本的升级的话，都需要重装
- 需要一定软硬件基础

装黑苹果，要想省事的话，去论坛，比如国内的：[远景论坛](http://bbs.pcbeta.com/)、[黑果小兵](https://blog.daliansky.net/)，国外的：[tonymacx86](https://www.tonymacx86.com/)，按照别人已经有装成功过的硬件，并且对应的EFI也都有，那就对着采购一套相同的配件，尽可能选择免驱的硬件，基本上不会出大的问题，比如我的这个网卡BCM94360CS2 就是原笔记本的拆机原件。当然，你前提得懂一些基本的硬件和软件知识，否则还是花点钱，直接远程交给某宝来装。

由于我自己装的这套配置，已经有成功的 [（B365ITX-Hackintosh-OC）](https://github.com/Good0007/B365ITX-Hackintosh-OC) 例子，只要按照原作者给的提示，把对应的该删的删了，整体的安装过程，基本上很顺畅。整体的安装流程，参考的是黑果大神「[黑果小兵](https://blog.daliansky.net/)」的教程「[天逸510s Mini兼macOS BigSur安装教程](https://blog.daliansky.net/Lenovo-Tianyi-510s-Mini-and-macOS-BigSur-Installation-Tutorial.html)」，镜像也是用的黑果小兵大神封装的「[macOS BigSur 11.0.1 20B29 正式版](https://blog.daliansky.net/macOS-BigSur-11.0.1-20B29-Release-version-with-Clover-5126-original-image-Double-EFI-Version-UEFI-and-MBR.html)」。

## 遇到的问题

目前主流的两到黑苹果引导方式：OpenCore（简称OC）和 Clover（简称四叶草），目前 Clover 逐渐被淘汰了，很多的驱动 Kext 都放弃适配 Clover，大家目前都开始使用 OC 做为黑苹果的首选引导方式。

在安装过程中没遇到大的问题，就是通过「时间机器」恢复备份的时候，遇到一个比较坑爹的事情，我顺利的进入系统后，我打开系统自带的「迁移助理」，想恢复原有的备份，但是每次恢复到一半的时候，老是自动关机，重试几次，都是一样，很让人崩溃。最后，我不得不再次抹盘重装，在刚刚进入系统初始化的时候，系统提示是否要导入已有的备份，我从这里开始进行恢复，不等彻底登录进入系统后，通过「迁移助理」进行恢复，嚯，好家伙，顺顺利利的恢复成功了，你说这奇怪不奇怪。

再个就是修改引导工具 OpenCore 的相关的配置的时候，不生效的问题。比如原作者的 EFI，启动的时候开启了啰嗦模式（`-v`），系统启动的时候，总会打印一大串的debug的代码，所以为了隐藏这个，得把 EFI 里 `config.plist` 的 `boot-args` 属性里的 `-v` 去掉即可，但是发现去掉后，重启依旧不生效，后面通过找资料，最后发现，需要用工具 `Hackinttools`，清除 `NVRAM `里这行配置的缓存（选中删除即可），否则不会生效。

另外启动的时候，不想显示引导菜单的话，将 `showpicker` 改成 `false`，其他的话，目前没有遇到啥问题，由于大部分原作者已经调试好了，基本上就不需要调整了，感谢！

## 完成情况

目前这台黑苹果的整体的完整度在99%吧，唯一的缺点就是，睡眠的话，需要手动去点击系统左上角的「睡眠」选项，系统无法自动的进入睡眠。我自己也使用了大半年了，整体上和苹果的台式机 iMac、Mac Pro 基本上无任何的差别，也能配合 iPad、iPhone、Apple Watch 进行隔空投送、接力、随航、解锁 Mac等等一系列的功能。在会自己折腾的情况下，还是挺香的。所以如果你有差不多相同的配置，可以试试我这个 EFI。

## 参考资料

- [B365ITX-Hackintosh-OC 华擎B365ITX 黑苹果OC 配置](https://github.com/Good0007/B365ITX-Hackintosh-OC)
- [天逸510s Mini兼macOS BigSur安装教程](https://blog.daliansky.net/Lenovo-Tianyi-510s-Mini-and-macOS-BigSur-Installation-Tutorial.html)
- [【黑果小兵】macOS BigSur 11.0.1 20B29 正式版 with Clover 5126原版镜像[双EFI版][UEFI and MBR]
](https://blog.daliansky.net/macOS-BigSur-11.0.1-20B29-Release-version-with-Clover-5126-original-image-Double-EFI-Version-UEFI-and-MBR.html)
- [华擎 Asrock B365M-ITX/ac macOS Catalina 完美黑苹果 OC/Clover双版本](https://www.chenweikang.top/?p=846)
- [黑苹果安装教程](https://zhih.me/hackintosh-install-guide/)
- [精解OpenCore](https://blog.daliansky.net/OpenCore-BootLoader.html)
- [使用 OpenCore 引导黑苹果](https://blog.xjn819.com/post/opencore-guide.html)

## 资源附件

- 我目前在用的这台机器的 [EFI](https://github.com/superleeyom/B365ITX-Hackintosh-OpenCore)
- 原作者的 [EFI](https://github.com/Good0007/B365ITX-Hackintosh-OC)
- [opencore-configurator](https://mackie100projects.altervista.org/download-opencore-configurator/)
- [Hackintool](https://github.com/headkaze/Hackintool/releases)

