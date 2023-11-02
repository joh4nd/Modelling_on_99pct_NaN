# describe dfs

from wrangling_rebels_v2 import wr_2
import pandas as pd

# load data
dfs = wr_2()

# describe dataset
dfs
dfs.info()

""" Description

The dataset consists of 10 longitudinal samples from a 3 dimensional world. The 10 series are indicated by sampleNo. The 3 dims are x,y,z. The unit of analysis or observations are the rebels/messengers. The rebels are nested in ships, the cross-sectional units. From the truth data we have complete information about ship members, indicated by shipId_truth, while leaks are more uncertain and extracted using networkx.


 - sampleNo = 10 series
 - t = 1000 timeseries
 
 - messenger = names incorrectly indicates similarity of units across sampleNo.
 - messengerId = names combined with sampleNo.
 - messengerId_truth = IDs also incorrectly identical across across sampleNo.

 - shipNo = false similarities across sampleNo. A float because the used version of Pandas does not allow NaN in interger datatypes.
 - shipId = combined with sampleNo
 - shipId_truth = IDs also incorrectly conveying similarity across sampleNo.

 
"""

# messenger/rebel variables
dfs.messenger.unique() # Ane, Ariel, Barb... Ariel in sample 0001 is not Ariel in sample 0002.
dfs.messengerId.unique() # combined with sampleNo e.g. Ane_0001
dfs.messengerId_truth.unique() # RebelID_00001-35

# ship variables
dfs.shipNo.unique() # 1.0-6.0 + nan; bear false impression of similarity across sampleNo
dfs.shipId.unique() # combined with sample no e.g. 4_001
dfs.shipId_truth.unique() # ShipID_00001-5
