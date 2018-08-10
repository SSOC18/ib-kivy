import wx
import random
import sys
import pandas as pd
import wx.grid
import rethinkdb as r
import threading
EVEN_ROW_COLOUR = '#CCE6FF'
GRID_LINE_COLOUR = '#ccc'

class DataTable(wx.grid.GridTableBase):
    def __init__(self, data=None):
        wx.grid.GridTableBase.__init__(self)
        self.headerRows = 1
        if data is None:
            data = pd.DataFrame()
        self.data = data

    def GetNumberRows(self):
        return len(self.data)

    def GetNumberCols(self):
        return len(self.data.columns) + 1

    def GetValue(self, row, col):
        if col == 0:
            return self.data.index[row]
        return self.data.iloc[row, col - 1]

    def SetValue(self, row, col, value):
        self.data.iloc[row, col - 1] = value

    def GetColLabelValue(self, col):
        if col == 0:
            if self.data.index.name is None:
                return 'Index'
            else:
                return self.data.index.name
        return str(self.data.columns[col - 1])

    def GetTypeName(self, row, col):
        return wx.grid.GRID_VALUE_STRING

    def GetAttr(self, row, col, prop):
        attr = wx.grid.GridCellAttr()
        if row % 2 == 1:
            attr.SetBackgroundColour(EVEN_ROW_COLOUR)
        return attr


    
class PageOne(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        
        self.timer()
    def timer(self):
        df = pd.read_csv("/Users/raedzorkot/Desktop/pythontestodes/Workbook1.csv")
        table = DataTable(df)

        grid = wx.grid.Grid(self, -1)
        grid.SetTable(table, takeOwnership=True)
        grid.AutoSizeColumns()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(grid, 1, wx.EXPAND)
        self.SetSizer(sizer)

        self.Bind(wx.EVT_CLOSE, self.exit)
        self.Layout()
        self.Show()
        
        wx.CallLater(5000, self.timer)
        
    def exit(self, event):
        self.Destroy()

class PageTwo(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        
        self.timer()
    def timer(self):
        df = pd.read_csv("/Users/raedzorkot/Desktop/pythontestodes/Workbook2.csv")
        table = DataTable(df)
        
        grid = wx.grid.Grid(self, -1)
        grid.SetTable(table, takeOwnership=True)
        grid.AutoSizeColumns()
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(grid, 1, wx.EXPAND)
        self.SetSizer(sizer)
        
        self.Bind(wx.EVT_CLOSE, self.exit)
        self.Layout()
        self.Show()
        
        wx.CallLater(5000, self.timer)

        
    def exit(self, event):
        self.Destroy()

class PageThree(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        
        self.timer()
    def timer(self):
        df = pd.read_csv("/Users/raedzorkot/Desktop/pythontestodes/Workbook3.csv")
        table = DataTable(df)
        
        grid = wx.grid.Grid(self, -1)
        grid.SetTable(table, takeOwnership=True)
        grid.AutoSizeColumns()
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(grid, 1, wx.EXPAND)
        self.SetSizer(sizer)
        
        self.Bind(wx.EVT_CLOSE, self.exit)
        self.Layout()
        self.Show()
        
        wx.CallLater(5000, self.timer)
        
    def exit(self, event):
        self.Destroy()

class PageFour(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.timer()
        self.timer1()
    def timer(self):
        self.conn = r.connect(host='localhost', port=28015, db='readcsv')
        cursor = r.table("csvfile").pluck("name", "price").run(self.conn)
        res = []
        for document in cursor:
            res.append(document)
        df = pd.DataFrame(res);
        self.table = DataTable(df)
        
        self.grid = wx.grid.Grid(self, -1)
        self.grid.SetTable(self.table, takeOwnership=True)
        self.grid.AutoSizeColumns()
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.grid, 1, wx.EXPAND)
        self.SetSizer(sizer)
        
        self.Bind(wx.EVT_CLOSE, self.exit)
        self.Layout()
        self.Show()
        
        

    def timer1(self):
        
        feed = r.table('csvfile').pluck("name", "price").changes().pluck("new_val").run(self.conn)
        
        self.res1 = []
        def x():
            i=0
            
            for row in feed:

                self.res1=[]
                cursor = r.table("csvfile").pluck("name", "price").run(self.conn)
                for document in cursor:
                    self.res1.append(document)
                df = pd.DataFrame(self.res1)
                self.table = DataTable(df)
                self.grid = wx.grid.Grid(self, -1)
                self.grid.SetTable(self.table, takeOwnership=True)
                self.grid.AutoSizeColumns()

                sizer = wx.BoxSizer(wx.VERTICAL)
                sizer.Add(self.grid, 1, wx.EXPAND)
                self.SetSizer(sizer)
                self.Bind(wx.EVT_CLOSE, self.exit)
                self.Layout()
                self.Show()
        
            
            return 1
        threading.Thread(target=x).start()
    

        
    def exit(self, event):
        self.Destroy()



class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="Read and Refresh every 5 seconds")

        
        p = wx.Panel(self)
        nb = wx.Notebook(p)

        
        page1 = PageOne(nb)
        page2 = PageTwo(nb)
        page3 = PageThree(nb)
        page4 = PageFour(nb)

        
        nb.AddPage(page1, "Prices")
        nb.AddPage(page2, "Portfolio")
        nb.AddPage(page3, "Trades")
        nb.AddPage(page4, "Rethinkdb")

    
        sizer = wx.BoxSizer()
        sizer.Add(nb, 1, wx.EXPAND)
        p.SetSizer(sizer)


if __name__ == "__main__":
    app = wx.App()
    MainFrame().Show()
    app.MainLoop()
