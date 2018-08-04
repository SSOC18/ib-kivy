import wx
import random
import sys
import pandas as pd
import wx.grid
import rethinkdb as r
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
        s=str(random.randint(0, 100))
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
        
        wx.CallLater(3000, self.timer)
        
    def exit(self, event):
        self.Destroy()

class PageTwo(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        
        self.timer()
    def timer(self):
        s=str(random.randint(0, 100))
        df = pd.DataFrame({'symbol': ['a','b','c'], 'position': [s,2,3]})
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
        
        wx.CallLater(3000, self.timer)
        
    def exit(self, event):
        self.Destroy()

class PageThree(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        
        self.timer()
    def timer(self):
        s=str(random.randint(0, 100))
        df = pd.DataFrame({'symbol': ['a','b','c'], 'qty': [1, -1, 0]})
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
        
        wx.CallLater(3000, self.timer)
        
    def exit(self, event):
        self.Destroy()

class PageFour(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        
        self.timer()
    def timer(self):
        conn = r.connect(host='localhost', port=28015, db='python_tutorial')
        cursor = r.table("csvfile").pluck("name", "price").run(conn)
        res = []
        for document in cursor:
            res.append(document)
        df = pd.DataFrame(res);
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
        
        wx.CallLater(3000, self.timer)
        
    def exit(self, event):
        self.Destroy()



class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="Simple Notebook Example")

        # Here we create a panel and a notebook on the panel
        p = wx.Panel(self)
        nb = wx.Notebook(p)

        # create the page windows as children of the notebook
        page1 = PageOne(nb)
        page2 = PageTwo(nb)
        page3 = PageThree(nb)
        page4 = PageFour(nb)

        # add the pages to the notebook with the label to show on the tab
        nb.AddPage(page1, "Prices")
        nb.AddPage(page2, "Portfolio")
        nb.AddPage(page3, "Trades")
        nb.AddPage(page4, "Rethinkdb")
        # finally, put the notebook in a sizer for the panel to manage
        # the layout
        sizer = wx.BoxSizer()
        sizer.Add(nb, 1, wx.EXPAND)
        p.SetSizer(sizer)


if __name__ == "__main__":
    app = wx.App()
    MainFrame().Show()
    app.MainLoop()
