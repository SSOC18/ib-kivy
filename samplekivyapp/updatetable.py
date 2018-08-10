import rethinkdb as r
import pandas as pd
import subprocess
import threading




conn = r.connect(host='localhost', port=28015, db='readcsv')#database name inside db

subprocess.run('rethinkdb import -f /Users/raedzorkot/Desktop/pythontestodes/Workbook1.csv --format csv --table readcsv.csvfile --force', shell=True)#to repopulate the table from the csv file into db.table

