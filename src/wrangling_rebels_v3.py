# wrangling rebels version 3
# adds calculation of the truest nearest star

import glob 
import re
import pandas as pd
import numpy as np
import networkx as nx
import bin.rebel_decode as rd
from sklearn.neighbors import NearestNeighbors


######################################
#########   all 10 samples   #########
######################################

def wr(directory_to_files="../data/*.txt"):
    """
    Parses the rebel files using rebel_decode.py.

    Parameters:
    directory_to_files (str): the path to the rebel .txt-files.

    Returns:
    pandas.DataFrame: The wrangled, concatenated dataframes ready for multiple imputation.

    """

    files = glob.glob(directory_to_files) # list all files, some for rebel_decode
    sample_set = sorted({re.search(r"(\d{4})_", filetype).group(1) for filetype in files if re.search(r"(\d{2})_", filetype)}) # make time-series iterator
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
        rebs_df['ship'] = rebs_df['messenger'].map(ships).astype(float) #.astype(pd.Int16Dtype()). FIXME: Pandas 2.0 allows int to handle NaN 

        print("\n How many rebels' ships do we fail to identify?\n", int(rebs_df['ship'].isna().sum()/1000)) # t=1000
        
        rebs_df['shipId'] = rebs_df.apply(lambda df_x: np.nan if pd.isna(df_x['ship']) else str(int(df_x['ship']))+df_x['sampleNo'],axis=1) # use sample identifer from df I added to rebel_decode to ensure each ship has a unique ID. Makes ships unique across samples to imply/convey no cross-sample information. FIXME: Pandas 2.0 allows int to handle NaN. see perhaps pd.na
        
        # get TRUTH necessary for multiple imputation

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
        rebs_df = rebs_df.merge(star_coords, how='left', left_on='nearestStar', right_on='starid').drop(labels='starid', axis=1)

        ###########################################
        ########### wrangling_rebels_v3 ###########
        ###########################################

        ## calculate true nearest star (fill leaked nearest star or substitute during MI)
        ship_coordinates = ship_movements[['x_truth', 'y_truth', 'z_truth']].values
        star_coordinates = star_coords[['nearestStar_x', 'nearestStar_y', 'nearestStar_z']].values
        distance_matrix = np.linalg.norm(ship_coordinates[:, np.newaxis] - star_coordinates, axis=2) # Euclidian distances between N stars x M ship locations
        ship_moves_nearest_star = np.argmin(distance_matrix, axis=1) # index of nearest star for each ship movement e.g. ship movement 0; star 155
        ship_movements['nearestStar_truth'] = star_coords.loc[ship_moves_nearest_star, 'starid'].values # nearest star for each ship movement
        ship_movements['nearestStar_truth_x'] = star_coords.loc[ship_moves_nearest_star, 'nearestStar_x'].values # nearest star for each ship movement
        ship_movements['nearestStar_truth_y'] = star_coords.loc[ship_moves_nearest_star, 'nearestStar_y'].values # nearest star for each ship movement
        ship_movements['nearestStar_truth_z'] = star_coords.loc[ship_moves_nearest_star, 'nearestStar_z'].values # nearest star for each ship movement

        ## calculate true nearest neighbors of nearest star
        neighbor_stars = NearestNeighbors(radius=15.0) # neighbors within radius 15
        neighbor_stars.fit(star_coordinates)
        all_neighbors = neighbor_stars.radius_neighbors(star_coordinates, return_distance=False) # list neighbors for each star
        all_neighbors = [np.array(neighbors) for neighbors in all_neighbors] # to array
        num_neighbors = [len(neighbors) for neighbors in all_neighbors] # Calculate the number of neighbors for each star
        star_coords['nNeigh_truth'] = num_neighbors
        ship_movements['nearestStar_nNeigh_truth'] = star_coords.loc[ship_moves_nearest_star, 'nNeigh_truth'].values

        ## add nearst star id, position and nNeigh to df
        rebs_df = rebs_df.merge(ship_movements[['t','shipid','nearestStar_truth','nearestStar_truth_x', 'nearestStar_truth_y', 'nearestStar_truth_z','nearestStar_nNeigh_truth']], how='left', on=['t','shipid'], suffixes=('', '__y'))


        ## get LOC of leaker and impute to ship members (may cause bias if rebels vary systematically in the noise they add to the coordinate)
        LOC=p_info.get_loc() # df of messenger's location
        rebs_df = pd.merge(rebs_df,LOC[['t','messenger','x','y','z']], how='left',on=['messenger','t'], suffixes=('', '__y'))
        

        # removed attempts to manually impute LOC to shipmembers because members at t leaked slightly different positions (cf. noisy leaks) and there is no accurate way to decide what to impute. edit: perhaps the accurate way is one accounting for the noise in leaks, hence consider calculate noise (variance, st. err.) in leak locations, use estimated noise with calculated true positions to complete leak positions?

        rebs_df.drop(rebs_df.filter(regex='^.*(__x|__y)').columns, axis=1, inplace=True)

        # rearrange and relabel df cols
        rebs_df.rename(columns={'ship': 'shipNo', 'nearestStar':'nearestStarId','id': 'messengerId_truth', 'shipid': 'shipId_truth','at_dest':'atDest_moving'},inplace=True)
        rebs_df = rebs_df[['sampleNo','messengerId','messengerId_truth','shipNo','shipId','shipId_truth','messenger','t','msg_type','nearestStarId','nearestStar_x','nearestStar_y','nearestStar_z','nearestStar_nNeigh','nearestStar_truth','nearestStar_truth_x', 'nearestStar_truth_y', 'nearestStar_truth_z','nearestStar_nNeigh_truth','x','y','z','x_truth','y_truth','z_truth','atDest_moving']] # drop msg_content
        

        dfs.append(rebs_df)

    dfs = pd.concat(dfs).reset_index().drop('index', axis=1)
    dfs.info()

    return dfs