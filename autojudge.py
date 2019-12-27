# -*- coding: utf-8 -*-
import requests
import os, sys
import time
import subprocess
import select
from bs4 import BeautifulSoup

LOGIN_URL = 'https://atcoder.jp/login?continue=https%3A%2F%2Fatcoder.jp%2Fcontests%2F'
CONTEST_URL = 'https://atcoder.jp/contests/'
CONF_FILE = 'setting.conf'
TESTCASES_PATH = 'testcase'
TLE_TIME = 2

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
COLORRESET = "\033[0m"

class ExecuteTestCases:
    """テストケースの実行"""


    def __init__(self, testcases):
        self.testinfo = testcases[0]
        self.testCases = testcases[1:]
        self.result = {}
        self.result["build"] = 0
        self.result["result"] = {"AC":0, "WA":0, "TLE":0}

    def Execute(self, srcpath = ""):
        """テストを実行"""

        print(YELLOW + "Judging " + self.testinfo["contest"] + "/" + self.testinfo["testname"] + "..." + COLORRESET)
        if (srcpath == ""):
            srcpath = self.__GetPath()
        self.__Build(srcpath)
        if (self.result["build"] == 0):
            self.__Run()
        self.__Result()

    def __GetPath(self):
        """
        未指定時にソースコードの場所を取得
        設定ファイル(CONF_FILE)記載の相対パス/コンテスト名/テスト名.cppを返す
        """
        codepath = os.path.join(self.testinfo["contest"], self.testinfo["testname"] + ".cpp")
        workpath = "."
        with open(CONF_FILE, "r") as f:
            while True:
                line = f.readline().rstrip('\n')
                if not line:
                    break
                element = line.split(':')
                if (element[0] == "srcpath"):
                    workpath = element[1]
        return os.path.join(workpath, codepath)

    def __Build(self, srcpath):
        """
        ソースコード(c++)をビルドし、結果をresult["build"]に格納
        ビルド成功(0), ビルド失敗(1), ソース無(2)
        """
        print(RED, end="")
        if (os.path.exists(srcpath) == True):
            cmd = 'g++ -o tmp ' + srcpath
            if (subprocess.run(cmd, shell = True).returncode == 0):
                self.result["build"] = 0
            else:
                self.result["build"] = 1
        else:
            self.result["build"] = 2
        print(COLORRESET, end="")

    def __Run(self):
        try:
            execcmd = ""
            if os.name == "nt":
                execcmd = "tmp.exe"
            else:
                execcmd = "./tmp"
            for i,testcase in enumerate(self.testCases):
                print("testcase " + str(i + 1) + ": ", end="")
                proc = subprocess.Popen(execcmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
                proc.stdin.write(testcase["input"].encode())
                proc.stdin.flush()
                proc.stdout.flush()
                try:
                    proc.wait(TLE_TIME)
                    ans = proc.stdout.read().decode().replace('\r\n','\n')
                    out = testcase["output"].replace('\r\n','\n')
                    if out == ans:
                        self.result["result"]["AC"] += 1
                        print(GREEN + "AC" + COLORRESET)
                    else:
                        self.result["result"]["WA"] += 1
                        print(YELLOW + "WA" + COLORRESET)
                        print(RED + " predicted:"+ ans.rstrip('\r\n') + "\n" + " result:" + out.rstrip('\r\n') + COLORRESET)
                except:
                    self.result["result"]["TLE"] += 1
                    print(YELLOW + "TLE" + COLORRESET)
                    proc.terminate()
                    # process終了後timeoutを設けない場合、tmp.exeが削除できないことがある。
                    time.sleep(1)

        finally:
            if (os.path.exists(execcmd) == True):
                os.remove(execcmd)

    def __Result(self):
        """
        テスト結果を出力する
        全て正解=> AC, 実行時間オーバー=> TLE, 誤りを含む=> WA, コンパイルエラー=> CE
        """


        if (self.result["build"] == 2):
            print(RED, end="")
            print("src file is not found")
            print("please write exact path on " + CONF_FILE + " or specify path(-p)")
            print(COLORRESET, end="")
            return


        if (self.result["build"] == 1):
            RESULT = YELLOW + "CE" + COLORRESET
        elif (self.result["result"]["AC"] == len(self.testCases)):
            RESULT = GREEN + "AC" + COLORRESET
        elif (self.result["result"]["TLE"] >= 1):
            RESULT = YELLOW + "TLE" + COLORRESET
        else: 
            RESULT = YELLOW + "WA" + COLORRESET
        print("result: " + RESULT)

class ManageTestCases:
    """テストケースの管理"""

    def __init__(self, contest_name):
        os.makedirs(TESTCASES_PATH, exist_ok=True)
        self.config = {}
        self.contest = contest_name
        
    def RegisterUser(self):
        """user設定(初回)"""

        print("Atcoder Username:", end="")
        username = input().rstrip('\r\n')
        print("Atcoder Password:", end="")
        password = input().rstrip('\r\n')
        print("Src Directory(Ex. ./aaa/abc140/abc140.cpp => input \"./aaa\"):", end="")
        srcpath = input().rstrip('\r\n')

        with open(CONF_FILE, "w") as f:
            f.write("username:" + username + "\n")
            f.write("password:" + password + "\n")
            f.write("srcpath:" + srcpath + "\n")

    def __UpdateConf(self):
        try:        
            with open(CONF_FILE, "r") as f:
                while True:
                    line = f.readline().rstrip('\r\n')
                    if not line:
                        break
                    element = line.split(':')
                    self.config[element[0]] = element[1]
        except:
            print("cannot open config file.")

    def GetTestCases(self, test_name, islogin = False):
        """指定された問題名からテストケースを取得しリストを返す"""

        self.__UpdateConf()
        file_name = self.contest + "@" + test_name + ".txt"
        testinfo = [{"contest":self.contest, "testname":test_name}]
        # サーバ負荷低減のため同一情報の取得はスクレイピングさせない
        if file_name in os.listdir(TESTCASES_PATH):
            testcases = self.__ReadFile(file_name)
        else:
            testcases = self.__ScrapePage(test_name, islogin)
            self.__WriteFile(file_name, testcases)
        return testinfo + testcases

    def AddTestCases(self, test_name):
        """取得したテストケースに独自のテストケースを追加する"""

        self.__UpdateConf()
        testcase = {}
        print("type test input(exit by \"quit\")")
        testcase["input"] = ""
        while(1):
            line = input()
            if (line == "quit"):
                break;
            testcase["input"] += line + "\n"

        print("type test output(exit by \"quit\")")
        testcase["output"] = ""
        while(1):
            line = input()
            if (line == "quit"):
                break;
            testcase["output"] += line + "\n"
            
        file_name = self.contest + "@" + test_name + ".txt"
        if file_name in os.listdir(TESTCASES_PATH):
            testcases = self.__ReadFile(file_name)
        testcases.append(testcase)
        self.__WriteFile(file_name, testcases)

    def __ReadFile(self, file_name):
        """ファイルを読む"""

        testcases = []
        targ_path = os.path.join(TESTCASES_PATH, file_name)
        with open(targ_path, "r") as f:
            while(1):
                st = f.readline().rstrip('\r\n')
                if 'test case' in st:
                    testcase = {}
                    continue
                if 'input' in st:
                    mode = "input"
                    testcase[mode] = ""
                    continue
                if 'output' in st:
                    mode = "output"
                    testcase[mode] = ""
                    continue        
                if '---fin---' in st:
                    testcases.append(testcase)
                    continue
                if not st:
                    break
                testcase[mode] += st + "\n"
        return testcases

    def __WriteFile(self, file_name, testcases):
        """ファイルを書く"""
        targ_path = os.path.join(TESTCASES_PATH, file_name)
        with open(targ_path, "w") as f:
            for i, q in enumerate(testcases):
                f.write("[test case " + str(i) + "]\n")
                f.write("---input---\n")
                f.write(q["input"])
                f.write("---output---\n")
                f.write(q["output"])
                f.write("---fin---\n")
                
    def __ScrapePage(self, test_name, islogin):
        session = requests.session()
        if islogin == True:
            # loginに必要な認証情報を取得
            self.__LoginPage(session)
 
        pageAll = session.get(CONTEST_URL + str(self.contest) + "/tasks/" + str(test_name))
        testcases = self.__AnalyzePage(pageAll)
        return testcases

    def __LoginPage(self, session):
        """認証が必要なページにログインする"""

        res = session.get(LOGIN_URL + str(self.contest))
        page = BeautifulSoup(res.text, 'lxml')            
        csrf_token = page.find(attrs={'name': 'csrf_token'}).get('value')
        login_info = {
            "csrf_token": csrf_token,
            "username": self.config["username"],
            "password": self.config["password"],
        }
        session.post(LOGIN_URL + str(self.contest), data=login_info)

    def __AnalyzePage(self, page_org):
        """取得した問題のページから問題部分を抽出する"""

        page = BeautifulSoup(page_org.text, 'lxml').find_all(class_ = "part")
        quest_list = []
        quest = {}
        for element in page:
            ele_h3 = element.findChild("h3")
            ele_pre = element.findChild("pre")
            if 'Sample' not in str(ele_h3):
                continue
            if 'Input' in str(ele_h3):
                quest = {}
                quest["input"] = str(ele_pre).lstrip("<pre>").rstrip("</pre>").replace('\r\n','\n')
            else:
                quest["output"] = str(ele_pre).lstrip("<pre>").rstrip("</pre>").replace('\r\n', '\n')
                quest_list.append(quest)
        return quest_list
        

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument("contest_name", help = "set contest name(ex. abc143)", type = str)
    parser.add_argument("question", help = "set question name(ex. abc143_a)", type = str)
    parser.add_argument("-p", "--path", help = "set path of source code", type = str)
    parser.add_argument("-a", "--addtest", help = "add testcase", action="store_true")
    parser.add_argument("-i", "--init", help = "set configuration", action ="store_true")
    args = parser.parse_args()

    ac = ManageTestCases(args.contest_name)

    if (args.init == True):
        ac.RegisterUser()

    if (args.addtest == True):
        ac.AddTestCases(args.question)
        exit()

    testcases = ac.GetTestCases(args.question, True)
    ex = ExecuteTestCases(testcases)
    if (args.path != None):
        ex.Execute(args.path)
    else:
        ex.Execute()