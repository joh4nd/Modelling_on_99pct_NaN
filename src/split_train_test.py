# split data into training and test
import pandas as pd
import random

def split(df):
    """
    Splits concatenated dataframe into training and test dataframes

    Argument: df

    Returns: df_training, df_test
    """

    test_samples = random.sample(df['SampleNo'].unique().tolist(), 2) # draw 2 random  samples
    train_data = df[~df['SampleNo'].isin(test_samples)]
    test_data = df[df['SampleNo'].isin(test_samples)]

    return train_data, test_data