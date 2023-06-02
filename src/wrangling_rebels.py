# wrangling rebels
# the first part of the for loop must be used on the test data because it joins NEA leaks using inferred ship numbers, not shipIds from truth data (which are not accessible for testing the model)

import glob 
import re
import pandas as pd
import numpy as np
import networkx as nx
import bin.rebel_decode as rd


######################################
#########   all 10 samples   #########
######################################

""" 3. concatenation

plan: 
a) loop over files to extract, now from rebel_decode, df's and concatenate
b) use sample identifer from df I added to rebel_decode to ensure each ship has a unique ID

"""

files = glob.glob("../data/*.txt") # list all files, some for rebel_decode
sample_set = sorted({re.search(r"(\d{2})_", filetype).group(1).zfill(4) for filetype in files if re.search(r"(\d{2})_", filetype)}) # make time-series iterator
print('Number of time-series: ', len(sample_set))
dfs = [] # list of df's for concatenation at loop end

for sample_no in sample_set:
    
    print(f"Processing sample: {sample_no}")

    # extract pandas objects
    p_info = rd.parse_public_data(f"../data/{sample_no}_public.txt")
    truth = rd.parse_truth_data(f"../data/{sample_no}_truth.txt")
        
    # estimate ships from COT and rebs_df
    rebs_df=p_info.get_rebs_df()
    COT=p_info.get_cot() # df of messenger's cotraveller at t
    relations = nx.from_pandas_edgelist(COT, source='messenger', target='cotraveller')
    ships = {rebel: shipnumber for shipnumber, ship in enumerate(nx.connected_components(relations), start=1) for rebel in ship}
    rebs_df['ship'] = rebs_df['messenger'].map(ships).astype(float) #.astype(pd.Int16Dtype())
    rebs_df['ship_missing'] = rebs_df['ship'].isna().astype(int) # use to check missingness independence of t/xyz; NOT for prediction, because it produces biased estimates
    print("\n How many rebels' ships do we fail to identify?\n", int(rebs_df['ship'].isna().sum()/1000)) # t=1000
    rebs_df['ship_sample'] = rebs_df.apply(lambda df_x: np.nan if pd.isna(df_x['ship']) else str(df_x['ship'])+'_'+str(df_x['sample']),axis=1) # make ships unique across samples to imply/convey no cross-sample information

        
    # get NEA of leaker and impute to ship members
    NEA=p_info.get_nea() # df of messenger's closest star
    NEA['ship'] = NEA['messenger'].map(ships)

    if NEA['ship'].isna().sum() < 1:
        rebs_df = pd.merge(rebs_df,NEA[['t','ship','closestStar']], how='left', on=['ship','t'], suffixes=('', '__y'))

        if rebs_df.duplicated().astype(int).sum() > 0:
            print('Duplicates after join NEA: '), print(rebs_df.duplicated().astype(int).sum())

            rebs_df.drop_duplicates(inplace=True)

    else:
        print('\n\nNEA leakers with unidentified ships: {}\n'.format(NEA['ship'].isna().sum()))

        rebs_df = pd.merge(rebs_df,NEA[['messenger','t','closestStar']], how='left',on=['messenger','t'], suffixes=('', '__y'))

        print('\nclosest stars first time: {}'.format(rebs_df['closestStar'].notna().sum()))

        NEA2 = NEA.loc[NEA['ship'].notna()]
        
        if NEA2[['ship','t','closestStar']].duplicated().sum() > 0:
            
            print('\nshipmembers duplicate NEA leaks: {}'.format(NEA2[['ship','t','closestStar']].duplicated().sum()))
            NEA2 = NEA2[['ship','t','closestStar']].drop_duplicates().sort_values(by=['ship','t'])

        rebs_df = rebs_df.combine_first(rebs_df.drop('closestStar',axis=1).merge(NEA2, how='left',on=['ship','t']))
        
        print('closest stars second time: {}\n'.format(rebs_df['closestStar'].notna().sum()))


    # get LOC of leaker and impute to ship members
    LOC=p_info.get_loc() # df of messenger's location
    rebs_df = pd.merge(rebs_df,LOC[['t','messenger','x','y','z']], how='left',on=['messenger','t'], suffixes=('', '__y'))
    
    # removed attempts to manually impute LOC to shipmembers
    # because members at t leaked slightly different positions
    # and there is no accurate way to decide what to impute

    rebs_df.drop(rebs_df.filter(regex='^.*(__x|__y)').columns, axis=1, inplace=True)


    # get TRUTH to prepare multiple imputation

    ## messages (LOC,NEA,COT leaks in one df)
    messages = truth.get_messages()
    rebel_id = messages[['id','name','shipid']].drop_duplicates(subset=['id','name','shipid']).sort_values(by='name')
    rebs_df = rebs_df.merge(rebel_id, how='left', left_on='messenger', right_on='name').drop(labels='name', axis=1)

    if rebs_df['shipid'].isna().sum() > 0:
        print('\nrebels lacking shipid: {}\n'.format(rebs_df['shipid'].isna().sum()))

    ## ship movements
    ship_movements = truth.get_moves()
    ship_movements.columns=['t', 'x_truth', 'y_truth', 'z_truth','shipid','at_dest']
    ship_movements['at_dest'] = ship_movements['at_dest'].map({'true': True, 'false': False})
    rebs_df = rebs_df.merge(ship_movements, how='left', on=['t','shipid'], suffixes=('', '__y'))
    rebs_df.drop(rebs_df.filter(regex='^.*(__y)').columns, axis=1, inplace=True)

    ## star coordinates
    star_coords = truth.get_stars()
    star_coords.columns=['closestStar_x', 'closestStar_y', 'closestStar_z', 'closestStar_nNeigh','starid']
    rebs_df = rebs_df.merge(star_coords, how='left', left_on='closestStar', right_on='starid').drop(labels='starid', axis=1)

    # last touch on df cols
    rebs_df.drop(labels='msg_content', axis=1, inplace=True) # OBS ship_missing?
    rebs_df.rename(columns={'ID': 'messengerId', 'sample': 'sampleNo', 'ship': 'shipNo', 'ship_sample': 'shipId','closestStar':'closestStarId','id': 'messengerId_truth', 'shipid': 'shipId_truth','at_dest':'atDest_moving'},inplace=True)
    rebs_df = rebs_df[['sampleNo','messengerId','messengerId_truth','shipId','shipId_truth','messenger','t','msg_type','closestStarId','closestStar_x','closestStar_y','closestStar_z','closestStar_nNeigh','x','y','z','x_truth','y_truth','z_truth','atDest_moving']]
    
    dfs.append(rebs_df)

dfs = pd.concat(dfs).reset_index().drop('index', axis=1)
dfs.info()

#region: inspect and compare samples
print('###### df info: ######\n'), print(dfs.info())

## message, type, and sample frequency distributions
print('###### Message frequencies: ######\n')
print(' Cross msgtype & sample distribution \n'), print(dfs.groupby('sample')[['msg_type']].value_counts().reset_index().describe().round())
print('\n ## What type of leaks are most common? (are they?) ##')
print('\n Aggregate sum \n'), print(dfs.value_counts('msg_type'))
print('\n distribution over sample \n'), print(dfs.groupby(['sample','msg_type'])[['msg_type']].value_counts().reset_index().pivot(index='sample',columns='msg_type',values='count'))
print('\n top messages over sample \n'), print(dfs.groupby('sample')[['msg_type']].describe().round())
print('\n msgtype distribution \n'), print(dfs.groupby('sample')[['msg_type']].value_counts().reset_index().groupby('msg_type')['count'].describe().round())

## number of messengers with respect to message type and sample
print('###### Messager frequencies: ######\n')
print('\n joint number of messengers \n'), print(dfs['messenger'].nunique())
print('\n number of messengers per sample \n'), print(dfs.groupby('sample')['messenger'].nunique())
print('\n number of messengers per msgtype \n'), print(dfs.groupby(['msg_type'])['messenger'].nunique())
print('\n number of messengers per msgtype distribution over sample \n'), print(dfs.groupby(['sample','msg_type'])[['messenger']].nunique().reset_index().pivot(index='sample',columns='msg_type',values='messenger'))
print('\n messenger distribution across sample and msg_type \n'), print(dfs.groupby(['sample','msg_type'])[['messenger']].nunique().reset_index().describe().round())
print('\n messenger distribution across sample  \n'), print(dfs.groupby(['sample'])[['messenger']].nunique().reset_index().describe().round())
print('\n messenger distribution across msg_type  \n'), print(dfs.groupby(['msg_type'])[['messenger']].nunique().reset_index().describe().round())
print('\n messenger distribution by sample and msg_type \n'), print(dfs.groupby(['sample','msg_type'])[['messenger']].nunique().reset_index().pivot(index='sample',columns='msg_type',values='messenger').describe().round())

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

##############################################
######## when xyz are concatenated ###########
##############################################
# print('\n ## Are public message leak rates independent of time/position? ## \n')
# print('\n ## If not, can you determine the analytical function that govern the rates? ## \n')


