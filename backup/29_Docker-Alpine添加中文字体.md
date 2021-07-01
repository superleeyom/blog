# [Docker-Alpine添加中文字体](https://github.com/superleeyom/blog/issues/29)

1. 首先提前将需要安装的字体拷贝到 Jenkins 所在的机器上（`/media/front/`目录下）

   ```shell
   cd /media/front/
   ls
   simhei.ttf  simsun.ttc
   ```

2. 修改 Jenkins 的自动化配置，这里只展示核心的部分 shell 脚本片段：

   ```shell
   # 进入项目编译后的target目录
   cd /home/jenkins/data/soft/model/${MODEL_NAME}${BUILD_ID}/${MODEL_NAME}/target
   # 创建临时目录，并拷贝字体到临时目录
   mkdir front
   cp -r /media/front/* front/
   ...
   ...
   # 安装字体
   RUN apk add --update ttf-dejavu fontconfig \
       && rm -rf /var/cache/apk/* \
   WORKDIR /usr/share/fonts/
   COPY front/* /usr/share/fonts/
   WORKDIR /
   ```

   解析下 shell 脚本，其中安装字体那块，是构建 Docker 镜像的部分 Dockerfile 命令，下面解析这几句命令：

   ```dockerfile
   RUN apk add --update ttf-dejavu fontconfig \
       && rm -rf /var/cache/apk/* \
   ```

   因为我们使用的基础镜像是`FROM retail-harbor.aqara.com/retail/apline-jdk-iptables:v0.0.1`，基于Linux 发行版`Alpine`，所以安装软件的指令是 `apk`，类似于 CentOS 的 `yum`，Ubuntu 的 `apt-get`。

   由于安装字体需要安装软件`fontconfig`，所以需要执行`apk add --update ttf-dejavu fontconfig`，为了减少镜像的大小，需要删除安装后的缓存，执行`rm -rf /var/cache/apk/*`，`fontconfig`安装完成后，会自动在`/usr/share/`下创建两个目录，分别是`fontconfig`和`fonts`目录，接下来要做的就是把物理机的字体，拷贝到镜像的`fronts`目录中去。

   > 为了保持 `Dockerfile` 文件的可读性，可理解性，以及可维护性，建议将长的或复杂的 `RUN` 指令用反斜杠 `\` 分割成多行，参考[文档](https://vuepress.mirror.docker-practice.com/appendix/best_practices/#run)。

   踩了一个坑就是，始终无法将本地的字体文件拷贝到镜像中去，镜像的定制实际上就是定制每一层所添加的配置、文件，每一个 `RUN` 的行为都会建立一层新的镜像，所以如果我没有指定工作目录 `WORKDIR`的话，实际拷贝的时候，是找不到 `/usr/share/fonts/`这个路径。

   >使用 `WORKDIR` 指令可以来指定工作目录（或者称为当前目录），以后各层的当前目录就被改为指定的目录，如该目录不存在，`WORKDIR` 会帮你建立目录，更多有关`WORKDIR` 命令，参考[文档](https://vuepress.mirror.docker-practice.com/image/dockerfile/workdir/)。

   ```dockerfile
   WORKDIR /usr/share/fonts/
   COPY front/* /usr/share/fonts/
   # 拷贝完字体后，将工作目录切回根目录，因为接下来是要执行根目录下shell脚本entrypoint.sh
   WORKDIR /
   USER root
   ENTRYPOINT ["sh","entrypoint.sh" ]
   ```

   这里需要注意，`COPY` 这类指令中的源文件的路径都是相对路径，比如`COPY front/* /usr/share/fonts/`，这个 `front`目录就是相对路径，因为我们此时上下文路径就是**项目编译后的target目录**：

   ```shell
   # 进入项目编译后的target目录
   cd /home/jenkins/data/soft/model/${MODEL_NAME}${BUILD_ID}/${MODEL_NAME}/target
   ```
