# [关于Redis缓存穿透、缓存雪崩、缓存击穿问题探讨](https://github.com/superleeyom/blog/issues/13)

## 缓存穿透

拿一个不存在的 key 去查询数据，如果缓存里面查询不到，就会去数据库里面查询，如果有人恶意拿不存在的 key 疯狂请求，会把数据库压垮，这就是缓存穿透，下面用一段伪代码：

```java
List<String> cacheList = redis.get(key);
if(CollUtil.isEmpty(cacheList)){
	List<String> list = mysql.getList(key);
	if(CollUtil.isNotEmpty(list)){
		redis.set(key,list,3 * 60);
	}
  return list;
}
return cacheList;
```

通常来说，解决缓存穿透有两种方式：

- 为不存在的 key 设置空值

  - 伪代码如下：

    ```java
    List<String> cacheList = redis.get(key);
    if(CollUtil.isEmpty(cacheList)){
    	// 不管有没有在数据库中查询到数据，都给key设置值   
    	List<String> list = mysql.getList(key);
    	redis.set(key,list,3 * 60);
      return list;
    }
    return cacheList;
    ```

- 使用布隆过滤器

  - 之前在一篇公众号上看到的文章，讲解的挺好的：[《布隆过滤器究竟是什么，这篇讲的明明白白的》](https://mp.weixin.qq.com/s/Y7OJ0ntjU0pumWuwFoY8mQ)
  - 布隆过滤器就相当于在 Cache 之前，就做了一层过滤，防止恶意请求这种不存在的 key
  - 但是布隆过滤器也不是万能的，也会存在误判的可能性

## 缓存雪崩

在某个时间点，大批的 key 出现过期，导致所有的请求全部打到数据库上，把数据库压垮，这种就是缓存雪崩，通常解决缓存雪崩有如下的几种方案：

- **永不过期**：设置 key 永不过期，但是这种会占用服务器挺多内存；
- **过期时间错开**：比如这个 key 设置的过期时间是 5 分钟，那另外一个 key 设置的过期时间则为 7 分钟，把过期时间错开，防止在某个时间点同时失效
- **多缓存结合**：在数据库和 Redis 再加一层缓存，比如 Memcache，这样的话，缓存一旦过期，Memcache 里面还可以顶一会儿；
  - ![](https://raw.githubusercontent.com/superleeyom/blog/main/img/20201222220143.png)
- **采购第三方的 Redis 服务**：现在很多云平台都有推出 Redis 服务，有单机的，集群的，可以根据自己的使用场景去采购，当然人家也帮你处理好了这些问题，有钱啥问题都能解决。

## 缓存击穿

当前的某个热点 key 缓存过期，同一时间，有大量的请求同时来访问这个 key，导致所有的请求都打到数据库上去了，把数据库压垮。那通常遇到这种问题的话，一般就是使用排斥锁，当然也有一种粗暴的办法，就是设置永不过期，但是这种粗暴方式，大多数情况下不适用。

关于排斥锁，可以这样理解，第一个请求达到请求 key 发现缓存里面没有，允许它去数据库查询，同时加锁，这样第二个请求，第三个请求…都会被锁阻塞到当前，当第一个请求从数据库查询到数据后，将数据缓存到 Redis 中，然后释放锁，这样第二个，第三个请求...，就直接可以从缓存中拿数据，就不会再打到数据库，这样就减少了数据库的并发压力。

```java
String get(String key) {  
   String value = redis.get(key);  
   if (value  == null) {  
    if (redis.setnx(key_mutex, "1")) {  
        // 给锁设置一个过期时间，防止持有锁的人挂了，导致锁不能释放
        redis.expire(key_mutex, 3 * 60)  
        // 从DB中查询数据并缓存
        value = db.get(key);  
        redis.set(key, value);
      	// 释放锁
        redis.delete(key_mutex);
      	return value;
    } else {  
        //其他线程休息100毫秒后重试  
        Thread.sleep(100);  
        get(key);  
    }  
  }
  return value;
}
```

其实对于这些热点 key，最好还是有个独立的服务，去定时的刷新缓存，这样的话，很大的程度上可以避免这种问题。