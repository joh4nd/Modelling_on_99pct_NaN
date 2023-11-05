# multiple imputation

from wrangling_rebels_v3 import wr
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder

# from rpy2.robjects.packages import importr # guidelines: https://github.com/joh4nd/amelia-rpy2
# from rpy2.robjects import r
# from rpy2.robjects import pandas2ri 

# load data
dfs = wr() # to understand dfs read describe_dfs.py
dfs_MI = dfs.loc[:, ~dfs.columns.isin(['messengerId_truth','shipNo','messenger'])].copy() # deselect variables expected not to be useful by MI in presence of similar variables with more unique values better preventing falsely calculated identities.
# df[df.columns[~df.columns.isin(['b'])]]

# convert categorical values into numeric, required by MI. Amelia understands nominal variables
cols_to_cat = ['sampleNo','messengerId','shipId','shipId_truth','msg_type','closestStarId']
dfs_MI[cols_to_cat] = dfs_MI[cols_to_cat].astype('category').apply(lambda x_col: x_col.cat.codes).replace(-1,np.nan)
print('cat nulls before conversion:\n\n', dfs[cols_to_cat].isna().sum(),'\n\n','cat nulls after conversion:\n\n',dfs_MI[cols_to_cat].isna().sum(),sep="")

# save to csv for R processes (before handled through rpy2)
dfs_MI.to_csv('../data/dfs_MI.csv', index=False)


# # run R instance to use Amelia
# rutils = importr('utils')
# rhelp_where = rutils.help_search('help')

# Amelia = importr('Amelia')
# dir(Amelia)
# # Amelia.
