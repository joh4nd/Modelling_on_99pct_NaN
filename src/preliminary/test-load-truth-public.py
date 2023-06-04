


import glob 
import re
import bin.rebel_decode as rd


files = glob.glob("../data/*.txt") # load all files
sample_set = sorted({re.search(r"(\d{2})_", filetype).group(1).zfill(4) for filetype in files if re.search(r"(\d{2})_", filetype)}) # make time-series iterator
print('Number of time-series: ', len(sample_set))

for sample_no in sample_set:
    
    print(f"Processing sample: {sample_no}")

    p_info = rd.parse_public_data(f"../data/{sample_no}_public.txt")
    truth = rd.parse_truth_data(f"../data/{sample_no}_truth.txt")



################## new public
# public_list = sorted(glob.glob("../data/00??_public.txt")) # list files for rebel_decode
# print('Public files: ', len(public_list))
# public_dfs = [] # list of df's for concatenation at loop end

# for sample_no, filename in enumerate(public_list, start=1):

#     # print('Sample number: {} \nFile path: "{}"'.format((sample_no), (filename)))
#     print('Sample number: {}'.format((sample_no)))
    
#     # extract pandas objects
#     p_info = rd.parse_public_data(filename)
#     rebs_df=p_info.get_rebs_df()





#################### old public + truth

# import os
# directory = "../data/"
# preprocessed = []
# COT_times = []
# ts_ship_ids = set()

# for i in range(1,11):

#     file_number = str(i).zfill(4) # 0001-0010
#     public_file = os.path.join(directory, f"{file_number}_public.txt")
#     truth_file = os.path.join(directory, f"{file_number}_truth.txt")

#     p_info = rd.parse_public_data(public_file) # "0001_public.txt"
#     REBS=p_info.get_rebs() # REBS is not dict: includes headed and comma-concatinated dicts
#     COT=p_info.get_cot() # df 
#     NEA=p_info.get_nea() # df
#     LOC=p_info.get_loc() # df
#     FLAVOUR_DICT=p_info.get_flavour_dict()

#     truth = rd.parse_truth_data(truth_file) # "../dataaa/0001_truth.txt"
#     star_coords = truth.get_stars()
#     ship_movements = truth.get_moves()
#     messages = truth.get_messages()
