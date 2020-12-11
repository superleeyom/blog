# [Java8函数式编程中比较实用的操作语法](https://github.com/superleeyom/blog/issues/2)

![java8-stream](https://user-images.githubusercontent.com/22115219/95572264-483a9580-0a5c-11eb-8cc7-0f908e997cc0.png)

## 分组（一对多）
假如有如下的一个数据结构：
```json
[
  {
    "userId": 1,
    "name": "王二狗",
    "className": "classA"
  },
  {
    "userId": 2,
    "name": "李老四",
    "className": "classA"
  },
  {
    "userId": 3,
    "name": "张翠花",
    "className": "classB"
  },
  {
    "userId": 4,
    "name": "李雷",
    "className": "classB"
  }
]
```
需要将它按班级`className`进行分组，即如下的数据结构：
```json
{
  "classA": [
    {
      "userId": 1,
      "name": "王二狗",
      "className": "classA"
    },
    {
      "userId": 2,
      "name": "李老四",
      "className": "classA"
    }
  ],
  "classB": [
    {
      "userId": 3,
      "name": "张翠花",
      "className": "classB"
    },
    {
      "userId": 4,
      "name": "李雷",
      "className": "classB"
    }
  ]
}
```
学生实体类 `Student.java`：
```java
@Data
@AllArgsConstructor
public class Student {

    private long userId;

    private String name;

    private String className;
}
```
采用Java8函数式编程 `groupingBy` 语法进行快速分组：
```java
Student s1 = new Student(1, "王二狗", "classA");
Student s2 = new Student(2, "李老四", "classA");
Student s3 = new Student(3, "张翠花", "classB");
Student s4 = new Student(4, "李雷", "classB");
List<Student> list = new ArrayList<>();
list.add(s1);
list.add(s2);
list.add(s3);
list.add(s4);
Map<String, List<Student>> map = list.stream().collect(Collectors.groupingBy(Student::getClassName));
System.out.println(JSONUtil.toJsonStr(map));
```

## 分组（一对一）
还是这个数据结构：
```json
[
  {
    "userId": 1,
    "name": "王二狗",
    "className": "classA"
  },
  {
    "userId": 2,
    "name": "李老四",
    "className": "classA"
  },
  {
    "userId": 3,
    "name": "张翠花",
    "className": "classB"
  },
  {
    "userId": 4,
    "name": "李雷",
    "className": "classB"
  }
]
```
只不过要按用户的 `userId` 进行分组，分组后的数据格式如下：
```json
{
  "1": {
    "className": "classA",
    "userId": 1,
    "name": "王二狗"
  },
  "2": {
    "className": "classA",
    "userId": 2,
    "name": "李老四"
  },
  "3": {
    "className": "classB",
    "userId": 3,
    "name": "张翠花"
  },
  "4": {
    "className": "classB",
    "userId": 4,
    "name": "李雷"
  }
}
```
采用Java8函数式编程的 `toMap` 语法进行快速分组：
```java
Map<Long, Student> studentMap = list.stream().collect(Collectors.toMap(Student::getUserId, student -> student, (k1, k2) -> k1));
```

## 对集合中重复的元素进行去重
对于简单的集合，比如字符串，整型类的集合，采用 `distinct` 进行快速去重：
```java
List<String> strList = Arrays.asList("a", "b", "c", "c", "d");
List<String> distinctList = strList.stream().distinct().collect(Collectors.toList());
System.out.println(JSONUtil.toJsonStr(distinctList));
```
对于集合元素是对象的，根据对象指定的属性进行去重：
```java
// 根据className去重
List<Student> unique = list.stream().collect(Collectors.collectingAndThen(
    Collectors.toCollection(() -> new TreeSet<>(Comparator.comparing(Student::getClassName))), ArrayList::new));
System.out.println(JSONUtil.toJsonStr(unique));
```
```java
// 根据userId和className去重
List<Student> unique2 = list.stream().collect(Collectors.collectingAndThen(
    Collectors.toCollection(() -> new TreeSet<>(Comparator.comparing(o -> o.getUserId() + ";" + o.getClassName()))), ArrayList::new));
System.out.println(JSONUtil.toJsonStr(unique2));
```
## 对集合元素进行快速排序
```java
Student s1 = new Student(1, "王二狗", "classA",10);
Student s2 = new Student(2, "李老四", "classA",9);
Student s3 = new Student(3, "张翠花", "classB",8);
Student s4 = new Student(4, "李雷", "classB", 12);
List<Student> list = new ArrayList<>();
list.add(s1);
list.add(s2);
list.add(s3);
list.add(s4);
// 按照年龄进行升序
list.sort(Comparator.comparing(Student::getAge));
// 按照年龄进行降序
list.sort(Comparator.comparing(Student::getAge).reversed());
```

## 快速判断对象集合中是否存在指定的元素

```java
// 查找学生当中是否存在一个叫王二狗的同学
boolean matchResult = list.stream().anyMatch(student -> "王二狗".equals(student.getName()));
```

## 将List转变为逗号分隔的字符串

```java
List<String> cities = Arrays.asList("Milan", "London", "New York", "San Francisco");
String citiesCommaSeparated = String.join(",", cities);
System.out.println(citiesCommaSeparated);
// 输出: Milan,London,New York,San Francisco
```

## 参考文章

- [一文带你玩转 Java8 Stream 流，从此操作集合 So Easy](https://juejin.im/post/6844903830254010381)