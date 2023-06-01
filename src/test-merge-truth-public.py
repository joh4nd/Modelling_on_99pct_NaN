# test how to merge truth data with public data


import glob 
import pandas as pd
import networkx as nx
# import numpy as np
import bin.rebel_decode as rd



######################################
######### inspect one sample #########
######################################



# extract pandas objects
p_info = rd.parse_public_data("../data/0001_public.txt")
truth = rd.parse_truth_data("../data/0001_truth.txt")

# region: public wrangle

# estimate ships from COT and rebs_df
rebs_df=p_info.get_rebs_df()
COT=p_info.get_cot() # df of messenger's cotraveller at t
relations = nx.from_pandas_edgelist(COT, source='messenger', target='cotraveller')
ships = {rebel: shipnumber for shipnumber, ship in enumerate(nx.connected_components(relations), start=1) for rebel in ship}
rebs_df['ship'] = rebs_df['messenger'].map(ships).astype(float) #.astype(pd.Int16Dtype())
rebs_df['ship_missing'] = rebs_df['ship'].isna().astype(int) # use to check missingness independence of t/xyz; NOT for prediction, because it produces biased estimates
print("\n How many rebels' ships do we fail to identify?\n", int(rebs_df['ship'].isna().sum()/1000)) # t=1000
rebs_df['ship_sample'] = rebs_df.apply(lambda df_x: pd.isna if pd.isna(df_x['ship']) else str(df_x['ship'])+'_'+str(df_x['sample']),axis=1) # make ships unique across samples to imply/convey no cross-sample information

# get NEA of leaker and impute to ship members
NEA=p_info.get_nea() # df of messenger's closest star
NEA['ship'] = NEA['messenger'].map(ships)

if NEA['ship'].isna().sum() < 1:
    rebs_df = pd.merge(rebs_df,NEA[['t','ship','closestStar']], how='left', on=['ship','t'], suffixes=('', '_y'))

    if rebs_df.duplicated().astype(int).sum() > 0:
        print('Duplicates after join NEA: '), print(rebs_df.duplicated().astype(int).sum())

        rebs_df.drop_duplicates(inplace=True)

else:
    print('\n\nNEA leakers with unidentified ships: {}\n'.format(NEA['ship'].notna().sum()))

    rebs_df = pd.merge(rebs_df,NEA[['messenger','t','closestStar']], how='left',on=['messenger','t'], suffixes=('', '_y'))

    print('\nclosest stars first time: {}'.format(rebs_df['closestStar'].notna().sum()))

    NEA = NEA.loc[NEA['ship'].notna().astype('int')]
    rebs_df = rebs_df.combine_first(rebs_df.drop('closestStar',axis=1).merge(NEA, how='left',on=['ship','t']))
    
    print('closest stars second time: {}\n'.format(rebs_df['closestStar'].notna().sum()))

    if rebs_df.duplicated().astype(int).sum() > 0:
        print('Duplicates after join NEA: '), print(rebs_df.duplicated().astype(int).sum())

        rebs_df.drop_duplicates(inplace=True)

rebs_df.drop(rebs_df.filter(regex='^.*(_x|_y)').columns, axis=1, inplace=True)


# # get LOC of leaker and impute to ship members
# LOC=p_info.get_loc() # df of messenger's location
# LOC['ship'] = LOC['messenger'].map(ships)

# if LOC['ship'].isna().sum() < 1:

#     rebs_df = pd.merge(rebs_df,LOC[['ship','t','x','y','z']], how='left',on=['ship','t'], suffixes=('', '_y'))
    
#     if rebs_df.duplicated().astype(int).sum() > 0:
#         print('Duplicates after join LOC: '), print(rebs_df.duplicated().astype(int).sum())

#         rebs_df.drop_duplicates(inplace=True)

# else:
#     print('\n\nLOC leakers with unidentified ships: {}\n'.format(LOC['ship'].notna().sum()))
    
#     rebs_df = pd.merge(rebs_df,LOC[['t','messenger','x','y','z']], how='left',on=['messenger','t'], suffixes=('', '_y'))

#     print('\nx positions first time: {}'.format(rebs_df['x'].notna().sum()))
#     print('y positions first time: {}'.format(rebs_df['y'].notna().sum()))
#     print('z positions first time: {}\n'.format(rebs_df['z'].notna().sum()))

#     LOC = LOC.loc[LOC['ship'].notna().astype('int')]
#     rebs_df = rebs_df.combine_first(rebs_df.drop(['x','y','z'],axis=1).merge(LOC, how='left',on=['ship','t']))
    
#     print('\nx positions second time: {}'.format(rebs_df['x'].notna().sum()))
#     print('y positions second time: {}'.format(rebs_df['y'].notna().sum()))
#     print('z positions second time: {}\n'.format(rebs_df['z'].notna().sum()))
    
#     if rebs_df.duplicated().astype(int).sum() > 0:
#         print('Duplicates after join LOC: '), print(rebs_df.duplicated().astype(int).sum())

#         rebs_df.drop_duplicates(inplace=True)

rebs_df.drop(rebs_df.filter(regex='^.*(_x|_y)').columns, axis=1, inplace=True)

# endregion

rebs_df.info()

###############################################

# get TRUTH to prepare multiple imputation

## messages (LOC,NEA,COT leaks in one df)
messages = truth.get_messages()
""" plan

1. get shipid to rebs_df

1.1. show ship and shipid by rebel name

1.2. join on name

2. check for NaN in shipid: are any rebel names missing shipid?

"""
rebel_id = messages[['id','name','shipid']].drop_duplicates(subset=['id','name','shipid']).sort_values(by='name')
rebs_df = rebs_df.merge(rebel_id, how='left', left_on='messenger', right_on='name').drop(labels='name', axis=1)

if rebs_df['shipid'].isna().sum() > 0:
    print('\nrebels lacking shipid: {}\n'.format(rebs_df['shipid'].isna().sum()))





## ship movements
ship_movements = truth.get_moves()
# ship_movements['ship'] = ship_movements['id'].apply(lambda id_x: int(id_x.split('_')[1])) # split, tak the last item, to int
ship_movements.columns=['t', 'x_truth', 'y_truth', 'z_truth','shipid','at_dest']
""" plan

1. join t, shipid to get true positions and at_dest

## irrelevant:
# 1. convert id to comparable key for join
# 1.1.1. if ships are identified completely
# 1.1.2. else it may be tricky to join on ship==id
# 1.2. write function to check leak positions correspondebce with truth positions
# 1.2.1. if they correpond somewhat, join
# 1.2.2. if they do not correponds, change the ship integers, and run check again until match

"""
rebs_df = rebs_df.merge(ship_movements, how='left', on=['t','shipid'], suffixes=('', '_y'))
rebs_df.drop(rebs_df.filter(regex='^.*(_y)').columns, axis=1, inplace=True)






## star coordinates
star_coords = truth.get_stars()
star_coords.columns=['x_star', 'y_star', 'z_star', 'nNeigh','starid']
""" plan

1. get (a) star positions of leaked nearest stars and (b) nNeigh, by joining on star_id

- (redundant?) perhaps use information about predicted positions to predict the positions of stars
that, via information about the ship, can in turn be used to predict more positions

"""
rebs_df = rebs_df.merge(star_coords, how='left', left_on='closestStar', right_on='starid').drop(labels='starid', axis=1)

