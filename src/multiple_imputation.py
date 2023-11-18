# multiple imputation version 2

## setup rpy2
# import rpy2
# print(rpy2.situation)
# base = importr('base')
# print(base._libPaths())
# print(base._Library)
# print(base._Library_site)
# robjects.r.getwd()

# setup R in python
# import rpy2.robjects as ro # for writing embedded R code
# from rpy2.robjects import pandas2ri as p2r
# from rpy2.robjects import r

# setup Amelia
# from rpy2.robjects.packages import isinstalled
# packnames = ('Amelia', 'dplyr')
from rpy2.robjects.vectors import StrVector
# names_to_install = [x for x in packnames if not isinstalled(x)]
from rpy2.robjects.packages import importr # packs to python objects
Amelia = importr('Amelia')
# dir(Amelia)

# utils = importr('utils')
# utils.chooseCRANmirror(ind=1) # select the first mirror in the list for R packages
# if len(names_to_install) > 0:
#     utils.install_packages(StrVector(names_to_install))


# load data
import data_pipeline as dp
import numpy as np
dfs_MI = dp.runner(m=1)

# # inspect conversion
# p2r.activate()
# rdf = p2r.py2rpy(dfs_MI) # index is also converted, hence one col less
# r.head(rdf)
# list(enumerate(r.colnames(rdf))) # 9-11 + 1 because R starts at 1, not 0 like python

imputed = Amelia.amelia(x = dfs_MI,
              m = 1,
              p2s = 1,
              idvars = StrVector(['row.names','sampleNo']), # StrVector(['index', 'sampleNo']) # rownames = 'index'
              noms = StrVector(["messengerId","nearestStarId_truth"]),
              ords = "atDest_moving",
              ts = "t",
              cs = "shipId_truth",
              empri = 0.05 * len(dfs_MI),
              polytime = 3,
              splinetime = 9,
              intercs = True,
              bounds = np.array([[10, 0, 1000], [11, 0, 1000], [12, 0, 1000]]),
              parallel = 'multicore',
              ncpus = 8)



"""
def impute(df=dfs_MI, m=1, parallel='multicore', ncpus=8):

    # diagnostics

    # simulation to draw samples of m imputated datasets, to be combined in one final dataset
    # NOTE this may alternatively be done using numpy random functions

    return imputed_data
"""


# concatenate

