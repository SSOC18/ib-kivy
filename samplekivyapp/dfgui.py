#!/usr/bin/env python
# -*- encoding: utf-8

from __future__ import absolute_import, division, print_function

try:
    import wx
except ImportError:
    import sys
    sys.path += [
        "/usr/lib/python2.7/dist-packages/wx-2.8-gtk2-unicode",
        "/usr/lib/python2.7/dist-packages"
    ]
    import wx

import matplotlib
matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure
from bisect import bisect
import rethinkdb as r
import numpy as np
import pandas as pd
import random
# unused import required to allow 'eval' of date filters
import datetime
from datetime import date

# try to get nicer plotting styles
try:
    import seaborn
    seaborn.set()
except ImportError:
    try:
        from matplotlib import pyplot as plt
        plt.style.use('ggplot')
    except AttributeError:
        pass


class ListCtrlDataFrame(wx.ListCtrl):

    # TODO: we could do something more sophisticated to come
    # TODO: up with a reasonable column width...
    DEFAULT_COLUMN_WIDTH = 100
    TMP_SELECTION_COLUMN = 'tmp_selection_column'

    def __init__(self, parent, df, status_bar_callback):
        wx.ListCtrl.__init__(
            self, parent, -1,
            style=wx.LC_REPORT | wx.LC_VIRTUAL | wx.LC_HRULES | wx.LC_VRULES | wx.LB_MULTIPLE
        )
        self.status_bar_callback = status_bar_callback

        self.df_orig = df
        self.original_columns = self.df_orig.columns[:]
        self.current_columns = self.df_orig.columns[:]

        self.sort_by_column = None

        self._reset_mask()

        # prepare attribute for alternating colors of rows
        self.attr_light_blue = wx.ListItemAttr()
        self.attr_light_blue.SetBackgroundColour("#D6EBFF")

        self.Bind(wx.EVT_LIST_COL_CLICK, self._on_col_click)
        self.Bind(wx.EVT_RIGHT_DOWN, self._on_right_click)

        self.df = pd.DataFrame({})  # init empty to force initial update
        self._update_rows()
        self._update_columns(self.original_columns)

    def _reset_mask(self):
        #self.mask = [True] * self.df_orig.shape[0]
        self.mask = pd.Series([True] * self.df_orig.shape[0], index=self.df_orig.index)

    def _update_columns(self, columns):
        self.ClearAll()
        for i, col in enumerate(columns):
            self.InsertColumn(i, col)
            self.SetColumnWidth(i, self.DEFAULT_COLUMN_WIDTH)
        # Note that we have to reset the count as well because ClearAll()
        # not only deletes columns but also the count...
        self.SetItemCount(len(self.df))

    def set_columns(self, columns_to_use):
        """
        External interface to set the column projections.
        """
        self.current_columns = columns_to_use
        self._update_rows()
        self._update_columns(columns_to_use)

    def _update_rows(self):
        old_len = len(self.df)
        self.df = self.df_orig.loc[self.mask.values, self.current_columns]
        new_len = len(self.df)
        if old_len != new_len:
            self.SetItemCount(new_len)
            self.status_bar_callback(0, "Number of rows: {}".format(new_len))

    def apply_filter(self, conditions):
        """
        External interface to set a filter.
        """
        old_mask = self.mask.copy()

        if len(conditions) == 0:
            self._reset_mask()

        else:
            self._reset_mask()  # set all to True for destructive conjunction

            no_error = True
            for column, condition in conditions:
                if condition.strip() == '':
                    continue
                condition = condition.replace("_", "self.df_orig['{}']".format(column))
                print("Evaluating condition:", condition)
                try:
                    tmp_mask = eval(condition)
                    if isinstance(tmp_mask, pd.Series) and tmp_mask.dtype == np.bool:
                        self.mask &= tmp_mask
                except Exception as e:
                    print("Failed with:", e)
                    no_error = False
                    self.status_bar_callback(
                        1,
                        "Evaluating '{}' failed with: {}".format(condition, e)
                    )

            if no_error:
                self.status_bar_callback(1, "")

        has_changed = any(old_mask != self.mask)
        if has_changed:
            self._update_rows()

        return len(self.df), has_changed

    def get_selected_items(self):
        """
        Gets the selected items for the list control.
        Selection is returned as a list of selected indices,
        low to high.
        """
        selection = []
        current = -1    # start at -1 to get the first selected item
        while True:
            next = self.GetNextItem(current, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
            if next == -1:
                return selection
            else:
                selection.append(next)
                current = next

    def get_filtered_df(self):
        return self.df_orig.loc[self.mask, :]

    def _on_col_click(self, event):
        """
        Sort data frame by selected column.
        """
        # get currently selected items
        selected = self.get_selected_items()

        # append a temporary column to store the currently selected items
        self.df[self.TMP_SELECTION_COLUMN] = False
        self.df.iloc[selected, -1] = True

        # get column name to use for sorting
        col = event.GetColumn()

        # determine if ascending or descending
        if self.sort_by_column is None or self.sort_by_column[0] != col:
            ascending = True
        else:
            ascending = not self.sort_by_column[1]

        # store sort column and sort direction
        self.sort_by_column = (col, ascending)

        try:
            # pandas 0.17
            self.df.sort_values(self.df.columns[col], inplace=True, ascending=ascending)
        except AttributeError:
            # pandas 0.16 compatibility
            self.df.sort(self.df.columns[col], inplace=True, ascending=ascending)

        # deselect all previously selected
        for i in selected:
            self.Select(i, on=False)

        # determine indices of selection after sorting
        selected_bool = self.df.iloc[:, -1] == True
        selected = self.df.reset_index().index[selected_bool]

        # select corresponding rows
        for i in selected:
            self.Select(i, on=True)

        # delete temporary column
        del self.df[self.TMP_SELECTION_COLUMN]

    def _on_right_click(self, event):
        """
        Copies a cell into clipboard on right click. Unfortunately,
        determining the clicked column is not straightforward. This
        appraoch is inspired by the TextEditMixin in:
        /usr/lib/python2.7/dist-packages/wx-2.8-gtk2-unicode/wx/lib/mixins/listctrl.py
        More references:
        - http://wxpython-users.1045709.n5.nabble.com/Getting-row-col-of-selected-cell-in-ListCtrl-td2360831.html
        - https://groups.google.com/forum/#!topic/wxpython-users/7BNl9TA5Y5U
        - https://groups.google.com/forum/#!topic/wxpython-users/wyayJIARG8c
        """
        if self.HitTest(event.GetPosition()) != wx.NOT_FOUND:
            x, y = event.GetPosition()
            row, flags = self.HitTest((x, y))

            col_locs = [0]
            loc = 0
            for n in range(self.GetColumnCount()):
                loc = loc + self.GetColumnWidth(n)
                col_locs.append(loc)

            scroll_pos = self.GetScrollPos(wx.HORIZONTAL)
            # this is crucial step to get the scroll pixel units
            unit_x, unit_y = self.GetMainWindow().GetScrollPixelsPerUnit()

            col = bisect(col_locs, x + scroll_pos * unit_x) - 1

            value = self.df.iloc[row, col]
            # print(row, col, scroll_pos, value)

            clipdata = wx.TextDataObject()
            clipdata.SetText(str(value))
            wx.TheClipboard.Open()
            wx.TheClipboard.SetData(clipdata)
            wx.TheClipboard.Close()

    def OnGetItemText(self, item, col):
        """
        Implements the item getter for a "virtual" ListCtrl.
        """
        value = self.df.iloc[item, col]
        # print("retrieving %d %d %s" % (item, col, value))
        return str(value)

    def OnGetItemAttr(self, item):
        """
        Implements the attribute getter for a "virtual" ListCtrl.
        """
        if item % 2 == 0:
            return self.attr_light_blue
        else:
            return None


class DataframePanel(wx.Panel):
    """
    Panel providing the main data frame table view.
    """

    def __init__(self, parent, df, status_bar_callback):
        wx.Panel.__init__(self, parent)

        self.df_list_ctrl = ListCtrlDataFrame(self, df, status_bar_callback)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.df_list_ctrl, 1, wx.ALL | wx.EXPAND | wx.GROW, 5)
        self.SetSizer(sizer)
        self.Show()



class MainFrame(wx.Frame):
    """
    The main GUI window.
    """
    def __init__(self):
        
        # finally, put the notebook in a sizer for the panel to manage
        # the layout
        
        
        self.timer()


        
        

    def timer(self):
        # Here we create a panel and a notebook on the panel
        wx.Frame.__init__(self, None, -1, "Pandas DataFrame GUI")
        self.CreateStatusBar(2, style=0)
        self.SetStatusWidths([200, -1])
        self.SetSize((800, 600))
        self.Center()


        p = wx.Panel(self)
        nb = wx.Notebook(p)
        self.nb = nb

        conn = r.connect(host='localhost', port=28015, db='python_tutorial')
        cursor = r.table("csvfile").pluck("name", "price").run(conn)
        res = []
        for document in cursor:
            res.append(document)

        
            
        s=str(random.randint(0, 100))
        df1 = pd.read_csv("/Users/raedzorkot/Desktop/pythontestodes/Workbook1.csv")
        df2= pd.DataFrame({'symbol': ['a','b','c'], 'position': [s,2,3]})
        df3 = pd.DataFrame({'symbol': ['a','b','c'], 'qty': [1, -1, 0]})
        df4 = pd.DataFrame(res);

        
        
        # create the page windows as children of the notebook
        self.page1 = DataframePanel(nb, df1, self.status_bar_callback)
        self.page2 = DataframePanel(nb, df2, self.status_bar_callback)
        self.page3 = DataframePanel(nb, df3, self.status_bar_callback)
        self.page4 = DataframePanel(nb, df4, self.status_bar_callback)
        

        # add the pages to the notebook with the label to show on the tab
        nb.AddPage(self.page1, "Prices")
        nb.AddPage(self.page2, "Portfolio")
        nb.AddPage(self.page3, "Trades")
        nb.AddPage(self.page4, "Rethinkdb")
        

        nb.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.on_tab_change)
        
        
        sizer = wx.BoxSizer()
        sizer.Add(nb, 1, wx.EXPAND)
        p.SetSizer(sizer)
        self.Layout()
        
        

        wx.CallLater(3000, self.timer)
        self.Show()
        
        

    def on_tab_change(self, event):
        #self.page2.list_box.SetFocus()
        page_to_select = event.GetSelection()
        #wx.CallAfter(self.fix_focus, page_to_select)

        event.Skip(True)

    def fix_focus(self, page_to_select):
        page = self.nb.GetPage(page_to_select)
        page.SetFocus()
        if isinstance(page, DataframePanel):
            self.page1.df_list_ctrl.SetFocus()
        elif isinstance(page, ColumnSelectionPanel):
            self.page2.list_box.SetFocus()

    def status_bar_callback(self, i, new_text):
        self.SetStatusText(new_text, i)

    


if __name__ == "__main__":
    """
    The main function to start the data frame GUI.
    """

    app = wx.App()
    frame = MainFrame()
    frame.Show()
    app.MainLoop()
