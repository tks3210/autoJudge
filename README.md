# Atcoder-AutoJudge
auto judge system( Scraping Web Page and Build(c++) and Test source code)

# 初期設定(setting)

## 想定環境(environment)

* OS: Windows10 / Mac(Mojave 10.15.4)
* C++ Compiler: gcc (or clang?)
* Python:3.8.2
  * python module: requests, bs4, lxml

## import module
```
pip install requests
pip install bs4 lxml
```

## ディレクトリ構成(directory path)

テスト対象のソースコード(.cpp)が格納されたディレクトリで**autoJudge**がcloneされることを想定しており、
下記のようなディレクトリ構成と命名規則での動作を推奨してます。(ソースコードの命名規則はfileformatから新たに規定可能です。)
(ただ、-pオプションでソースコードのパスを直接指定出来るので、下記の構成じゃなくても動きます。）
```
git clone https://github.com/tks3210/autoJudge.git
```
  

```
.
├── autoJudge (here!)
│   ├── autojudge.py
│   ├── config.py
│   ├── design.pu
│   ├── setting.conf
│   ├── regiater_cmd.py
│   ├── run.sh
│   ├── setting.conf
│   ├── testcase
│   │   ├── abc162
│   │   │   ├── a.cpp
│   │   │   ├── b.cpp
│   │   ├── abc163
│   │   │   :
├── abc162
│   ├── a.cpp
│   ├── b.cpp
│   ├── c.cpp
│   ├── d.cpp
│   ├── e.cpp
│   └── f.cpp
├── abc163
:
```

## 設定ファイル更新(edit config file)

設定ファイル(setting.conf)を更新
```
username:[Atcoder ユーザ名]
password:[Atcoder パスワード]
srcpath:../
fileformat:{problem}_{problem}
defaultextension:.cpp

```
* username/passwordにユーザ名/パスワードを記載
* srcpathにautoJudge.pyからトップディレクトリへの相対パスを記載
* fileformatによって、ソースファイルの命名規則を規定できる。
  * デフォルトでは、a.cppのように認識される。
* defaultextensionにデフォルトで実行したい拡張子を入力（.も含める）

### 命名規則の設定について(fileformat)
fileformat:の記載に沿って、ソースファイルの命名規則をある程度設定できる。  
例えば、abc140_C.cppのようなソースファイルで命名している場合、
```
fileformat:{contest}_{PROBLEM}
```
と書くことで、abc140_C.cppのファイルをコンテストabc140のC問題のソースコードと認識される。
* 命名規則を規定するに当たって使用できる変数は下記の4つ
  * {contest} => Ex. abc140
  * {CONTEST} => Ex. ABC140
  * {problem} => Ex. a
  * {PROBLEM} => Ex. A

## コマンド登録
```
python regiater_cmd.py
``` 
と打ち、regiater_cmd.pyを実行すると  
Windowsなら"C:/commands/"  
Unixなら"/usr/local/bin/"  
配下に、autojudge.pyを実行するrun.shのシンボリックリンクを貼ります

コマンド登録をすると
```
python [autojudge.pyまでのパス] abc164 a
```
を実行する必要があったのが、   
```
atjudge abc 164 a
```
上のように打つとどこからでもautojudgeを呼び出すことが出来ます  

引数をとると
```
python regiater_cmd.py judge
```
引数の文字でコマンド登録されます
```
judge abc 164 a
```


# Execute Test

AC
```
>atjudge abc162 abc162_a
Judging ../abc162/a.cpp
testcase 1: AC
testcase 2: AC
testcase 3: AC
result: AC
```
WA

```
>atjudge abc162 abc162_a
Judging ../abc162/a.cpp
testcase 1: WA
 predicted:8
 result:4
testcase 2: AC
testcase 3: AC
result: WA
```
TLE
```
>atjudge abc162 abc162_a
Judging ../abc162/a.cpp
testcase 1: AC
testcase 2: TLE
testcase 3: TLE
result: TLE
```
RE
```
>atjudge abc162 a -p ../abc162/a.py 
Judging ../abc162/a.py
Traceback (most recent call last):
  File "../abc162/a.py", line 2, in <module>
    if 7 in s:
TypeError: 'in <string>' requires string as left operand, not int
testcase 1: RE
 predicted:
 result:Yes
Traceback (most recent call last):
  File "../abc162/a.py", line 2, in <module>
    if 7 in s:
TypeError: 'in <string>' requires string as left operand, not int
testcase 2: RE
 predicted:
 result:No
Traceback (most recent call last):
  File "../abc162/a.py", line 2, in <module>
    if 7 in s:
TypeError: 'in <string>' requires string as left operand, not int
testcase 3: RE
 predicted:
 result:Yes
result: RE
```

# Add original testcase

-aオプションでテストケース追加

```
>atjudge abc162 abc162_a -a
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
>atjudge abc162 d -i
Atcoder Username:tks_fj
Atcoder Password:*******
Src Directory(Ex. ./aaa/abc140/abc140.cpp => input "./aaa"):../../02_contest
Judging ../../02_contest/abc162/d.cpp
testcase 1: AC
testcase 2: AC
testcase 3: AC
result: AC
```

# Specify source-code path

-pオプションでソースコードのパスを指定可能

```
>atjudge abc162 abc162_a -p ../../02_contest/abc162/abc162_a.cpp
Judging a../../02_contest/abc162/abc162_a.cpp
testcase 1: AC
testcase 2: AC
testcase 3: AC
testcase 4: AC
result: AC
```
