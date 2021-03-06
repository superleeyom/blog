# [nginx基础指令及初始配置解析](https://github.com/superleeyom/blog/issues/4)

## nginx 常用命令

- `./nginx -s stop` ：强制停止nginx

- `./nginx -s quit`： 优雅停止nginx，即处理完所有请求后再停止服务

- `./nginx -t` ：检测配置文件是否有语法错误

- `./nginx  -v`： 查看nginx的版本号

- `./nginx -V` ：查看版本号和配置选项信息

- `./nginx -c`：设置配置文件（默认是：`/etc/nginx/nginx.conf`）

- `./nginx -s reload`: 重新加载配置文件

## nginx docker 相关指令

- 拉取 nginx 镜像：`docker pull nginx`
- 启动 nginx 容器实例：`docker run -itd --name nginx-demo -p 8080:80 nginx`
  - `-itd`：`-t` 选项让 Docker 分配一个伪终端（pseudo-tty）并绑定到容器的标准输入上， `-i` 则让容器的标准输入保持打开，`-d`是后台运行
  - `--name nginx-demo`：指定容器实例名称`nginx-demo`
  - `-p 8080:80`：将本机 8080 端口映射为容器的 80 端口
- 进入容器：`docker exec -it nginx-demo bash`
- 终止容器：`docker container stop nginx-demo`
- 删除容器：`docker container rm nginx-demo`
- 启动已终止的容器：`docker container start nginx-demo`
- 查询当前运行的容器：`docker container ls`
- 查询所有的容器：`docker container ls -a`
- 更多的docker指令见[《Docker — 从入门到实践》](https://vuepress.mirror.docker-practice.com)

## nginx 默认配置文件解析

```nginx
# 设置worker进程的用户，指的linux中的用户，会涉及到nginx操作目录或文件的一些权限
user  nginx;
# worker进程工作数设置，一般来说CPU有几个，就设置几个
worker_processes  1;

# 设置日志级别，debug | info | notice | warn | error | crit | alert | emerg，错误级别从左到右越来越大
error_log  /var/log/nginx/error.log warn;
# 设置nginx进程 pid
pid        /var/run/nginx.pid;

# 设置工作模式
events {
	# 每个worker允许连接的客户最大连接数
	worker_connections  1024;
}

# http 是指令块，针对http网络传输的一些指令配置
http {
	# include 引入外部配置，提高可读性，避免单个配置文件过大
	include /etc/nginx/mime.types;
	# 设置HTTP默认的 content-type
	default_type  application/octet-stream;
	# 设置日志格式，各项含义如下：
	# $remote_addr：客户端ip
	# $remote_user：远程客户端用户名，一般为：’-’
	# $time_local：时间和时区
	# $request：请求的url以及method
	# $status：响应状态码
	# $body_bytes_send：响应客户端内容字节数
	# $http_referer：记录用户从哪个链接跳转过来的
	# $http_user_agent：用户所使用的代理，一般来时都是浏览器
	# $http_x_forwarded_for：通过代理服务器来记录客户端的ip
	log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

	access_log  /var/log/nginx/access.log  main;

	# sendfile 使用高效的文件传输，提升传输性能，启用后才能使用tcp_nopush，指当数据表累积到一定的大小后才发送，提高效率
	sendfile        on;
	#tcp_nopush     on;
		
	# 设置客户端与服务端请求的超时时间，保证客户端多次请求的时候不会重复建立新的连接，节约资源损耗
	keepalive_timeout  65;
		
	# 开启gzip压缩功能，提高传输效率，节约带宽
	#gzip  on;
		
	# include 引入外部配置，提高可读性，避免单个配置文件过大
	include /etc/nginx/conf.d/*.conf;
}
```



## root 与 alias

假如服务器路径为：`/home/leeyom/files/img/header.png`

- root 路径完全匹配访问：

  ```nginx
  location /leeyom { 
    root /home 
  }
  ```

  用户访问的请求为：`url:port/leeyom/files/img/header.png`

- alias 可以为你的路径做一个别名，对用户透明：

  ```nginx
  location /hello { 
    alias /home/leeyom
  }
  ```

  用户访问的请求为：`url:port/hello/files/img/header.png`，相当于给 `leeyom` 目录做一个别名。

## location 的匹配规则

- `空格`：默认匹配，普通匹配

  ```nginx
  location / { 
    root /home 
  }
  ```

  用户可以访问 `home` 目录下的所有文件。

- `=`：精确匹配

  ```nginx
  location = /leeyom/files/img/header.png { 
    root /home; 
  }
  ```

  用户只能访问此路径`/home/leeyom/files/img/header.png`下的`header.png`图片。

- `~*`：匹配正则表达式，不区分大小写

  ```nginx
  location ~* \.(GIF|jpg|png|jpeg|gif) { 
    root /home; 
  }
  ```

  用户可以访问 `home` 目录下的只要后缀为`GIF|jpg|png|jpeg|gif`的文件，由于不区分大小写，如果访问的是 `header.GIF`图片，会重定向访问`header.gif`图片。

- `~`：匹配正则表达式，区分大小写

  ```nginx
  location ~ \.(GIF|jpg|png|jpeg|gif) { 
    root /home; 
  }
  ```

  用户可以访问 `home` 目录下的只要后缀为`GIF|jpg|png|jpeg|gif`的文件。

- `^~`：以某个字符路径开头请求

  ```nginx
  location = ^~ /leeyom/files/img { 
    root /home; 
  }
  ```

  用户只能访问此路径`/home/leeyom/files/img/`下的文件。

## nginx 跨域配置

在 `server` 块里面增加：

```nginx
# 允许跨域请求的域，*代表允许所有的域
add_header 'Access-Control-Allow-Origin' *;
# 允许带上cookie请求
add_header 'Access-Control-Allow-Credentials' 'true';
# 允许请求的header，比如：Authorization,Content-Type,Accept,Origin,User-Agent 等
add_header 'Access-Control-Allow-Headers' *;
# 允许请求的方法，比如：GET、POST、PUT、DELETE
add_header 'Access-Control-Allow-Methods' *;
```

## nginx 防盗链

```nginx
# 对源站点进行验证（白名单），多个域名用空格隔开
valid_referers *.leeyom.com;
# 非法访问则返回403
if($invalid_referer){
	return 403;  
}
```

## nginx 搭建 Tomcat 集群简版配置

```nginx
upstream tomcats {
  server 192.168.1.174:8080;
  server 192.168.1.175:8080;
  server 192.168.1.176:8080;
}
server {
  listen 80;
  server_name www.tomcats.com;
  location / {
    proxy_pass: http://tomcats;
  }
}
```

访问`www.tomcats.com`，将以轮询方式，分别访问三台 Tomcat，当然也可以使用加权轮询，例如：

```nginx
server 192.168.1.174:8080 weight=1;
server 192.168.1.175:8080 weight=2;
server 192.168.1.176:8080 weight=5;
```

`weight`的值越大，当前服务器的 Tomcat 被访问的几率越大。

## upstream 指令

```nginx
server 192.168.1.174:8080 max_conns=2;
server 192.168.1.175:8080 max_conns=2;
server 192.168.1.176:8080 max_conns=2;
```

- `max_conns`：限制每台server的连接数，用于保护避免过载，可起到限流作用；

```nginx
server 192.168.1.174:8080 weight=1;
server 192.168.1.175:8080 weight=2;
server 192.168.1.176:8080 weight=5 slow_start=60s;
```

- `slow_start`：缓慢启动，`weight`逐渐增大，使某台服务器慢慢加入集群，方便该服务器完成一些前置化的操作，该指令需要注意：
  - 只能在商业版中使用；
  - 该参数不能使用在`hash`和`random load balancing`中；
  - 如果upstream中只有一台 server，则该参数无效；
- `down`：标记服务节点不可用
- `backup`：表示当前服务器节点是备用机， 只有在其他的服务器都宕机以后， 自己才会加入到集群中， 被用户访问到
  - `backup`参数不能使用在`hash`和`random load balancing`中；
- `max_fails`：表示失败几次，则标记 server 已宕机，踢出服务，默认值为1
- `fail_timeout`：表示失败的重试时间，默认值 10s
  - 示例：`max_fails=2 fail_timeout=15s `：15 秒内，请求某一 server 失败达 2 次后，则认为此 server 已经宕机，随后再过 15 秒，这 15 秒内不会有新的请求到达刚宕机的节点，会请求到正常的运行的 server，15秒后会有新请求再次请求挂掉的 server，如果还是失败，重复之前的操作；

## Keepalived 提高吞吐量

```nginx
upstream tomcats {
  server 192.168.1.174:8080;
  server 192.168.1.175:8080;
  server 192.168.1.176:8080;
  # 设置长连接处理的数量
  keepalive 32;
}
server {
  listen 80;
  server_name www.tomcats.com;
  location / {
    proxy_pass: http://tomcats;
    # 设置长连接http的版本号
    proxy_http_version 1.1;
    # 清除 connection header 信息
    proxy_set_header Connection "";
  }
}
```

## nginx的反向代理缓存

```nginx
# proxy_cache_path 设置缓存目录
# keys_zone 设置共享内存以及占用空间大小
# max_size 设置缓存大小
# inactive 超过此时间则被清理
# use_temp_path 临时目录，使用后会影响nginx性能
proxy_cache_path /usr/local/nginx/upstream_cache keys_zone=mycache:5m max_size=1g inactive=1m use_temp_path=off;
```

```nginx
location / {
  proxy_pass http://tomcats;
  # 启用缓存，和keys_zone一致
  proxy_cache mycache;
  # 针对200和304状态码缓存时间为8小时
  proxy_cache_valid 200 304 8h;
}
```

## 配置ssl证书

1. 安装 `ssl` 模块

2. 将 ssl 证书`*.crt`和私钥`*.key`拷贝到`/usr/local/nginx/conf`目录中

3. 新增 server 监控 443 端口：

   ```nginx
   server{
     listen 443;
     server_name www.leeyom.me;
     # 开启ssl
     ssl on;
     # 配置ssl证书
     ssl_certificate yourdomain.com.crt;
     # 配置证书秘钥
     ssl_certificate_key yourdomain.com.key;
     # ssl会话cache
     ssl_session_cache shared:SSL:1m;
     # ssl会话超时时间
     ssl_session_timeout 5m;
     # 配置加密套件，写法遵循 openssl 标准
     ssl_protocols TLSv1 TLSv1.1 TLSv1.2; ssl_ciphers ECDHE-RSA-AES128-G
   }
   ```