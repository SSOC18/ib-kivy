import rethinkdb as r
import pandas as pd
import subprocess
import threading


def insert():
    threading.Timer(5.0, insert).start()
    conn = r.connect(host='localhost', port=28015, db='python_tutorial')
    r.table("csvfile").delete().run(conn)
    subprocess.run('rethinkdb import -f /Users/raedzorkot/Desktop/pythontestodes/Workbook1.csv --format csv --table python_tutorial.csvfile --force', shell=True)
    

insert()

