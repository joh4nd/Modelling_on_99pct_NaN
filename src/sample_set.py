# define sample set

import glob
import re

def path_to_set(directory_to_files="../data/*.txt"):
    """
    Takes path str as input
    
    Returns sample_set
    """
    
    files = glob.glob(directory_to_files) # list all files, some for rebel_decode
    
    sample_set = sorted({re.search(r"(\d{4})_", filetype).group(1) for filetype in files if re.search(r"(\d{2})_", filetype)}) # make time-series iterator
    
    return sample_set