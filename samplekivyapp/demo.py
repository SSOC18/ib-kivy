#!/usr/bin/env python
# -*- encoding: utf-8

from __future__ import absolute_import, division, print_function

"""
If you are getting wx related import errors when running in a virtualenv:
Either make sure that the virtualenv has been created using
`virtualenv --system-site-packages venv` or manually add the wx library
path (e.g. /usr/lib/python2.7/dist-packages/wx-2.8-gtk2-unicode) to the
python path.
"""

import datetime
import pandas as pd
import numpy as np
import dfgui

df1 = pd.DataFrame({'symbol': ['a','b','c'], 'close': [100, 120, 90]})
df2= pd.DataFrame({'symbol': ['a','b','c'], 'position': [1,2,3]})
df3 = pd.DataFrame({'symbol': ['a','b','c'], 'qty': [1, -1, 0]})

dfgui.show(df1, df2, df3)
