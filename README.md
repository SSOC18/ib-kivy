# ib-kivy
[kivy](https://kivy.org/) GUI application wrapping Interactive Brokers' [TWS API](http://interactivebrokers.github.io/tws-api/) to show market data


## Requirements
Software
- Interactive Brokers Trader Working Station (IB TWS)
- TWS API
- python 3
- kivy

Hardware
- anything larger than AWS EC2 t2.small

Optional tools
- pipenv
- git


## Installation
- To install Rethinkdb go to [Install Rethinkdb](https://www.rethinkdb.com/docs/install/) and choose your operating system, then to [Installing the Python driver](https://rethinkdb.com/docs/install-drivers/python/) for installing the python driver.
- To launch Rethinkdb simply type `rethinkdb` in terminal for mac os and linux or type `C:\Users\Slava\RethinkDB\>rethinkdb.exe` for windows.
- To run the python scripts, first you need to make sure all the modules are installed and have the rethinkdb database working and running.
- To create a table and setting a primary key in a database in Rethinkdb run the python script `createtablePK.py` .
- To populate the database table in Rethinkdb run the python script `updatetable.py`  and change your csv file directory and database name and table.
- To display the tables from the csv files and Rethinkdb database run the wxPython app `newapp.py` and change your csv file directory and database name and table.

Video demonstrating the app running: [video](https://youtu.be/SNbaUV1WniI)
