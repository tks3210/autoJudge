# -*- coding: utf-8 -*-
import os
import sys
import time
import requests
import subprocess
from bs4 import BeautifulSoup
from config import *


class ExecuteTestCases:
    """テストケースの実行"""

    def __init__(self, testcases):
        self._test_info = testcases[0]
        self._testcases = testcases[1:]
        self._result = {}
        self._result["build"] = 0
        self._result["result"] = {"AC": 0, "WA": 0, "TLE": 0, "RE": 0}

    def execute(self, srcpath=""):
        """テストを実行"""

        if (srcpath == ""):
            self.srcpath = self._get_path()
        else:
            self.srcpath = srcpath

        # ジャッジするファイルパスを出力
        print(YELLOW + "Judging " + self.srcpath + COLORRESET)

        # 拡張子を調べ、Pythonかどうか判定、メンバ変数に格納
        self._is_python = os.path.splitext(self.srcpath)[1] == '.py'
        self._build()
        if self._result["build"] == 0:
            self._run()
        self._show_result()

    def _return_conf_file_info(self, key):
        with open(CONF_FILE, "r") as f:
            while True:
                line = f.readline().rstrip('\n')
                if not line:
                    break
                element = line.split(':')
                if (element[0] == key):
                    return element[1]

    def _get_path(self):
        """
        未指定時にソースコードの場所を取得
        設定ファイル(CONF_FILE)記載の相対パス/コンテスト名/テスト名.cppを返す
        """
        # どの言語のファイルを探すかをconfファイルから取得する
        default_extension = self._return_conf_file_info("defaultextension")
        file_format = self._return_conf_file_info("fileformat")
        if file_format == "":
            file_format = self._test_info["problem"]
        else:
            file_format = file_format.replace('{contest}', self._test_info["contest"])
            file_format = file_format.replace('{problem}', self._test_info["problem"])
            file_format = file_format.replace('{CONTEST}', self._test_info["contest"].upper())
            file_format = file_format.replace('{PROBLEM}', self._test_info["problem"].upper())
        code_path = os.path.join(self._test_info["contest"], file_format + default_extension)
        work_path = self._return_conf_file_info("srcpath")
        if work_path == "":
            work_path = "."

        return os.path.join(work_path, code_path)

    def _build(self):
        """
        ソースコード(c++)をビルドし、結果をresult["build"]に格納
        ビルド成功(0), ビルド失敗(1), ソース無(2)
        """
        # print(RED, end="")
        if (os.path.exists(self.srcpath) is True):
            # Pythonならビルドせずパス
            if self._is_python is True:
                return
            cmd = 'g++ -o tmp ' + self.srcpath
            if (subprocess.run(cmd, shell=True).returncode == 0):
                self._result["build"] = 0
            else:
                self._result["build"] = 1
        else:
            self._result["build"] = 2
        print(COLORRESET, end="")

    def _run(self):
        try:
            if self._is_python:
                cmd = ['python', self.srcpath]
            elif os.name == "nt":
                cmd = "tmp.exe"
            else:
                cmd = "./tmp"
            for i, testcase in enumerate(self._testcases):
                print("testcase " + str(i + 1) + ": ", end="")
                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
                proc.stdin.write(testcase["input"].encode())
                proc.stdin.flush()
                proc.stdout.flush()
                try:
                    proc.wait(TLE_TIME)
                    ans = proc.stdout.read().decode().replace('\r\n', '\n')
                    out = testcase["output"].replace('\r\n', '\n')
                    if out == ans:
                        self._result["result"]["AC"] += 1
                        print(GREEN + "AC" + COLORRESET)
                    else:

                        if proc.returncode == 0:
                            resultkey = "WA"
                        else:
                            resultkey = "RE"
                        self._result["result"][resultkey] += 1
                        print(YELLOW + resultkey + COLORRESET)
                        print(RED + " predicted:" + ans.rstrip('\r\n') + "\n" + " result:" + out.rstrip('\r\n') + COLORRESET)
                except:
                    self._result["result"]["TLE"] += 1
                    print(YELLOW + "TLE" + COLORRESET)
                    proc.terminate()
                    # process終了後timeoutを設けない場合、tmp.exeが削除できないことがある。
                    time.sleep(1)

        finally:
            if self._is_python is False and os.path.exists(cmd) is True:
                os.remove(cmd)

    def _show_result(self):
        """
        テスト結果を出力する
        全て正解=> AC, 実行時間オーバー=> TLE, 誤りを含む=> WA, コンパイルエラー=> CE
        """

        if (self._result["build"] == 2):
            print(RED, end="")
            print("src file is not found")
            print("please write exact path on " + CONF_FILE + " or specify path(-p)")
            print(COLORRESET, end="")
            return

        if self._result["build"] == 1:
            result = YELLOW + "CE"
        elif self._result["result"]["RE"] >= 1:
            result = YELLOW + "RE"
        elif self._result["result"]["TLE"] >= 1:
            result = YELLOW + "TLE"
        elif self._result["result"]["AC"] == len(self._testcases):
            result = GREEN + "AC"
        else:
            result = YELLOW + "WA"

        result += COLORRESET
        print("result: " + result)


class ManageTestCases:
    """テストケースの管理"""

    def __init__(self, contest_name):
        os.makedirs(TESTCASES_PATH, exist_ok=True)
        self._config = {}
        self._contest = str(contest_name)
        self._contest_folder = os.path.join(TESTCASES_PATH, self._contest)

    def register_user(self):
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

    def _update_conf(self):
        try:
            with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), CONF_FILE), "r") as f:
                while True:
                    line = f.readline().rstrip('\r\n')
                    if not line:
                        break
                    element = line.split(':')
                    self._config[element[0]] = element[1]
        except:
            print(sys.exc_info())
            print("cannot open config file.")

    def get_testcases(self, problem_name, is_login=False):
        """指定された問題名からテストケースを取得しリストを返す"""
        self._update_conf()
        # atcoder上の問題のファイル名
        test_name = self._contest + '_' + problem_name
        file_name = problem_name + ".txt"
        test_info = [{"contest": self._contest, "problem": problem_name, "testname": test_name}]
        # コンテスト名のフォルダーがなければつくる
        if not os.path.exists(self._contest_folder):
            os.mkdir(self._contest_folder)

        # サーバ負荷低減のため同一情報の取得はスクレイピングさせない
        if file_name in os.listdir(self._contest_folder):
            testcases = self._read_file(file_name)
        else:
            testcases = self._scrape_page(test_name, is_login)
            self._write_file(file_name, testcases)
        return test_info + testcases

    def add_testcases(self, problem_name):
        """取得したテストケースに独自のテストケースを追加する"""

        self._update_conf()
        testcase = {}
        print("type test input(exit by \"quit\")")
        testcase["input"] = ""
        while(1):
            line = input()
            if (line == "quit"):
                break
            testcase["input"] += line + "\n"

        print("type test output(exit by \"quit\")")
        testcase["output"] = ""
        while(1):
            line = input()
            if (line == "quit"):
                break
            testcase["output"] += line + "\n"

        file_name = problem_name + ".txt"
        if os.path.exists(self._contest_folder) and file_name in os.listdir(self._contest_folder):
            testcases = self._read_file(file_name)
        testcases.append(testcase)
        self._write_file(file_name, testcases)

    def _read_file(self, file_name):
        """ファイルを読む"""

        testcases = []
        targ_path = os.path.join(self._contest_folder, file_name)
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

    def _write_file(self, file_name, testcases):
        """ファイルを書く"""
        targ_path = os.path.join(self._contest_folder, file_name)
        with open(targ_path, "w") as f:
            for i, q in enumerate(testcases):
                f.write("[test case " + str(i) + "]\n")
                f.write("---input---\n")
                f.write(q["input"])
                f.write("---output---\n")
                f.write(q["output"])
                f.write("---fin---\n")

    def _scrape_page(self, test_name, is_login):
        session = requests.session()
        if is_login:
            # loginに必要な認証情報を取得
            self._login_page(session)

        pageAll = session.get(CONTEST_URL + self._contest + "/tasks/" + test_name)
        testcases = self._analyze_page(pageAll)
        return testcases

    def _login_page(self, session):
        """認証が必要なページにログインする"""

        res = session.get(LOGIN_URL + self._contest)
        page = BeautifulSoup(res.text, 'lxml')
        csrf_token = page.find(attrs={'name': 'csrf_token'}).get('value')
        login_info = {
            "csrf_token": csrf_token,
            "username": self._config["username"],
            "password": self._config["password"],
        }
        session.post(LOGIN_URL + self._contest, data=login_info)

    def _analyze_page(self, page_org):
        """取得した問題のページから問題部分を抽出する"""

        page = BeautifulSoup(page_org.text, 'lxml').find_all(class_="part")
        quest_list = []
        quest = {}
        for element in page:
            ele_h3 = element.findChild("h3")
            ele_pre = element.findChild("pre")
            if 'Sample' not in str(ele_h3):
                continue
            if 'Input' in str(ele_h3):
                quest = {}
                quest["input"] = str(ele_pre).lstrip("<pre>").rstrip("</pre>").replace('\r\n', '\n')
            else:
                quest["output"] = str(ele_pre).lstrip("<pre>").rstrip("</pre>").replace('\r\n', '\n')
                quest_list.append(quest)
        return quest_list


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument("contest_name", help="set contest name(ex. abc143)", type=str)
    parser.add_argument("question", help="set question name(ex. a)", type=str)
    parser.add_argument("-p", "--path", help="set path of source code", type=str)
    parser.add_argument("-a", "--addtest", help="add testcase", action="store_true")
    parser.add_argument("-i", "--init", help="set configuration", action="store_true")
    args = parser.parse_args()

    ac = ManageTestCases(args.contest_name)

    if (args.init is True):
        ac.register_user()

    if (args.addtest is True):
        ac.add_testcases(args.question)
        exit()

    testcases = ac.get_testcases(args.question, True)
    ex = ExecuteTestCases(testcases)
    if (args.path is not None):
        ex.execute(args.path)
    else:
        ex.execute()
