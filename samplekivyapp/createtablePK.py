import rethinkdb as r
import pandas as pd
import subprocess
import threading



conn = r.connect(host='localhost', port=28015, db='readcsv')#database name inside db
r.db('readcsv').table_create('csvfile', primary_key='name').run(conn)
