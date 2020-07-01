# hacknote

## 漏洞

UAF

## 思路

做过很多次的一道题，但是有两点和`hitcon trainning`不同

- 需要自己调用`system`
- 一个坑：传参的问题，这里传参传递的是`pt[0]`的内容，所以`system`的参数只能是`system`的地址。但是可以加上`||`表示运行多个命令。

