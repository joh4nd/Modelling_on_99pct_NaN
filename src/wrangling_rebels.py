# wrangling rebels

# in the terminal, activate the virtual environment
# $ source opg_RR/bin/venv/bin/activate

# import
import glob 
import pandas as pd
import networkx as nx

"""load tools in rebel_decode.py
__init__.py in src/bin/
vs code uses absolute paths for .py
"""
from opg_RR.src.bin import rebel_decode as rd

######### inspect one sample #########
p_info = rd.parse_public_data("opg_RR/data/0001_public.txt")
COT=p_info.get_cot() # df of messengers cotraveller at t
NEA=p_info.get_nea() # df of messengers closest star
LOC=p_info.get_loc() # df of messengers location
FLAVOUR_DICT=p_info.get_flavour_dict() # dict of messengers flavour/msg_type
REBS=p_info.get_rebs() # semi-dict of messengers cotravellers
rebs_df = pd.read_csv('opg_RR/data/0001_public.txt',
                 header=None, engine='python',
                 sep='t=(\d+), (\w+), (\w+), (.*)')\
                    .dropna(how='all', axis=1) # regex from rebel_decode.py
rebs_df.columns=['t', 'msg_type', 'messenger', 'msg_content'] # replace index,1,2,3,4
rebs_df.reset_index(drop=True)
rebs_df = rebs_df[['t','messenger','msg_type']] # drop msg_content

""" plan
1. use co-traveller info to determine shipmembers and ship identities
2. use ship info to impute on all known shipmembers:
    (a) nearest star and perhaps
    (b) approximate location    
3. concatenate the 10 sample dfs
4. either
    (a) join with truth data and carry out multiple imputation impute
    (b) or remove missing values
"""

""" 1. determine shipmembers and ship identities
We know that some rebels travel together at all times. We can tie the rebels together using the names and the leaked cotraveller names (including who leaked the names).

a. Make a graph called relations based on the rebels relationships to each other through leaked information about who they travel with.
b. Extract the ships based on observed relations using `connected_components`.
c. Use `enumerate` to assign unique shipnumbers to each ship. Finally, use the shipnumber to determine the ship of each messenger/rebel.
d. To this end, use dictionary comprehension i.e. a method to make a dictionary, that is, {key: value} pairs.
e. Dict comprhension syntax is {new_key:new_value for item in iterable}.
f. We use two for loops:
    i. the first to loop through each `shipnumber, ship`-tuple returned by enumerate e.g. 4 connected components;
    ii. the second to loop through each rebel in the given instance of a ship (ship is a string of rebel names, so e.g. Finn, Marie, Ane) defining the {rebel: shipnumber} key-value pairs.
"""
relations = nx.from_pandas_edgelist(COT, source='messenger', target='cotraveller') # graph of nodes and edges
print(list(nx.connected_components(relations))) # dict-lists of connected rebels
print(list(enumerate((nx.connected_components(relations))))) # given numbers in tuples as (number, {'rebel, names, here'})
ships = {rebel: shipnumber for shipnumber, ship in enumerate((nx.connected_components(relations))) for rebel in ship}
print('TO BE FIXED: rebels without ties must not be in a ship! One method is to insert if-statements, such that if len(ship)>1 we go on, else NaN')

# Add ships to rebs_df
rebs_df['ship'] = rebs_df['messenger'].map(ships)
print('How many rebels are not aboard a ship?\n', rebs_df['ship'].isna().sum()) # yes
print('How many groups of rebels aka ships are there?\n',rebs_df.ship.nunique())
print(pd.Series(ships))

# counting leak types and number of leakers per type
print(rebs_df.info())
print(rebs_df.value_counts('msg_type'))
print(rebs_df.groupby(['msg_type'])['messenger'].nunique())


""" 3. concatenation

plan: 
a) add sample identifer
b) make sure each ship has a unique ID
"""












# load files and wrangle
public_list = glob.glob("opg_RR/data/00??_public.txt") # list files for rebel_decode
public_dfs = []

for filename in public_list: #for i, filename in enumerate(file_list):

    # p_info = rd.parse_public_data("filename")

    rebs_df = pd.read_csv(filename,
                    header=None, engine='python',
                    sep='t=(\d+), (\w+), (\w+), (.*)').dropna(how='all', axis=1) # regex from rebel_decode.py
    rebs_df.columns=['t', 'msg_type', 'messenger', 'msg_content']
    rebs_df.reset_index(drop=True)

    # df['iteration'] = '{:04d}'.format(i+1)


# make time-series for predicting observations at 1-1000 time points
rebs_df = rebs_df.set_index('t')\
            .groupby('messenger')\
            .apply(lambda df_x: df_x.reindex(range(1, 1000+1)))\
            .drop('messenger', axis=1).reset_index()


"""Inspect each sample

1) What is the number of unique rebel names?
 - is it ~30?

2) What is the number of unique
2.1) leaked COT
2.2) leaked LOC: xyz
2.3) leaked NEA
2.4) t


3) What is the mean
3.1) leaked LOC: xyz
3.2) leaked NEA
3.3) t
"""
