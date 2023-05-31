
import glob 
import pandas as pd
import networkx as nx
# import numpy as np
import bin.rebel_decode as rd



######################################
######### inspect one sample #########
######################################

p_info = rd.parse_public_data("../data/0001_public.txt")
COT=p_info.get_cot() # df of messenger's cotraveller at t
NEA=p_info.get_nea() # df of messenger's closest star
LOC=p_info.get_loc() # df of messenger's location
FLAVOUR_DICT=p_info.get_flavour_dict() # dict of messenger's flavour/msg_type
REBS=p_info.get_rebs() # semi-dict of messenger's co-travellers
rebs_df=p_info.get_rebs_df() # added method to exract df

""" plan
1. use co-traveller info to determine shipmembers and ship identities
2. use ship info to impute on all known shipmembers:
    (a) nearest star and perhaps
    (b) approximate location    


3. concatenate the 10 sample dfs
4. to do:
    (a) i. join with truth data
        ii. carry out multiple imputation
    (b) eventually remove missing values

?. inspect data

    # # inspect 
    # print('Print df info: \n')
    # print(rebs_df.info())
    # print('\n What type of leaks are most common? (are they?)')
    # print(rebs_df.value_counts('msg_type'), '\n')
    # print('Frequency by type: \n', rebs_df.groupby(['msg_type'])['messenger'].nunique())

"""



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
ships = {rebel: shipnumber for shipnumber, ship in enumerate(nx.connected_components(relations), start=1) for rebel in ship} # if len(ship)>1 else np.nan

# Add ships to rebs_df
rebs_df['ship'] = rebs_df['messenger'].map(ships)
print('How many rebels are not aboard a ship?\n', rebs_df['ship'].isna().sum())
print('How many groups of rebels aka ships are there?\n',rebs_df.ship.nunique())
print('What are the groups?',rebs_df.ship.value_counts())
print(pd.Series(ships))


""" 2. impute known shipmembers'
    (a) NEA nearest star and perhaps
    (b) LOC approximate location 

    1) messenger to messenger
    2) messenger to ship
"""
rebs_df = pd.merge(rebs_df,NEA[['messenger','t','closestStar']], how='left',on=['messenger','t'])
NEA['ship'] = NEA['messenger'].map(ships)
rebs_df = pd.merge(rebs_df,NEA[['t','ship','closestStar']]
                   ,how='left',on=['ship','t'])\
                   .drop_duplicates(subset=['t','messenger','ship','closestStar',])

rebs_df = pd.merge(rebs_df,LOC[['messenger','t','x','y','z']], how='left',on=['messenger','t']) # consider averaging leaked loc etc.
LOC['ship'] = LOC['messenger'].map(ships)
rebs_df = pd.merge(rebs_df,LOC[['t','ship','x','y','z']]
                   ,how='left',on=['ship','t'])\
                   .drop_duplicates(subset=['t','messenger','ship','x'])

# counting leak types and number of leakers per type
print(rebs_df.info())
print(rebs_df.value_counts('msg_type'))
print(rebs_df.groupby(['msg_type'])['messenger'].nunique())

