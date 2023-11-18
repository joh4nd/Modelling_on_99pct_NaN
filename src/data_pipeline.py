# run data pipeline

import sample_set as ss
from wrangling_rebels import wrangle
import pandas as pd
# import multiple_imputation as mi
# import split_train_test as stt

def runner(directory_to_files="../data/*.txt", series=10, switch=True, Test=False, m=1, parallel='multicore', ncpus=8):
    """
    Returns: One or more Pandas Dataframes.

    Arguments: directory, draws, switch, Test, m, parallel, and ncpus.

    series specifies the number of datasets.

    switch specifies whether to input up to m number of files or file number m.

    Test is a placeholder, future use for test dataset.

    m is the number of imputations.

    parallel determines whether to proces the function using multiple cpu cores. Amelia defines the possible values. 

    ncpus is the number of cpus used for parallel processing during multiple imputation.
    """
    
    assert series >= 0 and series <= 10

    dfs = []
    # dfs_train = []
    # dfs_test = []

    if Test:
        # placeholder for test data
        
        # sample_set = ...

        pass
    
    else:

        sample_set = ss.path_to_set(directory_to_files)

        if switch:
            sample_set = sample_set[:series] # all files up to series
        else:
            sample_set = [sample_set[sample_set==series-1]] # only series
        
    
    print('Number of time-series: ', len(sample_set))
        
    for sample_no in sample_set:
        
        print(f"Processing sample: {sample_no}")
        
        df = wrangle(f"{sample_no}")
        
        # df = mi.impute(df=df, m=m, parallel=parallel, ncpus=ncpus)
        
        # df_train, df_test = stt_split(df) # split to test and training

        if len(sample_set) == 1:
            df.info()

            # df_train.info()
            # df_test.info()

        elif len(sample_set) > 1:

            dfs.append(df)
            del df
            dfs.info()

            # dfs_train.append(df_train)
            # del df_train
            # dfs_test.append(df_test)
            # del df_test

    if len(sample_set) > 1:
        dfs = pd.concat(dfs).reset_index().drop('index', axis=1)

        # dfs_train = pd.concat(dfs_train).reset_index().drop('index', axis=1)
        # dfs_test = pd.concat(dfs_test).reset_index().drop('index', axis=1)
        # dfs_train.info()
        # dfs_test.info()

    return df if len(sample_set) == 1 else dfs # dfs_train, dfs_test

