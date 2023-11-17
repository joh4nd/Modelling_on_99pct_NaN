# multiple imputation version 2

from wrangling_rebels import wr
import pandas as pd
import numpy as np


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
    

def impute(imputation_method="Amelia", df=df):

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










# concatenate

# # split data into training and test
# test_samples = random.sample(df['Sample'].unique().tolist(), 2) # draw 2 random  samples
# train_data = df[~df['Sample'].isin(test_samples)]
# test_data = df[df['Sample'].isin(test_samples)]


