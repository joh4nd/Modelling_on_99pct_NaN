import os
import rebel_decode as rd
import pandas as pd
import networkx as nx


data_directory = "../data/"

for i in range(1, 10):  # Replace 10 with the maximum number of files you expect to have
    file_number = str(i).zfill(4)  # Pad with zeros to get four digits
    public_file = os.path.join(data_directory, f"{file_number}_public.txt")
    truth_file = os.path.join(data_directory, f"{file_number}_truth.txt")


"""
# Function to preprocess data and return dataframe
def preprocess(file_path):
    p_info = rd.parse_public_data(file_path)
    df_a = p_info.get_df_a()
    df_b = p_info.get_df_b()
    # Preprocessing steps go here
    # ...
    # Return the preprocessed dataframe
    return preprocessed_df


"""
def preprocess(filenames):

    base_filename = os.path.splitext(filenames)[0]

    data = []
    for file_num in file_nums:
        public_file = f'../data/{file_num:04}_public.txt'
        truth_file = f'../data/{file_num:04}_truth.txt'

    p_info = rd.parse_public_data(f"../data/{base_filename}_public.txt") # "0001_public.txt"
    REBS=p_info.get_rebs()
    COT=p_info.get_cot() # df 
    NEA=p_info.get_nea() # df
    LOC=p_info.get_loc() # df
    FLAVOUR_DICT=p_info.get_flavour_dict()

    truth = rd.parse_truth_data(f"../data/{base_filename}_truth.txt") # "../data/0001_truth.txt"
    star_coords = truth.get_stars()
    ship_movements = truth.get_moves()
    messages = truth.get_messages()

    rebs_df = pd.read_csv(f"../data/{base_filename}_public.txt", # '../data/0001_public.txt'
                    header=None, engine='python',
                    sep='t=(\d+), (\w+), (\w+), (.*)').dropna(how='all', axis=1) # regex from rebel_decode.py
    rebs_df.columns=['t', 'msg_type', 'messenger', 'msg_content']
    rebs_df.reset_index(drop=True)


    # rebs_df = rebs_df[['t','messenger','msg_type']]
    # rebs_df = rebs_df.set_index('t')\
    #             .groupby('messenger')\
    #             .apply(lambda df_x: df_x.reindex(range(1, 1000+1)))\
    #             .drop('messenger', axis=1).reset_index()




    # relations = nx.from_pandas_edgelist(COT, source='messenger', target='cotraveller')
    # ships = {rebel: ship for ship, shipnumber in enumerate((nx.connected_components(relations))) for rebel in shipnumber}
    # rebs_df['ship'] = rebs_df['messenger'].map(ships)
    # # rebs_df['ship'].isna().sum() # yes
    # # rebs_df.ship.nunique() # 4
    # # pd.Series(ships)


    # ship_movements['ship'] = ship_movements['id'].apply(lambda id_x: int(id_x.split('_')[1])) # split, tak the last item, to int
    # ship_movements.rename({'x': 'x_truth', 'y': 'y_truth', 'z': 'z_truth'}, axis=1, inplace=True)
    # ship_movements = ship_movements[['t','x_truth','y_truth','z_truth','ship']]

    # rebs_df_wtruth = pd.merge(rebs_df,ship_movements, how='left',on=['t','ship'])
    # rebs_df_wtruth













