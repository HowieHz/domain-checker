# domain-checker
 
> 通过查询 whois 批量检查域名是否过期的小工具

![GitHub](https://img.shields.io/github/license/HowieHz/domain-checker)
![GitHub all releases](https://img.shields.io/github/downloads/HowieHz/domain-checker/total)
![GitHub release (latest by date)](https://img.shields.io/github/downloads/HowieHz/domain-checker/latest/total)
![GitHub repo size](https://img.shields.io/github/repo-size/HowieHz/domain-checker)

- 异步查询

--- 

## 目录

- [domain-checker](#domain-checker)
  - [目录](#目录)
  - [使用方法](#使用方法)
  - [使用示例](#使用示例)
    - [指定输出文件](#指定输出文件)
    - [安静模式](#安静模式)
  - [项目鸣谢](#项目鸣谢)
  - [开发指南](#开发指南)
  - [更新日志](#更新日志)
  - [项目数据统计](#项目数据统计)
    - [Star History](#star-history)

--- 

## 使用方法

```bash
usage: main.py [-h] [-i INPUT] [-o OUTPUT] [-e ERROR] [-q [True]]

options:
  -h, --help            显示此帮助信息并退出程序
  -i INPUT, --input INPUT
                        指定输入文件，默认为 input.txt
  -o OUTPUT, --output OUTPUT
                        指定保存过期域名的文件
  -e ERROR, --error ERROR
                        指定保存未能成功查询的域名的文件
  -q [True], --quiet [True]
                        使程序减少输出。--quiet 或 --quiet True 均可启用此选项
```

## 使用示例

- 要查询的域名放入 input.txt，一行一个，以下均为可接受形式

```
luogu.com.cn
https://luogu.com.cn
luogu.com.cn/index.html
blog.luogu.com.cn
www.luogu.com.cn/index.html?id=1
aaa.www.luogu.com.cn/aaaa/aaaa
```

运行以下指令（假设二进制文件名为 `main.exe`）

如果仅想在终端查看结果，而不想输出结果到文件，可以使用以下指令

```bash
main.exe -i input.txt
```

input.txt 为 input 默认值，所以上面的指令也可以改写为

```bash
main.exe
```

### 指定输出文件

- 指定 error.txt 文件中将放置查询失败\解析失败的域名
- 指定 output.txt 文件中将放置查询出已过期的域名

> 指令指定的 input.txt output.txt error.txt 无需提前创建

```bash
main.exe -i input.txt -o output.txt -e error.txt
```

input.txt 为 input 默认值，所以上面的指令也可以改写为

```bash
main.exe -o output.txt -e error.txt
```

### 安静模式

如果仅想要将结果输出到文件，终端不输出处理结果，可以使用以下指令

```bash
main.exe -q -o output.txt -e error.txt
```

## 项目鸣谢

- [WuSuoV/SkyQianWhois](https://github.com/WuSuoV/SkyQianWhois) 参考此项目的代码完成此项目 whois 查询部分，赞美作者。

## 开发指南

见 [CONTRIBUTING](./CONTRIBUTING)

## 更新日志

见 [Releases](https://github.com/HowieHz/domain-checker/releases)

## 项目数据统计

### Star History

<a href="https://star-history.com/#HowieHz/domain-checker&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=HowieHz/domain-checker&type=Date&theme=dark" loading="lazy" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=HowieHz/domain-checker&type=Date" loading="lazy" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=HowieHz/domain-checker&type=Date" loading="lazy" />
 </picture>
</a>