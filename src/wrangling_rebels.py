# wrangling rebels version 3
# adds calculation of the truest nearest star


import re
import pandas as pd
import numpy as np
import networkx as nx
import bin.rebel_decode as rd
from sample_set import path_to_set
from sklearn.neighbors import NearestNeighbors

def wrangle(sample_set=f'0001'):
    """
    Parses the rebel files using rebel_decode.py.

    Parameters:
    sample_set (str): the path to the rebel .txt-files.

    Returns:
    pandas.DataFrame: The wrangled, concatenated dataframes ready for multiple imputation.
    """

    # extract objects
    p_info = rd.parse_public_data(f"../data/{sample_set}_public.txt")
    truth = rd.parse_truth_data(f"../data/{sample_set}_truth.txt")
        
    # estimate ships from COT and rebs_df
    rebs_df=p_info.get_rebs_df()
    COT=p_info.get_cot() # df of messenger's cotraveller at t

    relations = nx.from_pandas_edgelist(COT, source='messenger', target='cotraveller')
    ships = {rebel: shipnumber for shipnumber, ship in enumerate(nx.connected_components(relations), start=1) for rebel in ship}
    rebs_df['ship'] = rebs_df['messenger'].map(ships).astype(float) #.astype(pd.Int16Dtype()). NOTE: Pandas 2.0 allows int to handle NaN 

    print("\n How many rebels' ships do we fail to identify?\n", int(rebs_df['ship'].isna().sum()/1000)) # t=1000
    
    rebs_df['shipId'] = rebs_df.apply(lambda df_x: np.nan if pd.isna(df_x['ship']) else str(int(df_x['ship']))+df_x['sampleNo'],axis=1) # use sample identifer from df I added to rebel_decode to ensure each ship has a unique ID. Makes ships unique across samples to imply no cross-sample information. NOTE: Pandas 2.0 allows int to handle NaN. see perhaps pd.na
    
    #region: get TRUTH for multiple imputation

    ## messages (LOC,NEA,COT leaks in one df)
    messages = truth.get_messages()
    rebel_id = messages[['id','name','shipid']].drop_duplicates(subset=['id','name','shipid']).sort_values(by='name')
    rebs_df = rebs_df.merge(rebel_id, how='left', left_on='messenger', right_on='name').drop(labels='name', axis=1)

    if rebs_df['shipid'].isna().sum() > 0:
        print('\nrebels lacking shipid: {}\n'.format(rebs_df['shipid'].isna().sum()))

    ## ship movements
    ship_movements = truth.get_moves()
    ship_movements.columns=['t', 'x_truth', 'y_truth', 'z_truth','shipid','at_dest']
    ship_movements['at_dest'] = ship_movements['at_dest'].map({'true': 1, 'false': 0})
    rebs_df = rebs_df.merge(ship_movements, how='left', on=['t','shipid'], suffixes=('', '__y'))
    rebs_df.drop(rebs_df.filter(regex='^.*(__y)').columns, axis=1, inplace=True)

    ## get NEA of leaker and impute to ship members USING TRUTH ID
    NEA=p_info.get_nea() # df of messenger's closest star
    NEA.columns=['messenger', 't', 'nearestStar']
    NEA = NEA.merge(rebel_id, how='left', left_on='messenger', right_on='name').drop(labels=['id','name'], axis=1)

    if NEA['shipid'].isna().sum() < 1:
        rebs_df = pd.merge(rebs_df,NEA[['t','shipid','nearestStar']], how='left', on=['shipid','t'], suffixes=('', '__y'))

        if rebs_df.duplicated().astype(int).sum() > 0:
            print('Duplicates after join NEA: '), print(rebs_df.duplicated().astype(int).sum())

            rebs_df.drop_duplicates(inplace=True)

    else:
        print('\n\nNEA leakers with unidentified ships: {}\n'.format(NEA['shipid'].isna().sum()))

        rebs_df = pd.merge(rebs_df,NEA[['messenger','t','nearestStar']], how='left',on=['messenger','t'], suffixes=('', '__y'))

        print('\nnearest stars first time: {}'.format(rebs_df['nearestStar'].notna().sum()))

        NEA2 = NEA.loc[NEA['shipid'].notna()].copy()
        
        if NEA2[['shipid','t','nearestStar']].duplicated().sum() > 0:
            
            print('\nshipmembers duplicate NEA leaks: {}'.format(NEA2[['shipid','t','nearestStar']].duplicated().sum()))
            NEA2 = NEA2[['shipid','t','nearestStar']].drop_duplicates().sort_values(by=['shipid','t'])

        rebs_df = rebs_df.combine_first(rebs_df.drop('nearestStar',axis=1).merge(NEA2, how='left',on=['shipid','t']))
        
        print('nearest stars second time: {}\n'.format(rebs_df['nearestStar'].notna().sum()))

    ## star coordinates
    star_coords = truth.get_stars()
    star_coords.columns=['nearestStar_x', 'nearestStar_y', 'nearestStar_z', 'nearestStar_nNeigh','starid']
    rebs_df = rebs_df.merge(star_coords, how='left', left_on='nearestStar', right_on='starid').drop(labels='starid', axis=1) # append only to leaks

    ## calculate true nearest star (fill leaked nearest star or substitute during MI)
    ship_coordinates = ship_movements[['x_truth', 'y_truth', 'z_truth']].values
    star_coordinates = star_coords[['nearestStar_x', 'nearestStar_y', 'nearestStar_z']].values
    distance_matrix = np.linalg.norm(ship_coordinates[:, np.newaxis] - star_coordinates, axis=2) # Euclidian distances between N stars x M ship locations
    ship_moves_nearest_star = np.argmin(distance_matrix, axis=1) # index of nearest star for each ship movement e.g. ship movement 0; star 155
    ship_movements[['nearestStarId_truth','nearestStar_truth_x','nearestStar_truth_y','nearestStar_truth_z']] = star_coords.loc[ship_moves_nearest_star, ['starid','nearestStar_x','nearestStar_y','nearestStar_z']].values # nearest star and coordinates for each ship

    ## calculate true nearest neighbors of nearest star
    neighbor_stars = NearestNeighbors(radius=50) # neighbors within radius ~½% of 3d space
    neighbor_stars.fit(star_coordinates)
    all_neighbors = neighbor_stars.radius_neighbors(star_coordinates, return_distance=False) # list neighbors of each star
    all_neighbors = [np.array(neighbors) for neighbors in all_neighbors] # to array
    num_neighbors = [len(neighbors) -1 for neighbors in all_neighbors] # Calculate the number of neighbors for each star, not counting each star as its own neighbor
    star_coords['nNeigh_truth'] = num_neighbors
    nNeigh_corr = star_coords['nearestStar_nNeigh'].corr(star_coords['nNeigh_truth']) # correlation between predicted and given nNeigh
    print(f"Correlation between given and predicted nNeigh: {nNeigh_corr:.2f}\n")
    ship_movements['nearestStar_nNeigh_truth'] = star_coords.loc[ship_moves_nearest_star, 'nNeigh_truth'].values

    ## add nearest star id, position, and nNeigh to df
    rebs_df = rebs_df.merge(ship_movements[['t','shipid','nearestStarId_truth','nearestStar_truth_x', 'nearestStar_truth_y', 'nearestStar_truth_z','nearestStar_nNeigh_truth']], how='left', on=['t','shipid'], suffixes=('', '__y'))

    # convert to float
    rebs_df[['nearestStar_truth_x','nearestStar_truth_y','nearestStar_truth_z']] = rebs_df[['nearestStar_truth_x','nearestStar_truth_y','nearestStar_truth_z']].apply(lambda cols_x: cols_x.astype('float64'))

    #endregion

    # get LOC of leaker and impute to ship members (may cause bias if rebels vary systematically in the noise they add to the coordinate)
    LOC=p_info.get_loc() # df of messenger's location
    rebs_df = pd.merge(rebs_df,LOC[['t','messenger','x','y','z']], how='left',on=['messenger','t'], suffixes=('', '__y'))
    # WONTDO: manually impute LOC to shipmembers because members at t leak slightly different positions i.e. "noisy leaks". Multiple imputation most accurately derives accurate values.

    rebs_df.drop(rebs_df.filter(regex='^.*(__x|__y)').columns, axis=1, inplace=True)

    # rearrange and relabel df cols
    rebs_df.rename(columns={'ship': 'shipNo', 'nearestStar':'nearestStarId','id': 'messengerId_truth', 'shipid': 'shipId_truth','at_dest':'atDest_moving'},inplace=True)
    rebs_df = rebs_df[['sampleNo','messengerId','messengerId_truth','shipNo','shipId','shipId_truth','messenger','t','msg_type','nearestStarId','nearestStar_x','nearestStar_y','nearestStar_z','nearestStar_nNeigh','nearestStarId_truth','nearestStar_truth_x', 'nearestStar_truth_y', 'nearestStar_truth_z','nearestStar_nNeigh_truth','x','y','z','x_truth','y_truth','z_truth','atDest_moving']] # drop msg_content
        

    # dfs = wr() # understand dfs, see: describe_dfs.py


    # prepare to imputation
    dfs_MI = rebs_df[rebs_df.columns[~rebs_df.columns.isin(['index','messengerId_truth','shipNo','shipId','messenger','nearestStarId','nearestStar_x','nearestStar_y','nearestStar_z','nearestStar_nNeigh','msg_type'])]].copy() # deselect variables expected not to be useful by MI in presence of similar variables with more unique values better preventing falsely calculated identities. shipId, nearestStarId/x/y/z/nNeigh, msg_type are useful for ML, not MI.
    # NOTE 1) should we drop all rows being NaN in msg_type (perhaps for ML)?
    del rebs_df

    # convert categorical into numeric, required by MI. Amelia understands nominal variables
    cols_to_cat = ['sampleNo','messengerId','shipId_truth','nearestStarId_truth']
    dfs_MI[cols_to_cat] = dfs_MI[cols_to_cat].astype('category').apply(lambda x_col: x_col.cat.codes).replace(-1,np.nan)
    print('cat nulls before conversion:\n\n', dfs_MI[cols_to_cat].isna().sum(),'\n\n','cat nulls after conversion:\n\n',dfs_MI[cols_to_cat].isna().sum(),sep="")

    # save to csv for R processes handled through rpy2
    dfs_MI.to_csv('../data/dfs_MI.csv',index_label='index') #, index=False)
    print(dfs_MI.columns)

    return dfs_MI
