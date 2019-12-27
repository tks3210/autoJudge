# Atcoder-AutoJudge
auto judge system( Scraping Web Page and Build(c++) and Test source code)

# 初期設定(setting)

## 想定環境(environment)

* OS: Windows10 / Mac(Mojave 10.14.6)
* C++ Compiler: gcc (or clang?)
* Python:3.7.1
  * python module: requests, bs4, lxml

## import module
```
pip install requests
pip install bs4, lxml
```

## ディレクトリ構成(directory path)

テスト対象のソースコード(.cpp)が格納されたディレクトリで**autoJudge**がcloneされることを想定しており、
下記のようなディレクトリ構成と命名規則での動作を推奨してます。  
(ただ、-pオプションでソースコードのパスを直接指定出来るので、下記の構成じゃなくても動きます。）
```
git clone https://github.com/tks3210/autoJudge.git
```
  

```
.
├── autoJudge (here!)
│   ├── setting.conf
│   ├── autojudge.py
│   ├── testcase
│   │   ├── abc142@abc142_a.txt
│   │   └── abc143@abc143_a.txt 
│   └── design.pu
├── abc142
│   ├── abc142_a.cpp
│   ├── abc142_b.cpp
│   ├── abc142_c.cpp
│   ├── abc142_d.cpp
│   ├── abc142_e.cpp
│   └── abc142_f.cpp
├── abc143
:
```

## 設定ファイル更新(edit config file)

設定ファイル(setting.conf)を更新
```
username:[Atcoder ユーザ名]
password:[Atcoder パスワード]
srcpath:../
```
* username/passwordにユーザ名/パスワードを記載
* srcpathにautoJudge.pyからトップディレクトリへの相対パスを記載

# Execute Test

AC
```
>python autojudge.py abc143 abc143_a
Judging abc143/abc143_a...
testcase 1: AC
testcase 2: AC
testcase 3: AC
result: AC
```
WA

```
>python autojudge.py abc143 abc143_a
Judging abc143/abc143_a...
testcase 1: WA
 predicted:8
 result:4
testcase 2: AC
testcase 3: AC
result: WA
```
TLE
```
>python autojudge.py abc143 abc143_a
Judging abc143/abc143_a...
testcase 1: AC
testcase 2: TLE
testcase 3: TLE
result: TLE
```
# Add original testcase

-aオプションでテストケース追加

```
>python autojudge.py abc143 abc143_a -a
type test input(exit by "quit")
20 7
quit
type test output(exit by "quit")
6
quit
```

# Update Configuration(setting.conf)

-iオプションで設定ファイル再構成

```
>python autojudge.py abc143 abc143_d -i
Atcoder Username:tks_fj
Atcoder Password:*******
Src Directory(Ex. ./aaa/abc140/abc140.cpp => input "./aaa"):../../02_contest
Judging abc143/abc143_d...
testcase 1: AC
testcase 2: AC
testcase 3: AC
result: AC
```

# Specify source-code path

-pオプションでソースコードのパスを指定可能

```
>python autojudge.py abc143 abc143_a -p ../../02_contest/abc143/abc143_a.cpp
Judging abc143/abc143_a...
testcase 1: AC
testcase 2: AC
testcase 3: AC
testcase 4: AC
result: AC
```