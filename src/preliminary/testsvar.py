# -*- coding: utf-8 -*-
"""
Created on Mon Mar 13 20:29:56 2023

@author: Johan
"""
import pandas as pd
from io import StringIO

# find ud af hvordan public assignment dataframe skal se ud eller ser ud, evt. hvad er koden bag?
df = pd.read_csv('C:/Users/Johan/opg_RR/out/0001_public.txt',
                 header=None, engine='python',
                 sep='t=(\d+), (\w+), (\w+), (.*)')
df

df2 = pd.read_csv('C:/Users/Johan/opg_RR/out/0001_public.txt',
                 header=None, engine='python',
                 sep='(\d+), (\w+), (\w+), (.*)')
df2.columns
print(df2)

df = pd.read_csv(StringIO(txt),\
             parse_dates=[1],\
             dayfirst=True)\
             .assign(id_index= lambda x_df: x_df\
             .groupby('ID', sort=False).ngroup())\
             .set_index("id_index")\
             .rename_axis(index=None)
