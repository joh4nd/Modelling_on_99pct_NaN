# inspect leak rates
# What type of leaks are most common?
# Are public message leak rates independent of time/position?
from wrangling_rebels_v2 import wr_2

dfs = wr_2()

#region: inspect and compare samples
# What type of leaks are most common?
print('###### df info: ######\n'), print(dfs.info())

## message, type, and sample frequency distributions
print('###### Message frequencies: ######\n')
print(' Cross msgtype & sample distribution \n'), print(dfs.groupby('sampleNo')[['msg_type']].value_counts().reset_index().describe().round())
print('\n ## What type of leaks are most common? (are they?) ##')
print('\n Aggregate sum \n'), print(dfs.value_counts('msg_type'))
print('\n distribution over sample \n'), print(dfs.groupby(['sampleNo','msg_type'])[['msg_type']].value_counts().reset_index().pivot(index='sampleNo',columns='msg_type',values='count'))
print('\n top messages over sample \n'), print(dfs.groupby('sampleNo')[['msg_type']].describe().round())
print('\n msgtype distribution \n'), print(dfs.groupby('sampleNo')[['msg_type']].value_counts().reset_index().groupby('msg_type')['count'].describe().round())

## number of messengers with respect to message type and sample
print('###### Messager frequencies: ######\n')
print('\n joint number of messengers \n'), print(dfs['messenger'].nunique())
print('\n number of messengers per sample \n'), print(dfs.groupby('sampleNo')['messenger'].nunique())
print('\n number of messengers per msgtype \n'), print(dfs.groupby(['msg_type'])['messenger'].nunique())
print('\n number of messengers per msgtype distribution over sample \n'), print(dfs.groupby(['sampleNo','msg_type'])[['messenger']].nunique().reset_index().pivot(index='sampleNo',columns='msg_type',values='messenger'))
print('\n messenger distribution across sample and msg_type \n'), print(dfs.groupby(['sampleNo','msg_type'])[['messenger']].nunique().reset_index().describe().round())
print('\n messenger distribution across sample  \n'), print(dfs.groupby(['sampleNo'])[['messenger']].nunique().reset_index().describe().round())
print('\n messenger distribution across msg_type  \n'), print(dfs.groupby(['msg_type'])[['messenger']].nunique().reset_index().describe().round())
print('\n messenger distribution by sample and msg_type \n'), print(dfs.groupby(['sampleNo','msg_type'])[['messenger']].nunique().reset_index().pivot(index='sampleNo',columns='msg_type',values='messenger').describe().round())

"""

The total number of rebel names is 46.
The total number of rebel names in the msg_types across samples are 43, 31, and 37.
There are 32.4 rebel names per sample.
There are 40.3 rebel names pr msg_type.
There are 10.8 rebel names pr msg_type pr sample.

We infer from the numbers that
(1) messenger names may reappear across samples
(2) messenger names may change msg_type across samples

Do messenger names refer to substantially identical messengers?
Or do the names in different samples just happen to be the same?

We don't know. Therefore, we have generated unique IDs per sample,
while keeping variables with names that appear to refer to the same
units across samples (e.g. John in sample 1 is John in sample 2).

* The ratio of messengers per msg_type to number of msg_type...
... says something about leak rates and there dependence of 
... indvidual rebels/names.

##################################################
##### number of leaked LOC (xyz), NEA, and t #####
##### mean leaked LOC, NEA, t                #####
##################################################
"""
#endregion

#region: leak rate independence of time/position (outcomes xyz)

""" background on leaks and missingness

We hope to use leaks to predict positions. There are not that many leaks compared to the many positions (1000) we know they take. This makes it difficult to predict. Does the lack of leaks means that there are not leaks and that the provided information are truly 'not there'? Or must the information still be there, e.g. messengers/rebeles must (a) have cotravellers i.e. be on a ship (b) have noisy positions (c) be closer to some stars that others? I believe we can fairly say that this is true. Nonetheless, it is still true that leak is a rebel level predictor (not ship level). So differences in leaks can be attributed to differences among rebels (type/flavour). This immediately implies that variation in leaks is not 'completely random', but 'random': When there is no leak, the leak is missing at random, e.g. due to known differences in rebels. But we do not know why some rebels leak and other do not, and why they leak different messages. Could the reason for their leaks and lack of leaks be confounded? In other words, is it 'missing not at random': Is some underlying factor related to the leaks determining the leaks? More generally, what (other than the individual rebel) determines whether information is leaked or not? And is the variation in leaks (and missing leaks/values) related to true space-time positions (that we want to predict, using leaks)?

"""


""" leak rates and outcomes/t

Are public message leak rates independent of time/position?
If not, can you determine the analytical function that govern the rates?

- Public leaks are the public data. Conversely, non leaks are ~missing values.

- Public leak rates are the number of non-NaN to sum(non-NaN + NaN).

- To be independent of time/position, the leak rates must have equal probabilities across time/position. Probabilities are indicated by frequency distributions. Determiming whether leaks/missingness are independent of time/position means conditioning on time-space, i.e. four dimensions simultaneously, like the visualization provided with the task. The plots show quite clearly that the leaks are not scattered randomly in the cube, nor randomly across points over time. They are clearly not equally distributed. It is rather a question of how unequally distributed the frequencies are. We could go further into examining this beyond inspecting the 3d visualizations. But the provided visualizations suffice.

- We have seen that leak types (COT LOC NEA) are not equally frequent. This could be due to some underlying factor, such as position or time. This suggests that the leaks' possible independence of time/position may vary across leak types.

- Determining an analytical function of missingness/leaks also requires conditioning on time-space. A problem with predicting missingness is that the predicted point estimates do not reflect the true variation/uncertainty of the real data. As a consequence, the actual model estimating true positions will be overconfident.

"""

""" missingness

We said rebel movements are not completely random. Is this true?

A rebel movement may be defined as a difference in 3 dimensional space from one time to the next. The 3d visualizations strongly indicates that rebel movements are not completely random, but random in the sense that they are dependent on time and space: Positions are strongly correlated conditioned on ship, time, and space. In other words, the these variables are strongly predictive of where the ship may be: Ships move only so far from one time to the next. Conversely, being completely random would imply that values are equally probably. We can plot the value frequency distributions of the positions to get a sense of that, which I believe is unlikely.

If rebel movements were completely random, we would not care to try to predict it (how could we?). We would also not care about missing values, since missing and non missing values would be equally good at predicting movements. However, if we lacked observations to power the methods, then we could impute values, to gain more confidence.

"""

# from scipy.stats import skew, kurtosis
# missing_rate_by_time = df[df['A'].isnull()].groupby('time').size() / df.groupby('time').size()
# # missing_rate_by_time = data.groupby('time')['A'].apply(lambda x: x.isnull().mean())
# missing_rate_stats = missing_rate_by_time.describe()
# skewness = skew(missing_rate_by_time)
# kurt = kurtosis(missing_rate_by_time)
# print(missing_rate_stats)
# print("Skewness for Combined Draws:", skewness)
# print("Kurtosis for Combined Draws:", kurt)

# by sample
##missing_rate_by_draw = df[df['A'].isnull()].groupby(['sample_number', 'time']).size() / df.groupby(['sample_number', 'time']).size()
##missing_rate_stats_by_draw = missing_rate_by_draw.groupby('sample_number').describe()
##skewness_by_draw = missing_rate_by_draw.groupby('sample_number').apply(skew)
##kurt_by_draw = missing_rate_by_draw.groupby('sample_number').apply(kurtosis)


# from scipy.stats import spearmanr
# correlation, p_value = spearmanr(missing_rate_by_time.index, missing_rate_by_time.values)
# print("spearmans r:", correlation), print("p-value:", p_value)

# from scipy.stats import kruskal
# statistic, p_value = kruskal(missing_rate_by_time)
# print("Kruskal-Wallis Test: ", statistic), print("p-value: ", p_value)

# import statsmodels.api as sm
# dfs['leak'] = dfs['msg_type'].notna()
# manova_results = sm.multivariate.MANOVA.from_formula('t + x + y + z ~ leak', data=dfs).fit()
# print(manova_results.summary())


#endregion