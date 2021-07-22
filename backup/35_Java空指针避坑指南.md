# [Java空指针避坑指南](https://github.com/superleeyom/blog/issues/35)

把阿里巴巴的《Java开发手册》里，关于 NPE异常总结了下，**预防空指针异常，从你我做起！** 

---

> 【强制】所有的 POJO 类属性必须使用包装数据类型。


数据库的查询结果可能是 null，因为自动拆箱，用基本数据类型接收有 NPE 风险。

---

> 【强制】在使用 java.util.stream.Collectors 类的 toMap()方法转为 Map 集合时，一定要注意当 value 为 null 时会抛 NPE 异常。


```java
List<Pair<String, double>> pairArrayList = new ArrayList<>(2);
pairArrayList.add(new Pair<>("version1", 8.3));
pairArrayList.add(new Pair<>("version2", null));
// 抛出 NullPointerException 异常
pairArrayList.stream().collect(Collectors.toMap(Pair::getKey, Pair::getValue));

```


因为 HashMap 的 merge 方法里，若 value 为 null，则会抛 NPE：

```java
@Override
public V merge(K key, V value,BiFunction<? super V, ? super V, ? extends V> remappingFunction) {
  if (value == null)
    // 抛出 NullPointerException 异常
    throw new NullPointerException();
  //....
}
```


这个问题`java9`已经修复，所以也可以尝试升级jdk，或者把value为null的过滤掉就行。另外注意：**如果key相同也会抛异常** ，改成如下代码相同的key就不会报异常，新key的value会替换旧key的value：

```Java
pairArrayList.stream().collect(Collectors.toMap(Pair::getKey, Pair::getValue,(v1, v2) -> v2))
```


---

> 【强制】使用集合转数组的方法，必须使用集合的 toArray(T[] array)，传入的是类型完全一 致、长度为 0 的空数组。


```java
List<String> list = new ArrayList<>(2);
list.add("guan");
list.add("bao");
// array 的值为：["guan","bao",null,null]
String[] array = list.toArray(new String[4]);
```


如果循环遍历 array 的时候，不注意，就有可能抛 NPE：

```java
for (String s : array) {
  // 抛出 NullPointerException 异常
  System.out.println(s.length());
}
```


所以建议数组空间大小的 length 设置为0，动态创建与 list size 相同的数组，性能最好。

```java
String[] array = list.toArray(new String[0]);
```


---

> 【强制】在使用 Collection 接口任何实现类的 addAll()方法时，都要对输入的集合参数进行 NPE 判断。


```java
List<String> list = new ArrayList<>(2);
list.add("guan");
list.add("bao");
List<String> listSecond = null;
// 抛出 NullPointerException 异常
list.addAll(listSecond);
```


观察 ArrayList 的 addAll 方法的源码：

```java
public Boolean addAll(Collection<? extends E> c) {
  // 若c为null，这里会抛NPE
  Object[] a = c.toArray();
  int numNew = a.length;
  ensureCapacityInternal(size + numNew);
  // Increments modCount
  System.arraycopy(a, 0, elementData, size, numNew);
  size += numNew;
  return numNew != 0;
}
```


所以正确的做法是，对输入参数做判空化处理：

```java
// CollUtil.emptyIfNull(List<T> set)方法是 hutool里面的对集合null设置为empty的方法，方法内实际为：
// (null == set) ? Collections.emptyList() : set
list.addAll(CollUtil.emptyIfNull(listSecond));
```


---

> 【推荐】高度注意 Map 类集合 K/V 能不能存储 null 值的情况。


![](http://image.leeyom.top/blog/20210722121222.png)

---

> 【强制】三目运算符(condition? 表达式 1 : 表达式 2) 中，高度注意表达式 1 和 2 在类型对齐时，可能抛出因自动拆箱导致的 NPE 异常。


```java
Integer a = 1;
Integer b = 2;
Integer c = null;
Boolean flag = false;
// a*b的结果是int类型，那么c会强制拆箱成int类型，抛出NPE异常
Integer result = (flag ? a * b : c);
```


`a*b` 包含了算术运算，因此会触发自动拆箱过程（会调用 intValue 方法），此时`a*b`的结果是 int 类型，那么c会强制拆箱成 int 类型，以下两种场景会触发类型对齐的拆箱操作：

1. 表达式 1 或表达式 2 的值只要有一个是原始类型。 

2. 表达式 1 或表达式 2 的值的类型不一致，会强制拆箱升级成表示范围更大的那个类型。

---

> 【强制】当某一列的值全是 NULL 时，count(col)的返回结果为 0，但 sum(col)的返回结果为 NULL，因此使用 sum()时需注意 NPE 问题。


![](http://image.leeyom.top/blog/20210722143358.png)

可以使用如下方式来避免 sum 的 NPE 问题：`SELECT IFNULL(SUM(column), 0) FROM table;`

---

> 【推荐】方法的返回值可以为 null，不强制返回空集合，或者空对象等，必须添加注释充分说 明什么情况下会返回 null 值。


防止 NPE 是调用者的责任。即使被调用方法返回空集合或者空对象，对调用者来说，也并非高枕无忧，必须考虑到远程调用失败、序列化失败、运行时异常等场景返回 null 的情况。

---

> 【强制】当 switch 括号内的变量类型为 String 并且此变量为外部参数时，必须先进行 null 判断。


```java
public static void method(String param) {
    switch(param) {
        case "sth":
            System.out.println("it's sth");
            break;
        case "null":
            System.out.println("it's null");
            break;
        default:
            System.out.println("default");
    }
}

public static void main(String[] args) {
    // 会报NPE异常
    method(null);
}
```


---

> 【强制】字符串判断相等，常量一定要写在前面


```Java
String str1 = null;
String str2 = "hello world";
// 错误的写法，会抛NPE
str1.equals(str2);
// 正确写法
str2.equals(str1);

```


---

其他的可能产生 NPE 的场景：

1. 返回类型为基本数据类型，return 包装数据类型的对象时，自动拆箱有可能产生 NPE：

```java
public int f() {
  Integer a = null;
  // 抛出NPE异常
  return a;
}
```


&ensp;&ensp;&ensp;&ensp;另外这种情况也会自动拆箱产生NPE：

```java
Integer num = null;
// 抛出NPE异常
if(num > 1) {
  // do someing
}
```


2. 数据库的查询结果可能为 null：

```java
// 数据库查询用户信息
User user = userMapper.getById(123);
// user可能为null，抛出NPE异常
String userName = user.getUserName();
```


3. 远程调用返回对象时，一律要求进行空指针判断，防止 NPE：

```java
ApiResponse<UserInfoDTO> apiResponse = userFeign.getById(123);
// user可能为null
User user = apiResponse.getData();
if(user!=null){
  String userName = user.getUserName();
}
```


4. 对于 Session 中获取的数据，建议进行 NPE 检查，避免空指针。

5. 级联调用 `obj.getA().getB().getC();`一连串调用，易产生 NPE。

6. 集合里的元素即使 isNotEmpty，取出的数据元素也可能为 null，因为 List 里面也可以存 null。

可以考虑使用 JDK8 的 Optional 类来防止 NPE 问题。

---
