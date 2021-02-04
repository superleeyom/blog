# [常用linux进程查询命令](https://github.com/superleeyom/blog/issues/15)

## ps 命令详解

[**ps命令详解**](https://wangchujiang.com/linux-command/c/ps.html)

## 根据进程名查询进程信息

```sh
ps  -ef | grep {processName}
```

## 根据进程pid查询进程信息

```sh
ps  -ef | grep {pid}
```

## 根据端口查看对应进程信息

### Linux

```shell
netstat -tunlp | grep {port}
```

示例：

```
# netstat -tunlp | grep 8080
tcp6       0      0 :::8080                 :::*                    LISTEN      29150/java
```

则 29150 为当前端口所对应的进程 pid

### MacOS

```sh
lsof -i tcp:{port}
```

## 查看进程pid占用端口情况

### Linux

```shell
netstat -nap | grep {pid}
```

### MacOS

```sh
lsof -p {pid}|grep LISTEN
```

## 查询僵尸进程

```shell
ps -A -ostat,ppid,pid,cmd | grep -e '^[Zz]'
```

- `-A` 参数列出所有进程
- `-o` 自定义输出字段 我们设定显示字段为 stat（状态）, ppid（进程父id）, pid(进程id)，cmd（命令）这四个参数
- 因为状态为 z 或者 Z 的进程为僵尸进程，所以我们使用 grep 抓取 stat 状态为 z 或者 Z 进程

## 查看最消耗CPU和内存的进程

```shell
# 查看最消耗CPU的进程
ps -eo pid,ppid,%mem,%cpu,cmd --sort=-%cpu | head
# 查看最消耗内存的进程
ps -eo pid,ppid,%mem,%cpu,cmd --sort=-%mem | head
```
