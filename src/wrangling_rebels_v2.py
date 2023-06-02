# wrangling rebels version 2
# uses truth data shipId earlier
# results in more 33321 < 30192 non-null values for closestStar
# ideal for training the model

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

    ###########################################
    ########### wrangling_rebels_v2 ###########
    ###########################################
    
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


    # get NEA of leaker and impute to ship members USING TRUTH ID
    NEA=p_info.get_nea() # df of messenger's closest star
    NEA = NEA.merge(rebel_id, how='left', left_on='messenger', right_on='name').drop(labels=['id','name'], axis=1)

    if NEA['shipid'].isna().sum() < 1:
        rebs_df = pd.merge(rebs_df,NEA[['t','shipid','closestStar']], how='left', on=['shipid','t'], suffixes=('', '__y'))

        if rebs_df.duplicated().astype(int).sum() > 0:
            print('Duplicates after join NEA: '), print(rebs_df.duplicated().astype(int).sum())

            rebs_df.drop_duplicates(inplace=True)

    else:
        print('\n\nNEA leakers with unidentified ships: {}\n'.format(NEA['shipid'].isna().sum()))

        rebs_df = pd.merge(rebs_df,NEA[['messenger','t','closestStar']], how='left',on=['messenger','t'], suffixes=('', '__y'))

        print('\nclosest stars first time: {}'.format(rebs_df['closestStar'].notna().sum()))

        NEA2 = NEA.loc[NEA['shipid'].notna()]
        
        if NEA2[['shipid','t','closestStar']].duplicated().sum() > 0:
            
            print('\nshipmembers duplicate NEA leaks: {}'.format(NEA2[['shipid','t','closestStar']].duplicated().sum()))
            NEA2 = NEA2[['shipid','t','closestStar']].drop_duplicates().sort_values(by=['shipid','t'])

        rebs_df = rebs_df.combine_first(rebs_df.drop('closestStar',axis=1).merge(NEA2, how='left',on=['shipid','t']))
        
        print('closest stars second time: {}\n'.format(rebs_df['closestStar'].notna().sum()))

    # get TRUTH - continued
    ## star coordinates
    star_coords = truth.get_stars()
    star_coords.columns=['closestStar_x', 'closestStar_y', 'closestStar_z', 'closestStar_nNeigh','starid']
    rebs_df = rebs_df.merge(star_coords, how='left', left_on='closestStar', right_on='starid').drop(labels='starid', axis=1)

    # get LOC of leaker and impute to ship members
    LOC=p_info.get_loc() # df of messenger's location
    rebs_df = pd.merge(rebs_df,LOC[['t','messenger','x','y','z']], how='left',on=['messenger','t'], suffixes=('', '__y'))
    
    # removed attempts to manually impute LOC to shipmembers
    # because members at t leaked slightly different positions
    # and there is no accurate way to decide what to impute

    rebs_df.drop(rebs_df.filter(regex='^.*(__x|__y)').columns, axis=1, inplace=True)


    # last touch on df cols
    rebs_df.drop(labels='msg_content', axis=1, inplace=True) # OBS ship_missing?
    rebs_df.rename(columns={'ID': 'messengerId', 'sample': 'sampleNo', 'ship': 'shipNo', 'ship_sample': 'shipId','closestStar':'closestStarId','id': 'messengerId_truth', 'shipid': 'shipId_truth','at_dest':'atDest_moving'},inplace=True)
    rebs_df = rebs_df[['sampleNo','messengerId','messengerId_truth','shipId','shipId_truth','messenger','t','msg_type','closestStarId','closestStar_x','closestStar_y','closestStar_z','closestStar_nNeigh','x','y','z','x_truth','y_truth','z_truth','atDest_moving']]
    
    dfs.append(rebs_df)

dfs = pd.concat(dfs).reset_index().drop('index', axis=1)
dfs.info()

