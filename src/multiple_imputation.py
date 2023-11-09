# multiple imputation

from wrangling_rebels import wr
import pandas as pd
import numpy as np

# from rpy2.robjects.packages import importr # guidelines: https://github.com/joh4nd/amelia-rpy2
# from rpy2.robjects import r
# from rpy2.robjects import pandas2ri 

# import random



# load data
dfs = wr() # understand dfs, see: describe_dfs.py
dfs_MI = dfs[dfs.columns[~dfs.columns.isin(['index','messengerId_truth','shipNo','shipId','messenger','nearestStarId','nearestStar_x','nearestStar_y','nearestStar_z','nearestStar_nNeigh','msg_type'])]].copy() # deselect variables expected not to be useful by MI in presence of similar variables with more unique values better preventing falsely calculated identities. shipId, nearestStarId/x/y/z/nNeigh, msg_type are useful for ML, not MI.
# NOTE 1) should we drop all rows being NaN in msg_type (perhaps for ML)?



# convert categorical into numeric, required by MI. Amelia understands nominal variables
cols_to_cat = ['sampleNo','messengerId','shipId_truth','nearestStarId_truth']
dfs_MI[cols_to_cat] = dfs_MI[cols_to_cat].astype('category').apply(lambda x_col: x_col.cat.codes).replace(-1,np.nan)
print('cat nulls before conversion:\n\n', dfs[cols_to_cat].isna().sum(),'\n\n','cat nulls after conversion:\n\n',dfs_MI[cols_to_cat].isna().sum(),sep="")
del dfs

# save to csv for R processes (before handled through rpy2)
dfs_MI.to_csv('../data/dfs_MI.csv',index_label='index') #, index=False)


# # run R instance to use Amelia
# rutils = importr('utils')
# rhelp_where = rutils.help_search('help')

# Amelia = importr('Amelia')
# dir(Amelia)
# # Amelia.



# # split data into training and test
# test_samples = random.sample(df['Sample'].unique().tolist(), 2) # draw 2 random  samples
# train_data = df[~df['Sample'].isin(test_samples)]
# test_data = df[df['Sample'].isin(test_samples)]