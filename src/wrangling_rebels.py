# wrangling rebels

import glob 
import pandas as pd
import networkx as nx
# import numpy as np
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

    print('sample number: {} \n file path {}'.format((sample_no), (filename)))
    p_info = rd.parse_public_data(filename)
    rebs_df=p_info.get_rebs_df()

    # make ships unique across samples
    rebs_df['ship_sample'] = rebs_df.apply(lambda df_x: pd.isna if pd.isna(df_x['ship']) else df_x['sample']+'_'+str(df_x['ship']),axis=1)

    # estimate ships
    relations = nx.from_pandas_edgelist(COT, source='messenger', target='cotraveller')
    ships = {rebel: shipnumber for shipnumber, ship in enumerate(nx.connected_components(relations), start=1) for rebel in ship}
    rebs_df['ship'] = rebs_df['messenger'].map(ships)
    
    print("How many rebels' ships do we fail to identify?\n", int(rebs_df['ship'].isna().sum()/1000))
    print('How many identified groups of rebels aka ships are there?\n',rebs_df.ship.nunique())
    # print('What are the groups?',rebs_df.ship.value_counts())
    
    rebs_df['ship_sample'] = rebs_df.apply(lambda df_x: pd.isna if pd.isna(df_x['ship']) else str(df_x['sample'])+'_'+str(int(df_x['ship'])),axis=1)


    public_dfs.append(rebs_df)

public_dfs = pd.concat(public_dfs)
public_dfs

