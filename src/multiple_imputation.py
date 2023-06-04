# multiple imputation

from wrangling_rebels_v2 import wr_2

dfs = wr_2()

# load Amelia for handling missing data
from rpy2.robjects.packages import importr
from rpy2.robjects import r
from rpy2.robjects import pandas2ri 


Amelia = importr('Amelia')
dir(Amelia)
Amelia.
