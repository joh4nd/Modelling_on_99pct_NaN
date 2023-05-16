# wrangling rebels

import glob 
import pandas as pd
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
public_list = sorted(glob.glob("../data/00??_public.txt")) # list files for rebel_decode
public_dfs = [] # list of df's for concatenation at loop end

for sample_no, filename in enumerate(public_list, start=1):

    print('Sample number: {} \nFile path: "{}"'.format((sample_no), (filename)))
    
    # extract pandas objects
    p_info = rd.parse_public_data(filename)
    COT=p_info.get_cot() # df of messenger's cotraveller at t
    rebs_df=p_info.get_rebs_df()

    # estimate ships
    relations = nx.from_pandas_edgelist(COT, source='messenger', target='cotraveller')
    ships = {rebel: shipnumber for shipnumber, ship in enumerate(nx.connected_components(relations), start=1) for rebel in ship}
    rebs_df['ship'] = rebs_df['messenger'].map(ships).astype(float).astype(pd.Int16Dtype())
    print("\n How many rebels' ships do we fail to identify?\n", int(rebs_df['ship'].isna().sum()/1000))
    print('\n How many identified groups of rebels aka ships are there?\n',rebs_df.ship.nunique())
    # print('What are the groups?',rebs_df.ship.value_counts())
    
    ## make ships unique across samples to imply/convey no cross-sample information
    rebs_df['ship_sample'] = rebs_df.apply(lambda df_x: pd.isna if pd.isna(df_x['ship']) else str(df_x['ship'])+'_'+str(df_x['sample']),axis=1)

    # inspect
    print('Print df info: \n')
    print(rebs_df.info())
    print('\n What type of leaks are most common? (are they?)')
    print(rebs_df.value_counts('msg_type'), '\n')
    print('Frequency by type: \n', rebs_df.groupby(['msg_type'])['messenger'].nunique())

    public_dfs.append(rebs_df)

public_dfs = pd.concat(public_dfs)
public_dfs


# inspect
print(public_dfs.info())
print(public_dfs.value_counts('msg_type'))
print(public_dfs.groupby(['msg_type'])['messenger'].nunique())
print(public_dfs['ship'].isna().sum()/1000)
print(public_dfs.ship.nunique())
print(public_dfs.value_counts('ship'))
print(public_dfs.value_counts('ship_sample'))


