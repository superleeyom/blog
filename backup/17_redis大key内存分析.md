# [redis大key内存分析](https://github.com/superleeyom/blog/issues/17)

最近 redis 的内存占用比较高，需要分析下哪些 key 内存占用率比较高，所以整理下分析的思路和笔记。

## bigkeys

使用 redis 自带的查询工具：

```
redis-cli -p 6379 -a 密码 --bigkeys
```

比如我执行结果：

```
[root@localhost ~]# redis-cli -p 6379 -a pd123456 --bigkeys

# Scanning the entire keyspace to find biggest keys as well as
# average sizes per key type.  You can use -i 0.1 to sleep 0.1 sec
# per 100 SCAN commands (not usually needed).

[00.00%] Biggest hash   found so far 'alarm:monitor:virtual.67481375665548lumi.light8.0.8107' with 1 fields
[27.15%] Biggest hash   found so far 'alarmDefinitionCache' with 2 fields
[28.14%] Biggest hash   found so far 'AIOT_DEVICE_INFO' with 62867 fields
[45.33%] Biggest hash   found so far 'RESOURCE_LAST_TS' with 111030 fields
[56.45%] Biggest set    found so far 'SMART_HOTEL_USER_CACHE' with 4 members
[57.53%] Biggest zset   found so far '1h~keys' with 2 members

-------- summary -------

Sampled 128971 keys in the keyspace!
Total key length in bytes is 7387660 (avg len 57.28)

Biggest    set found 'SMART_HOTEL_USER_CACHE' has 4 members
Biggest   hash found 'RESOURCE_LAST_TS' has 111030 fields
Biggest   zset found '1h~keys' has 2 members

0 strings with 0 bytes (00.00% of keys, avg size 0.00)
0 lists with 0 items (00.00% of keys, avg size 0.00)
1 sets with 4 members (00.00% of keys, avg size 4.00)
128969 hashs with 337016 fields (100.00% of keys, avg size 2.61)
1 zsets with 2 members (00.00% of keys, avg size 2.00)
```

我们可以看到打印结果分为两部分，扫描过程部分，只显示了扫描到当前阶段里最大的 key。summary 部分给出了每种数据结构中最大的 Key 以及统计信息。

`redis-cli --bigkeys` 的优点是可以在线扫描，不阻塞服务；缺点是信息较少，内容不够精确。扫描结果中只有 string 类型是以字节长度为衡量标准的。List、set、zset 等都是以元素个数作为衡量标准，只能看出来一个数据结构下有多少数据，看不出来到底占多少内存，看着数值大的并不一定有问题，也不一定占用空间很大，所以这个工具只能用来做大致分析。

## redis-rdb-tools

那其实最好的办法就是离线分析，这里推荐一个工具：[redis-rdb-tools](https://github.com/sripathikrishnan/redis-rdb-tools)，整体的思路就是，导出 redis 的 rdb 备份文件，生成内存报告，把所有 key 转换为 JSON，转存别的 DB 等，这里的 DB 就用 sqlite 就行。

1. 先用 redis-cli 工具连上 Redis 执行 bgsave，备份完成后，将 rdb 文件下载到本地。

2. 安装 `redis-rdb-tools`：

   ```
   pip install rdbtools python-lzf
   ```

   或者：

   ```
   git clone https://github.com/sripathikrishnan/redis-rdb-tools
   cd redis-rdb-tools
   sudo python setup.py install
   ```

   若提示缺少组件，按照提示安装好即可。

3. 若没有安装 `sqlite`，先安装 [sqlite](https://www.runoob.com/sqlite/sqlite-installation.html)。

4. 然后生成内存快照：`rdb -c memory dump.rdb > memory.csv`，生成 CSV 格式的内存报告，这一步可能会比较久，我处理的 rdb 文件 2 个多 g，跑了有一二十分钟，生成的 CSV 文件有 1个g的大小。包含的列有：数据库 ID，数据类型，key，内存使用量（byte），编码。内存使用量包含 key、value 和其他值。

5. 导入 `memory.csv` 到 `sqlite` 数据库，数量量比较大的话，需要等一会儿。

   ```
   $ sqlite3 memory.db
   SQLite version 3.32.3 2020-06-18 14:16:19
   Enter ".help" for usage hints.
   sqlite> create table memory(database int,type varchar(128),key varchar(128),size_in_bytes int,encoding varchar(128),num_elements int,len_largest_element varchar(128));
   sqlite> .mode csv memory
   sqlite> .import memory.csv memory
   ```

6. 查询内容占用最高的几个 key：

   ```
   sqlite> select key,size_in_bytes from memory order by size_in_bytes desc limit 11;
   key,size_in_bytes
   RESOURCE_LAST_TS,895383788
   AIOT_DEVICE_INFO,228425612
   DEVICE_STATUS_LAST_TS_ONLINE,47604980
   DEVICE_STATUS_LAST_TS_BIND,44006972
   RETAIL:TRADE:TRADE-ORDER-TEMP,22917444
   RETAIL:TRADE:TRADE-ORDER-MAPPER,3396012
   retail_biz_config_data:ticket_problem,750140
   areaTree,655416
   retail_biz_config_data:provider_product,486796
   ```

   经过内存分析，内存占用率排前十的key：

   - `RESOURCE_LAST_TS` 占用 853.9 MB

   - `AIOT_DEVICE_INFO` 占用 217.84 MB

   - `DEVICE_STATUS_LAST_TS_ONLINE` 占用 45.3996 MB

   - `DEVICE_STATUS_LAST_TS_BIND` 占用 41.9683 MB

   - `RETAIL:TRADE:TRADE-ORDER-TEMP` 占用 21.8558 MB

   - `RETAIL:TRADE:TRADE-ORDER-MAPPER` 占用 3.2387 MB

   - `retail_biz_config_data:ticket_problem` 占用 0.715389 MB

   - `areaTree` 占用 0.625053 MB

   - `retail_biz_config_data:provider_product` 占用 0.464245 MB

   - `retail_biz_config_data:config_fault` 占用 0.298893 MB

   找到了内存占用率比较高的 key 后，就可以去针对此 key 进行下一步的优化。

## 一些总结

1. **缩短键值对的存储长度**：键值对的长度是和性能成反比的，因此在保证完整语义的同时，我们要尽量的缩短键值对的存储长度，必要时要对数据进行序列化和压缩再存储。
2. **设置键值的过期时间**：我们应该根据实际的业务情况，对键值设置合理的过期时间，这样 Redis 会帮你自动清除过期的键值对，以节约对内存的占用，以避免键值过多的堆积，频繁的触发内存淘汰策略。
3. **禁用长耗时的查询命令**：Redis 绝大多数读写命令的时间复杂度都在 O(1) 到 O(N) 之间，其中 O(1) 表示可以安全使用的，而 O(N) 就应该当心了，N 表示不确定，数据越大查询的速度可能会越慢。因为 Redis 只用一个线程来做数据查询，如果这些指令耗时很长，就会阻塞 Redis，造成大量延时。要避免 O(N) 命令对 Redis 造成的影响，可以从以下几个方面入手改造：
   - 决定禁止使用 keys 命令；

   - 避免一次查询所有的成员，要使用 scan 命令进行分批的，游标式的遍历；

   - 通过机制严格控制 Hash、Set、Sorted Set 等结构的数据大小；

   - 将排序、并集、交集等操作放在客户端执行，以减少 Redis 服务器运行压力；

   - 删除 (del) 一个大数据的时候，可能会需要很长时间，所以建议用异步删除的方式 unlink，它会启动一个新的线程来删除目标数据，而不阻塞 Redis 的主线程。

## 参考资料

- [吐血整理Redis性能优化的13条军规！史上最全](https://cloud.tencent.com/developer/article/1606303)
- [Redis内存分析方法](https://www.cnblogs.com/aresxin/p/9014617.html)
- [找到 Redis 上大量占用内存的 key](https://ylgrgyq.com/find-big-keys-on-redis.html)