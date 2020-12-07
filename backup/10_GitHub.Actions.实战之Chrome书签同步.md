# [GitHub Actions 实战之Chrome书签同步](https://github.com/superleeyom/blog/issues/10)

之前对 `GitHub Actions` 不是特别熟悉，以为它适合于跑类似于脚本语言 `Python`，不太适合与 `Java` 这类需要借助于 JVM 的语言，恰好最近有一个简单的想法就是想把 `Chrome` 书签同步到 `Github`，并将书签生成 `README.md` 文件，就尝试下用 `GitHub Actions` 去构建 `Java`，实际验证了其实是可行的，`GitHub Actions` 完全可以跑 `Java`做一些自动化操作。

## 什么是 GitHub Actions

官网的定义就是：

> 在 GitHub Actions 的仓库中自动化、自定义和执行软件开发工作流程。 您可以发现、创建和共享操作以执行您喜欢的任何作业（包括 CI/CD），并将操作合并到完全自定义的工作流程中。

做 Java 的其实都知道 `Jenkins`，其实就是和 `Jenkins`差不多，用于自动化构建的，只不过 `GitHub Actions`基于 Github 平台。

你只要在你的仓库下，创建`.github/workflow`目录，并在此目录下创建`*.yml`的文件，就可以开启 `GitHub Actions`，`yml` 文件主要用于配置自动化构建，这里我就拿我的这次实践的`chrome_bookmarks_sync.yml`示例：

```yml
# 此 action 的名字
name: ChromeBookmarksSyncApplication

on:
  # 开启手动执行
  workflow_dispatch:
  # 触发条件，当有代码push到master分支的时候，就触发一次构建
  push:
    branches: [ master ]
  # 触发条件，当有pr发起的时候，就触发一次构建  
  pull_request:
    branches: [ master ]

# 自定义的环境变量，实际需要换成你自己的
env:
  GITHUB_NAME: superleeyom
  GITHUB_EMAIL: 635709492@qq.com

# 任务
jobs:
  build:
    # 设置系统环境
    runs-on: ubuntu-latest
    steps:
    # 检出代码
    - uses: actions/checkout@v2
    # 设置jdk版本号
    - name: Set up JDK 1.8
      uses: actions/setup-java@v1
      with:
        java-version: 1.8

    # 执行maven命令，进行编译，并执行脚本，生成 README.md
    - name: execute application
      run: mvn -B clean compile exec:java --file pom.xml

    # 提交代码
    - name: update README.md
      uses: github-actions-x/commit@v2.6
      with:
        github-token: ${{ secrets.G_TOKEN }}
        commit-message: ":memo: update README.md"
        files: README.md
        rebase: 'true'
        name: ${{ env.GITHUB_NAME }}
        email: ${{ env.GITHUB_EMAIL }}
```

更多的 `GitHub Actions`用例，可以参考官方的[文档](https://docs.github.com/cn/free-pro-team@latest/actions/guides/building-and-testing-java-with-maven)。

## 实现思路

其实思路很简单，首先使用 Chrome 插件「[书签同步](https://chrome.google.com/webstore/detail/%E4%B9%A6%E7%AD%BE%E5%90%8C%E6%AD%A5/fbcbemgibdnpboehnfcnkegefaomnlbk)」，将书签信息（`bookmark.json`）上传到 Github 仓库，然后通过 `github action` 去读取书签数据，然后生成` README.md` 文件。

没法科学上传的前提下，可以通过[CrxDL.COM](https://crxdl.com/)去下载该插件，关键字搜索「书签同步」进行下载安装，设置流程的话，参考插件使用指南：

- 登录Github，在 `Settings->Personal access tokens->Generate new token` 生成一个访问 token

- 生成的 token 需要勾选 repo 权限，保存生成的 token

- 点击插件 icon，依次输入用户名、凭据、仓库名、文件存放路径（在仓库提前创建好`*.json`文件）

- 如果需要记住用户数据，需要打开 `Remember Me` 开关

- 填写完用户数据后，便可以进行「上传」或「下载」操作

## 自动化构建


由于项目是用 `Maven` 构建的，所以我当时的想法是通过用 `mvn clean package` 命令，写个单元测试方法，去触发并执行 Java 类方法，后面经过试验发现是可行的，但是觉得此方法比较 `low` 啊，应该是还有其他方法的，后面经过查询资料，其实 `Maven` 是可以通过插件 `exec-maven-plugin`，运行 Java main 方法：

```xml
<plugin>
    <groupId>org.codehaus.mojo</groupId>
    <artifactId>exec-maven-plugin</artifactId>
    <version>1.2.1</version>
    <configuration>
      	<!-- 指定main方法入口 -->
        <mainClass>com.bookmark.action.ChromeBookmarksSyncApplication</mainClass>
    </configuration>
</plugin>
```

对应的本地测试命令：`mvn clean compile exec:java`，实际的 `github action` 的 yml 文件里的写法有点区别：`mvn -B clean compile exec:java --file pom.xml`，需要指定 pom 文件。另外如果你想执行 `mvn` 命令的时候传递命令参数到 main 方法，可以这样：`mvn clean compile exec:java -Dexec.args="arg0 arg1 arg2"`，这样在就可以接收到自定义参数了：

```java
public class ChromeBookmarksSyncApplication {
    public static void main(String[] args) {
      	// 打印：[arg0 arg1 arg2]
      	System.out.println("打印接收到的参数："+JSONUtil.toJsonStr(args));
        GenerateReadmeUtil.generateReadme();
        System.exit(0);
    }
}
```

这样是不是我们可以在 `yml` 配置中自定义的参数，就可以通过 `mvn` 命令传递进来呢？对吧？

## 文件路径问题

关于文件读取和写入的路径问题，实际我们在**本地测试**的时候，对于 `bookmark.json`和`README.md`应该取绝对路径，在`GenerateReadmeUtil.java`类中：

```java
private static final String BOOKMARK_JSON_PATH = "/Users/leeyom/workspace/github/chrome-bookmarks-sync/bookmark.json";
private static final String README_PATH = "/Users/leeyom/workspace/github/chrome-bookmarks-sync/README.md";
```

但是实际在 `github action` 中，取的是相对地址，如果取绝对地址，会报文件找不到的问题：

```java
private static final String BOOKMARK_JSON_PATH = "bookmark.json";
private static final String README_PATH = "README.md";
```

## 如何使用

1. fork 仓库 [chrome-bookmarks-sync](https://github.com/superleeyom/chrome-bookmark-sync)仓库

2. 修改`chrome_bookmarks_sync.yml`文件的环境变量：

   ```yml
   env:
     GITHUB_NAME: 改成你自己的github用户名
     GITHUB_EMAIL: 改成你自己的github邮箱
   ```

   设置 `G_TOKEN`常量，复制你创建的 `github token`，在该仓库下：`Settings-->Secrets-->New repository secret`，将此常量填入进去，变量名设置为`G_TOKEN`即可。

3. 安装 `Chrome` 插件「[书签同步](https://chrome.google.com/webstore/detail/%E4%B9%A6%E7%AD%BE%E5%90%8C%E6%AD%A5/fbcbemgibdnpboehnfcnkegefaomnlbk)」，依次输入用户名、凭据、仓库名、文件存放路径
4. 填写完用户数据后，便可以进行「上传」或「下载」操作，然后借助 `github action`，就可以自动生成 `README.md`

## 参考文档

- [使用Maven运行Java main的3种方式](https://blog.csdn.net/qbg19881206/article/details/19850857)
- [使用 Maven 构建和测试 Java](https://docs.github.com/cn/free-pro-team@latest/actions/guides/building-and-testing-java-with-maven)
- [Chrome 书签同步到GitHub](https://www.cnblogs.com/gongkiro/p/13221739.html)
- [Java-Markdown-Generator](https://github.com/Steppschuh/Java-Markdown-Generator)