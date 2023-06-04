# multiple imputation

from wrangling_rebels_v2 import wr_2
from rpy2.robjects.packages import importr # guidelines: https://github.com/joh4nd/amelia-rpy2
from rpy2.robjects import r
from rpy2.robjects import pandas2ri 

dfs = wr_2()

Amelia = importr('Amelia')
dir(Amelia)
# Amelia.
