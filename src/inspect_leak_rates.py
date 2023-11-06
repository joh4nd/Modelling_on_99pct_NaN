# inspect leak rates

############# background on leak rate independence of time/position (outcomes xyz) #############
#region 

# What type of leaks are most common?
## - when controlling for the number of leaker/messenger types?

# Are public message leak rates independent of time/position?
## If not, can you determine the analytical function that govern the rates?

# We said rebel movements are completely random. Is this true?

""" background: leaks and missingness

We hope to use leaks to predict positions.

If we did not know of the true positions, we might have asked, on the one hand, whether the lack of leaks meant that 'there are no positions'; that the provided information were truly 'not there'. Or, on the other hand, whether the information must have still been there, e.g. messengers/rebeles must (a) have cotravellers i.e. be on a ship (b) have (noisy) positions (c) be closer to some stars that others. It is fair to say that this is the case.

There are not that many leaks compared to the many positions (1000) we know they take. This makes true positions more difficult to predict. Estimating the positions at all times for all rebels using leaks (with missing values varying over different values of time t) makes estimates more uncertain because corresponding rows with values in true positions are dropped.

Leaking (vs. not leaking) is a rebel-level predictor rather than a ship level or draw/sample level predictor. So differences in leaks can be attributed to differences among rebels (type/flavour). This immediately suggests that variation in leaks is not 'completely random'. Instead, it may be 'random': When there is no leak, the leak is missing at random, e.g. due to known differences in rebels.

We might further argue that we do not know 1) why some rebels leak and other do not, and 2) why they leak different messages (we just know there are types). This uncertainty raises the question whether the reason for their leaks and lack of leaks could be confounded (with something else going on). In other words, is it 'missing not at random': Is some underlying factor related to the leaks determining the leaks? More generally, what (other than the individual rebel) determines whether information is leaked or not? And is the variation in leaks (and missing leaks/values) related to true space-time positions (that we want to predict, using leaks)?

If leak rates are related to, and really caused by rather than resulting in, what we try to predict--i.e. rebel-level xyz at t--then the model will be biased. That is, depending on what values are dropped this may also introduce bias and inconsistent estimates (not only uncertainty and inefficient estimates). Bias increases if the missingness of leaked positions is a result of the true positions. The slope coefficient is going to be too steep or too flat depending on what values of x,y,z are causing drops in observations (leaks and thus true positions).

We actually have all the data in the outcome; missingness is in the predictors. This should be less severe, meaning that bias is less of a problem. However, because so much data is missing in the predictors, the estimates are going to be very inefficient, all else being equal. This may mean that there is no other way around than finding a way to overcome missing values. And this will raise the concerns of how to compute unbiased and yet efficient estimates.

In any event, the ultimate task is for a training model with no missing true positions to be tested on the test sample where all true positions are missing, in order to predict those positions. In this case, it is the sample/draw that explains why the data are missing. But the predictors we otherwise know of do not help explain why any true positions are missing. Except that the sampleNo of the training sample (which we don't observe; it is arbitrary) explains the missingness. Here it is the training of the model on corresponding (aka training) data that can help. And the hopeful assumption is that the training and test data come from the same population, such that the difference between training and test data--that they are different draws from the same population, eventually indicated by sampleNo--does not imply differences in, first and foremost, what we try to predict (x,y,z,t; the true positions over time) and, secondarily, what we know about our predictors (leaks, rebels, and so on).* That is, the true information corresponding to the test data (that we aim to infer from training data) is missing completely at random. The reason we append the 10 training samples is exactly to provide more information to the training model such that it captures greater variation from the true universe, hoping that we capture some values that occur in the test data. Yet, the model still drops true positions when there are no leaks.

To circumvent this, we must use multiple imputation, which ensures unbiased and efficient estimates.

*except that it can be seenn in rebel_decode.py that grade_assignment.ipynb uses 0001_truth.txt to evaluate the performance of the model.

"""

""" Q: leak rates and outcomes/t

_Are public message leak rates independent of time/position?_

- Public leaks are the public data. Conversely, non leaks are ~missing values. Across 10 samples, there are_
  - 324.000 - ~33.000 = 293.000 missing values in the coordinates of closestStar.
  - 324.000 - ~6000 = 318.000 missing values in leaked coordinates.
  - 324.000 - ~302.000 = 22.000 missing values in ship (and some ships are not correctly identified)

  The share of missing values is about:
  - 90% missing values in closestStar
  - 98% missing values in coordinates
  - 93% missing values in closestStar

  We infer that this provides very little data to train the model, which increases uncertainty and bias.

- Public leak rates are the number of non-NaN to sum(non-NaN + NaN).

- To be independent of time/position, the leak rates must have equal probabilities across time/position. Probabilities are indicated by frequency distributions. Determiming whether leaks/missingness are independent of time/position means conditioning on time-space, i.e. four dimensions simultaneously, like the visualization provided with the task. The plots from individual samples show quite clearly that the leaks are not scattered completely randomly in the cube across points over time. They are clearly not equally distributed. They are closely related to (obviously) the true positions of the ships. But it is difficult to tell from the visualizations whether leaks are more likely to occur at some positions during movement. Stacking the leak and truth data from all samples indicate that both movements and leaks are quite representative of the whole world x,y,z,t. But it is still difficult to be confident from visualizations that leaks are completely randomly distributed.

- We have seen that leak types (COT LOC NEA) are not equally frequent, though differences may not be 'that' large. This could be due to some underlying factor, such as position or time. This could have suggested that the leaks' possible independence of time/position may vary across leak types. But the visualizations did not strongly indicate this.


_If not, can you determine the analytical function that govern the rates?_

- Determining an analytical function of missingness/leaks also requires conditioning on time-space. A problem with predicting missingness is that the predicted point estimates do not reflect the true variation/uncertainty of the real data. As a consequence, the actual model estimating true positions will be overconfident (the task gives points for both accuracy and certainty). Multiple imputation is the state of the art method to handling missing data because it increases efficiency of models (by helping to include values that were otherwise missing) without being overconfident. This is because the final data and model is based on samples from the possible value space.

"""

""" Q: missingness

_We said rebel movements are not completely random. Is this true?_

A rebel movement may be defined as a difference in 3 dimensional space from one time to the next. The 3d visualizations strongly indicates that rebel movements are not completely random, but random in the sense that they are dependent on time and space: Positions are strongly correlated conditioned on ship, time, and space. In other words, the these variables are strongly predictive of where the ship may be: Ships move only so far from one time to the next.

Conversely, being completely random would imply that all values are equally probable. If rebel movements were completely random, we would not care to try to predict it (how could we?). We would also not care about missing values, since missing and non missing values would be equally good at predicting movements.

"""

#endregion


from wrangling_rebels import wr
from scipy.stats import skew, kurtosis
import matplotlib.pyplot as plt
from bin import rebel_decode as rd
import plotly.express as px
import glob
import re
import pandas as pd

# load data
dfs = wr()

############# inspect leaks, msg_types and compare samples #############
#region 

# What type of leaks are most common?
print('###### df info: ######\n'), print(dfs.info())

## message, type, and sample frequency distributions
print('###### Message frequencies: ######\n')
print(' leak distribution \n'), print(dfs.groupby('sampleNo')[['msg_type']].value_counts().reset_index().describe().round())
print('\n ## What type of leaks are most common? (are they?) ##')
print('\n Aggregate sum \n'), print(dfs.value_counts('msg_type'))
print('\n number of leaks over sample \n'), print(dfs.groupby('sampleNo')[['msg_type']].count().reset_index())
print('\n leak distribution over sample \n'), print(dfs.groupby('sampleNo')[['msg_type']].value_counts().reset_index().groupby('sampleNo')['count'].describe().round())
print('\n msg_type over sample \n'), print(dfs.groupby(['sampleNo','msg_type'])[['msg_type']].value_counts().reset_index().pivot(index='sampleNo',columns='msg_type',values='count'))
print('\n msg_type distribution \n'), print(dfs.groupby('sampleNo')[['msg_type']].value_counts().reset_index().groupby('msg_type')['count'].describe().round())


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

""" Interpretation

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

############# check missingness/leak independence of t and x,y,z #############
#region
# (NOT for prediction, which produces biased estimates)
for timespace in dfs[['t','x_truth','y_truth','z_truth']]:
    
    for predictor in dfs[['msg_type','shipId']]:
        missing_rate_by_dim = dfs.loc[dfs[predictor].isnull()].groupby(timespace).size() / dfs.groupby(timespace).size()
        
        """ alternatives:

        # missing_rate_by_dim = dfs.groupby(dim)['msg_type'].apply(lambda x: x.isnull().mean())
        
        # dfs['ship_missing'] = dfs['shipNo'].isna().astype(int)
        
        # dfs[['msg_type']].apply(lambda df_x: 1-(df_x.count()/df_x.size))
        
        # g_time = dfs.groupby(['t']) # 'x', 'y', 'z'
        # non_nan_time = g_time['msg_type'].count() # count non-NaN
        # total_time = g_time.size() # total number of values (including NaN) for each time
        # leak_rate_time = non_nan_time / total_time
        """
        
        missing_rate_stats = missing_rate_by_dim.describe()
        print(f'rates of {predictor} missingness over {timespace} dimension')
        print(missing_rate_stats)
        skewness = skew(missing_rate_by_dim)
        print('skewness: ', skewness)
        kurt = kurtosis(missing_rate_by_dim)
        print('kurtosis: ', kurt)

        plt.plot(missing_rate_by_dim)
        plt.xlabel(timespace)
        plt.ylabel(f'{predictor} rate of missingness')
        plt.show() 

        # sns.lineplot(missing_rate_by_dim,legend=True)

        if predictor == 'msg_type':

            for msgtype in set(dfs.loc[dfs[predictor].notnull(), predictor]):

                missing_rate_by_dim = (dfs.loc[dfs[predictor].isnull()].groupby(timespace).size() - dfs.loc[dfs[predictor] == msgtype].groupby(timespace).size()) / dfs.groupby(timespace).size() # NaN by type
            
                print(f'msg_type {msgtype} rates of missingness over dimension: {timespace}')
                missing_rate_stats = missing_rate_by_dim.describe()
                print(f'rates of missingness over dimension: {timespace}')
                print(missing_rate_stats)
                skewness = skew(missing_rate_by_dim)
                print('skewness: ', skewness)
                kurt = kurtosis(missing_rate_by_dim)
                print('kurtosis: ', kurt)

                plt.plot(missing_rate_by_dim)
                plt.xlabel(timespace)
                plt.ylabel(f'{msgtype} rate')
                plt.show() 
#endregion

############# visual inspection conditional on all dimensions x,y,z,t #############
#region

# based on truth_plotter.ipynb
truth = rd.parse_truth_data("../data/0001_truth.txt")
star_coords = truth.get_stars() # where are stars in universe
ship_movements = truth.get_moves() # where do ships (and thus messengers) move?
messages = truth.get_messages() # when and who leaks what messages?


## one sample: plot stars, ship routes, and leaks
fig = px.line_3d(ship_movements, x="x", y="y", z="z", color="id",
                 range_x=[0,1000], range_y=[0,1000], range_z=[0,1000],
                 width=1000, height=1000,
                 hover_data = ['t','x','y','z'])
fig.add_trace(px.scatter_3d(star_coords, x='x', y='y', z='z', hover_name = 'id', opacity=0.9, width = 1000, height = 1000).data[0])
fig.update_traces(marker=dict(size=1, color='grey'), line=dict(width=4))
msg_colors = ['yellow', 'black', 'cyan']
fig_msgs = px.scatter_3d(messages, x='x', y='y', z='z', hover_name = 'id',
                         hover_data = ['msg','name','t','x','y','z'],
                         range_x=[0,1000], range_y=[0,1000], range_z=[0,1000],
                         opacity=1.0, width = 1000, height = 1000, color='msg')
fig_msgs.update_traces(marker=dict(size=4))
for i, trace in enumerate(fig_msgs.data):
    fig_msgs.data[i].marker.color = msg_colors[i % len(msg_colors)]
for indData in fig_msgs.data:
    fig.add_trace(indData)
fig.update_layout(height=500, width=500)
fig.show()


## one sample, one ship and its leaks
ship_001 = ship_movements[ship_movements['id']=='ShipID_00001']
msgs_001 = messages[messages['shipid']=='ShipID_00001']
fig_traceMovement = px.scatter_3d(ship_001, x='x', y='y', z='z',
                        hover_name = 'id', opacity=0.3,
                        range_x=[0,1000], range_y=[0,1000], range_z=[0,1000],
                        width = 1000, height = 1000,
                            hover_data = ['t'])
fig_traceMovement.update_traces(line=dict(width=4, color='blueviolet'), mode = "lines")
fig_traceMsgs = px.scatter_3d(msgs_001, x='x', y='y', z='z', hover_name = 'id',
                         hover_data = ['msg','name','t','x','y','z'], opacity=1.0,
                         range_x=[0,1000], range_y=[0,1000], range_z=[0,1000],color='msg',
                         width = 1000, height = 1000)
for indData in fig_traceMsgs.data:
    fig_traceMovement.add_trace(indData)
figstars = px.scatter_3d(star_coords, x='x', y='y', z='z', hover_name = 'id', opacity=0.9, width = 1000, height = 1000)
figstars.update_traces(marker=dict(size=1, color='grey'), line=dict(width=4))
for indData in figstars.data:
    fig_traceMovement.add_trace(indData)
fig_traceMovement.update_layout(height=500, width=500)
fig_traceMovement.show()


## all samples all leaks
### get all messages and their coordinates (use loop from wrangling_rebels_v2.py)
directory_to_files="../data/*.txt"
files = glob.glob(directory_to_files) # list all files, some for rebel_decode
sample_set = sorted({re.search(r"(\d{4})_", filetype).group(1) for filetype in files if re.search(r"(\d{2})_", filetype)})
msgs_all = []
for sample_no in sample_set:
    truth = rd.parse_truth_data(f"../data/{sample_no}_truth.txt")
    messages = truth.get_messages() # when and who leaks what messages?
    # match = re.search(r"/(\d{4})[^/]*\.txt$", f"../data/{sample_no}_truth.txt")
    # sample_no = int(match.group(1))
    messages['sampleNo'] = f'_{sample_no}'
    msgs_all.append(messages)
msgs_all = pd.concat(msgs_all).reset_index().drop('index', axis=1)

### disregard samples for ease of interpretation
fig_msgs = px.scatter_3d(msgs_all, x='x', y='y', z='z', hover_name = 'id',
                         hover_data = ['sampleNo','msg','name','t','x','y','z'],
                         range_x=[0,1000], range_y=[0,1000], range_z=[0,1000],
                         opacity=.3, width = 1000, height = 1000, color='msg',
                         color_discrete_sequence=['black','tan','sienna'])
for indData in fig_msgs.data:
    fig_msgs.update_traces(marker=dict(size=3,))
fig_msgs.update_layout(height=800, width=800)
fig_msgs.show()
""" interpretation

The leaks are clearly scattered throughout the space with some clusters. This would be missing at random rather than completely at random.

"""



## all samples all ships all leaks

### groupby sample (color) and shipId (line type)
figure = px.line_3d(dfs, x='x_truth',y='y_truth',z='z_truth', 
                  color='sampleNo',
                  line_group='shipId_truth',
                  line_dash='shipId_truth',
                  hover_name='shipId_truth',
                  range_x=[0,1000], range_y=[0,1000], range_z=[0,1000],
                  width=1000, height=1000,
                  hover_data = ['sampleNo','t'])
figure.update_traces(opacity=.1)

fig_msgs = px.scatter_3d(msgs_all, x='x', y='y', z='z', hover_name = 'id',
                         hover_data = ['sampleNo','msg','name','t','x','y','z'],
                         range_x=[0,1000], range_y=[0,1000], range_z=[0,1000],
                         opacity=1.0, width = 1000, height = 1000, color='sampleNo',
                         symbol='msg', color_discrete_sequence=['darkgray', 'black', 'rosybrown','tan','sienna','saddlebrown','peru','navajowhite','lightgrey','khaki'])
symbols=['cross','circle-open','diamond-open']
symbol_map = {msg:symbol for msg, symbol in zip(set(msgs_all['msg']), symbols)}
for indData in fig_msgs.data:
    msg_value = indData['legendgroup'][-3:]
    symbol = symbol_map.get(msg_value)
    indData['marker']['symbol'] = symbol
    fig_msgs.update_traces(marker=dict(size=3,))

#### and messages to the routes of all ships in all samples
for indData in fig_msgs.data:
    figure.add_trace(indData)
figure.update_layout(height=800, width=800)
figure.show()



""" loop - delete?
# enable switching on/off all ships across samples
figure = go.Figure()

for sample in set(dfs['sampleNo']):

    fig_sample = px.line_3d(dfs.loc[dfs['sampleNo'] == sample],
                            x='x_truth',y='y_truth',z='z_truth', 
                            color='shipId_truth',
                            # line_group='shipId_truth',
                            hover_name='shipId_truth',
                            range_x=[0,1000], range_y=[0,1000], range_z=[0,1000],
                            width=1000, height=1000,
                            hover_data = ['sampleNo','t'],
                            color_discrete_sequence=)
    
    # leak_sample = 

    # for indData in leak_sample.data:
    #     figure.add_trace(indData)

    for indData in fig_sample.data:
        figure.add_trace(indData)
    
colors = px.colors.sample_colorscale("viridis", [n/(n_colors -1) for n in range(n_colors)])
df.plot(color_discrete_sequence=colors)

figure.update_layout(height=500, width=500)
figure.show() """

#endregion

############# testing rates of missingness statistically #############
#region
 
# test for differences in xyz and t over observed/missing in, respectively, LOCxyz and NEAxyz
## two groups: observed vs. missing
## little's test

from pyampute.exploration.mcar_statistical_tests import MCARTest
mt = MCARTest(method='little') # Warning: the test is not geared to account for groups, and thus 't' is interpreted not as an index or timeseries but as a value

# test across all numeric variables
print(mt.little_mcar_test(dfs[['x','y','z','x_truth','y_truth','z_truth','closestStar_x','closestStar_y','closestStar_z']])) # not missing completely at random

# test differences in real positions
print(mt.little_mcar_test(dfs[['x','y','z','x_truth','y_truth','z_truth']])) # not missing completely at random

# missing in one dim: x
print(mt.little_mcar_test(dfs[['x','x_truth']])) # missing completely at random
print(mt.little_mcar_test(dfs[['x','y','z','x_truth']])) # missing completely at random
""" graphs from earlier speaking to this
missing_rate = dfs.loc[dfs['msg_type'].isnull()].groupby('x_truth').size() / dfs.groupby('x_truth').size() # NaN by type
plt.plot(missing_rate)
plt.xlabel('x_truth')
plt.ylabel('LOC leak missing rate')
plt.show() 

missing_rate_by_x = (dfs.loc[dfs['msg_type'].isnull()].groupby('x_truth').size() - dfs.loc[dfs['msg_type'] == 'LOC'].groupby('x_truth').size()) / dfs.groupby('x_truth').size() # NaN by type
plt.plot(missing_rate_by_x)
plt.xlabel('x_truth')
plt.ylabel('x missing rate')
plt.show() 

"""
print(mt.little_mcar_test(dfs[['x','x_truth','y_truth','z_truth']])) # not missing completely at random - like 3d graphs
for sample in set(dfs['sampleNo']):
    print('x, xtruth: ',mt.little_mcar_test(dfs.loc[dfs['sampleNo'] == sample, ['x','x_truth']]))
    print('x, xtruth, ytruth, ztruth: ', mt.little_mcar_test(dfs[['x','x_truth','y_truth','z_truth']]))

# missing in one dim: y
print(mt.little_mcar_test(dfs[['y','y_truth']])) # not missing completely at random
for sample in set(dfs['sampleNo']):
    print('y, ytruth: ',mt.little_mcar_test(dfs.loc[dfs['sampleNo'] == sample, ['y','y_truth']]))

# missing in one dim: z
print(mt.little_mcar_test(dfs[['z','z_truth']])) # not missing completely at random
for sample in set(dfs['sampleNo']):
    print('z, ztruth: ',mt.little_mcar_test(dfs.loc[dfs['sampleNo'] == sample, ['z','z_truth']]))



from opg_RR.src.bin.Little_MCARtest import little_mcar_test

res = little_mcar_test(dfs[['x','y','z','x_truth','y_truth','z_truth','closestStar_x','closestStar_y','closestStar_z']]) # returns multiple p-values :-/

#endregion
