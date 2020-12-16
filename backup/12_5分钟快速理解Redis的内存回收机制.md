# [5分钟快速理解Redis的内存回收机制](https://github.com/superleeyom/blog/issues/12)

## 设置键的生存时间

- `EXPIRE key seconds`：用于设置秒级精度的生存时间，它可以让键在指定的秒数之后自动被移除
- `PEXPIRE key milliseconds`：用于设置毫秒级精度的生存时间，它可以让键在指定的毫秒数之后自动被移除
- `EXPIREAT key timestamp`：将键 key 的过期时间设置为 timestamp 所指定的秒数时间戳
- `PEXPIREAT key timestamp`：将键 key 的过期时间设置为 timestamp 所指定的毫秒数时间戳

虽然有多种不同单位和不同形式的设置命令，但实际上`EXPIRE`、`PEXPIRE`、`EXPIREAT` 三个命令都是使用`PEXPIREAT`命令来实现的：无论客户端执行的是以上四个命令中的哪一个，经过转换之后，最终的执行效果都和执行`PEXPIREAT`命令一样。

![](https://raw.githubusercontent.com/superleeyom/blog/main/img/20201207155506.png)

在使用键过期功能时，组合使用 `SET `命令和 `EXPIRE/PEXIRE` 命令的做法非常常见：

- `SET key value [EX seconds] [PX milliseconds]`：在设置 key 的时候，同时设置过期时间，此命令等价于两条命令：

  ```
  SET key value
  EXPIRE key seconds
  ```

使用带有 `EX` 选项或 `PX` 选项的` SET` 命令除了可以减少命令的调用数量并提升程序的执行速度之外，更重要的是保证了操作的**原子性**，使得「为键设置值」和「为键设置生存时间」这两个操作可以一起执行。如果拆分成 `SET` 和 `EXPIRE` 两条命令执行的话，如果 Redis 服务器在成功执行 `SET` 命令之后因为故障下线，导致 `EXPIRE` 命令没有被执行，那么 `SET` 命令设置的缓存就会一直存在，而不会因为过期而自动被移除。

`EXPIREAT/PEXPIREAT`，还是 `EXPIRE/PEXIRE`，它们都只能对整个键进行设置，而无法对键中的某个元素进行设置，比如，用户只能对整个集合或者整个散列设置生存时间/过期时间，但是却无法为集合中的某个元素或者散列中的某个字段单独设置生存时间/过期时间，这也是目前 Redis 的自动过期功能的一个缺陷。

## 移除过期时间

能设置过期时间，自然也就能移除过期时间，`PERSIST`命令就是`PEXPIREAT`命令的反操作：`PERSIST key`命令在过期字典中查找给定的键，并解除键和值（过期时间）在过期字典中的关联。

## 计算并返回剩余时间

`TTL` 命令以秒为单位返回键的剩余生存时间，而`PTTL`命令则以毫秒为单位返回键的剩余生存时间：

```
TTL key
PTTL key
```

## Redis如何保存过期时间

Redis 里面有一个过期字典 expires，专门存储 Redis key 的过期时间，一个键的 key，有两个指向，一个指向实际的 value，一个指向它的的过期时间，如下图所示

![](https://raw.githubusercontent.com/superleeyom/blog/main/img/20201216170122.png)

判定一个键是否过期，主要分为两步：

1. 检查给定键是否存在于过期字典：如果存在，那么取得键的过期时间。
2. 检查当前 UNIX 时间戳是否大于键的过期时间：如果是的话，那么键已经过期；否则的话，键未过期。

## 过期键删除策略

- 定时删除：在设置键的过期时间的同时，创建一个定时器（timer），让定时器在键的过期时间来临时，立即执行对键的删除操作。
  - 定时删除占用太多 CPU 时间，影响服务器的响应时间和吞吐量。因为在过期键比较多的情况下，删除过期键这一行为可能会占用相当一部分 CPU 时间。
- 惰性删除：放任键过期不管，但是每次从键空间中获取键时，都检查取得的键是否过期，如果过期的话，就删除该键；如果没有过期，就返回该键。
  - 惰性删除浪费太多内存，有内存泄漏的危险。因为当过期键一直没有访问将无法得到及时删除，从而导致内存不能及时释放。
- 定期删除：每隔一段时间，程序就对数据库进行一次检查，删除里面的过期键。至于要删除多少过期键，以及要检查多少个数据库，则由算法决定。
  - 定期删除策略是前两种策略的一种整合和折中，如果采用定期删除策略的话，服务器必须根据情况，合理地设置删除操作的执行时长和执行频率，否则到头来，还是会搞得跟「定时删除」和「惰性删除」一样。

Redis 服务器实际使用的是**惰性删除**和**定期删除**两种策略，其中惰性删除策略会调用 `expireIfNeeded` 函数对键进行检查：

- 如果输入键已经过期，那么 `expireIfNeeded` 函数将输入键从数据库中删除
- 如果输入键未过期，那么 `expireIfNeeded` 函数不做动作

示意图如下：

![](https://raw.githubusercontent.com/superleeyom/blog/main/img/20201216172630.png)

![](https://raw.githubusercontent.com/superleeyom/blog/main/img/20201216172847.png)

而 Redis 的定期删除策略，`activeExpireCycle` 函数就会被调用，它在规定的时间内，分多次遍历服务器中的各个数据库，从数据库的 expires 过期字典中随机检查一部分键的过期时间，并删除其中的过期键，如下图所示：

![](https://raw.githubusercontent.com/superleeyom/blog/main/img/20201216193720.png)

## Redis内存回收机制

Redis 的内存回收机制主要体现在以下两个方面：

- 删除到达过期时间的键对象，就是上面说的过期键删除策略。

- 内存使用达到`maxmemory`上限时触发内存溢出控制策略。

当 Redis 所用内存达到 `maxmemory` 上限时会触发相应的溢出控制策略。 具体策略受 `maxmemory-policy` 参数控制，Redis 支持 6 种策略：

- `noeviction`：默认策略，不会删除任何数据，拒绝所有写入操作并返 回客户端错误信息`（error）OOM command not allowed when used memory`，此时 Redis 只响应读操作。
- `volatile-lru`：根据 LRU 算法删除设置了超时属性（expire）的键，直到腾出足够空间为止。如果没有可删除的键对象，回退到 noeviction 策略。
- `allkeys-lru`：根据 LRU 算法删除键，不管数据有没有设置超时属性， 直到腾出足够空间为止。
- `allkeys-random`：随机删除所有键，直到腾出足够空间为止。
- `volatile-random`：随机删除过期键，直到腾出足够空间为止。
- `volatile-ttl`：根据键值对象的 ttl 属性，删除最近将要过期数据。如果没有，回退到 noeviction 策略。

内存溢出控制策略可以采用如下命令动态配置：

```
config set maxmemory-policy {policy}
```

当 Redis 一直工作在内存溢出`（used_memory>maxmemory）`的状态下且设置非 noeviction 策略时，会频繁地触发回收内存的操作，影响 Redis 服务器的性能。频繁执行回收内存成本很高，主要包括查找可回收键和删除键的开销，如果当前 Redis 有从节点，回收内存操作对应的删除命令会同步到从节点，导致写放大的问题。

## 资料
- 《Redis开发与运维》
- 《Redis使用手册》
- 《Redis设计与实现》
