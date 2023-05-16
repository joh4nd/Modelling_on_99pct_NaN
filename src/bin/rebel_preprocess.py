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











