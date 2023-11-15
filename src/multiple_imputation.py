# multiple imputation

from wrangling_rebels import wr
import pandas as pd
import numpy as np



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
print(dfs_MI.columns)



############################################################3

# setup Amelia in python
from rpy2.robjects.packages import importr # guidelines: https://github.com/joh4nd/amelia-rpy2
from rpy2.robjects import r
from rpy2.robjects import pandas2ri 

# https://rpy2.github.io/doc/latest/html/pandas.html
# # run R instance to use Amelia
# rutils = importr('utils')
# rhelp_where = rutils.help_search('help')

# Amelia = importr('Amelia')
# dir(Amelia)
# # Amelia.



class MultipleImputer:

    def __init__(self, imputation_method="Amelia"):
        """imputation_method can be "Amelia" or "mice"."""
        self.imputation_method = imputation_method

    def impute_data(self, preprocessed_df):
        if self.imputation_method == "Amelia":
            return self.amelia_imputation(preprocessed_df)
        elif self.imputation_method == "mice":
            return self.mice_imputation(preprocessed_df)
        else:
            raise ValueError(f"Invalid imputation method: {self.imputation_method}")
    
    def amelia_imputation(self, preprocessed_df):
        """Amelia runs through rpy2"""

        r_dataframe = pandas2ri.py2ri(preprocessed_df)

        r_script = """
        
        pacman::p_load("Amelia", "dplyr")

        # convert Pandas dataframe to R dataframe through rpy2
        rebels <- read.csv("./repos/opg_RR/data/dfs_MI.csv")

        # run
        MI <- amelia(x = rebels1,
            m = 5,
            p2s = 1,
            idvars = c("index","sampleNo"),
            noms = c("messengerId","nearestStarId_truth"),
            ords = "atDest_moving",
            ts = "t",
            cs = "shipId_truth",
            empri = 0.05 * nrow(rebels1),
            polytime = 2,
            intercs = TRUE,
            bounds = matrix(c(11,0,1000, 12,0,1000, 13,0,1000), nrow = 3, ncol = 3, byrow = TRUE),
            parallel = 'multicore',
            ncpus = 8) 

        # diagnostics

        # simulation to draw samples of m imputated datasets, to be combined in one final dataset
        # NOTE this may alternatively be done using numpy random functions
        

        """
        
        imputed_data = robjects.r(r_script)

        imputed_df = pandas2ri.ri2py_dataframe(imputed_data)

        return imputed_data

    def mice_imputation(self, preprocessed_df):
        """placeholder for mice implementation"""
        # imp = mice(preprocessed_df)
        # imputed_data = imp.complete()
        # return imputed_data
        pass








# use data pipeline class to concatenate

# # split data into training and test
# test_samples = random.sample(df['Sample'].unique().tolist(), 2) # draw 2 random  samples
# train_data = df[~df['Sample'].isin(test_samples)]
# test_data = df[df['Sample'].isin(test_samples)]
