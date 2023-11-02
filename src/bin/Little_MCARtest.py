# Little's MCAR test
# https://stackoverflow.com/questions/58144737/mcar-littles-test-in-python/76499703#comment102675848_58144737

import numpy as np
import pandas as pd
from scipy.stats import chi2

def little_mcar_test(data, alpha=0.05):
    """
    Performs Little's MCAR (Missing Completely At Random) test on a dataset with missing values.
    
    Parameters:
    data (DataFrame): A pandas DataFrame with n observations and p variables, where some values are missing.
    alpha (float): The significance level for the hypothesis test (default is 0.05).
    
    Returns:
    A tuple containing:
    - A matrix of missing values that represents the pattern of missingness in the dataset.
    - A p-value representing the significance of the MCAR test.
    """
    
    # Calculate the proportion of missing values in each variable
    p_m = data.isnull().mean()
    
    # Calculate the proportion of complete cases for each variable
    p_c = data.dropna().shape[0] / data.shape[0]
    
    # Calculate the correlation matrix for all pairs of variables that have complete cases
    R_c = data.dropna().corr()
    
    # Calculate the correlation matrix for all pairs of variables using all observations
    R_all = data.corr()
    
    # Calculate the difference between the two correlation matrices
    R_diff = R_all - R_c
    
    # Calculate the variance of the R_diff matrix
    V_Rdiff = np.var(R_diff, ddof=1)
    
    # Calculate the expected value of V_Rdiff under the null hypothesis that the missing data is MCAR
    E_Rdiff = (1 - p_c) / (1 - p_m).sum()
    
    # Calculate the test statistic
    T = np.trace(R_diff) / np.sqrt(V_Rdiff * E_Rdiff)
    
    # Calculate the degrees of freedom
    df = data.shape[1] * (data.shape[1] - 1) / 2
    
    # Calculate the p-value using a chi-squared distribution with df degrees of freedom and the test statistic T
    p_value = 1 - chi2.cdf(T ** 2, df)
    
    # Create a matrix of missing values that represents the pattern of missingness in the dataset
    missingness_matrix = data.isnull().astype(int)
    
    # Return the missingness matrix and the p-value
    return missingness_matrix, p_value