# domain-checker
 
> 通过查询 whois 批量检查域名是否过期的小工具

![GitHub](https://img.shields.io/github/license/HowieHz/domain-checker)
![GitHub all releases](https://img.shields.io/github/downloads/HowieHz/domain-checker/total)
![GitHub release (latest by date)](https://img.shields.io/github/downloads/HowieHz/domain-checker/latest/total)
![GitHub repo size](https://img.shields.io/github/repo-size/HowieHz/domain-checker)

- 异步查询
- 多进程并发

## 为什么写这个小工具

- 在线工具：广告多，许多域名无法查询
- 类似项目：不能满足需求，没法过滤诸如 `https://www.aaa.com.cn/index.html?id=1` 的域名是否过期

类似项目：  
- [Matty9191/dns-domain-expiration-checker](https://github.com/Matty9191/dns-domain-expiration-checker) 年久失修，上一次更新在 4 年前
- [click0/domain-check-2](https://github.com/click0/domain-check-2) 需要 Bash 才能使用，需要干净的 主域名.顶级域名 作为输入数据才能工作
- [tdulcet/Remote-Servers-Status](https://github.com/tdulcet/Remote-Servers-Status)  至少需要 Bash 4.4 和 curl、netcat、ping、dig、delv、whois 和 openssl 命令
- [ashworthconsulting/domain-check](https://github.com/ashworthconsulting/domain-check) 年久失修，上一次更新在 9 年前

--- 

## 目录

- [domain-checker](#domain-checker)
  - [为什么写这个小工具](#为什么写这个小工具)
  - [目录](#目录)
  - [使用方法](#使用方法)
  - [使用示例](#使用示例)
    - [指定输出文件](#指定输出文件)
    - [提高使用的进程数](#提高使用的进程数)
    - [提高单个进程可使用使用的线程数](#提高单个进程可使用使用的线程数)
    - [安静模式](#安静模式)
  - [项目鸣谢](#项目鸣谢)
  - [开发指南](#开发指南)
  - [更新日志](#更新日志)
  - [项目数据统计](#项目数据统计)
    - [Star History](#star-history)

--- 

## 使用方法

```bash
usage: domain-checker.exe [-h] [-i INPUT] [-o OUTPUT] [-e ERROR] [-p NUM_PROCESSES] [-t MAX_NUM_THREADS_PER_PROCESS] [-utl [True]]
               [-q [True]]

options:
  -h, --help            显示此帮助信息并退出程序
  -i INPUT, --input INPUT
                        指定输入文件，默认为 input.txt
  -o OUTPUT, --output OUTPUT
                        指定保存过期域名的文件
  -e ERROR, --error ERROR
                        指定保存未能成功查询的域名的文件
  -p NUM_PROCESSES, --num-processes NUM_PROCESSES
                        指定并发进程数。默认为 1
  -t MAX_NUM_THREADS_PER_PROCESS, --max-num-threads-per-process MAX_NUM_THREADS_PER_PROCESS
                        指定每进程最大并发线程数。默认为 8
  -utl [True], --unlock-threads-limit [True]
                        解除线程最大值限制。--unlock-threads-limit 或 --unlock-threads-limit True 均可启用此选项
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

运行以下指令（假设二进制文件名为 `domain-checker.exe`）

如果仅想在终端查看结果，而不想输出结果到文件，可以使用以下指令

```bash
domain-checker.exe -i input.txt
```

input.txt 为 input 默认值，所以上面的指令也可以改写为

```bash
domain-checker.exe
```

### 指定输出文件

- 指定 error.txt 文件中将放置查询失败\解析失败的域名
- 指定 output.txt 文件中将放置查询出已过期的域名

> 指令指定的 input.txt output.txt error.txt 无需提前创建

```bash
domain-checker.exe -i input.txt -o output.txt -e error.txt
```

input.txt 为 input 默认值，所以上面的指令也可以改写为

```bash
domain-checker.exe -o output.txt -e error.txt
```

### 提高使用的进程数

该指令会使用 32 进程查询。首先会把 input.txt 分成 32 份，放入 `./temp/temp_part_0.txt`、`./temp/temp_part_1.txt` …… `./temp/temp_part_31.txt`，后用 32 个进程分别查询。

> 注：程序正常运行结束会清除 `./temp` 中产生的临时文件 `./temp/temp_part_0.txt`、`./temp/temp_part_1.txt` …… `./temp/temp_part_31.txt`

```bash
domain-checker.exe -p 32
```

### 提高单个进程可使用使用的线程数

如果不设限，一般来说一个进程会用到的最大线程为：此进程要处理的文件总行数。

例子：input.txt 有 100 行，开启了 `-p 10` 分配给 10 个进程，每个进程分配到 10 个需要检查的地址（也就是需要处理行数为 10 的文件）。那么不设限的情况下，每个进程会用到的最大线程数一般为 10。

以下指令会将最大进程数提升到 9999。

```bash
domain-checker.exe -t 9999
```

### 安静模式

如果仅想要将结果输出到文件，终端不输出处理结果，可以使用以下指令

```bash
domain-checker.exe -q -o output.txt -e error.txt
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
