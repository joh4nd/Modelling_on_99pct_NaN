# multiple impute wrangled data

pacman::p_load("Amelia", "dplyr")

########## load data ##########
rebels <- read.csv("./repos/opg_RR/data/dfs_MI.csv") # %>% as_tibble() # https://jtr13.github.io/cc21fall1/tibble-vs.-dataframe.html
View(rebels)
summary(rebels) # NAs

# choose nothing as index but as nominal or ordinal

# handle missing values 
# library(tidyr)
# my_data_frame <- replace_na(my_data_frame, list(col1 = NA, col2 = NA))

# AmeliaView()

amelia(x = data,
    m = 1, # start creating just 1 instead of 5
    idvars = c("sampleNo", "messengerId", "messengerId_truth", "shipId",
    "shipId_truth", "messenger", "closestStarId"), # idVars get dropped for MI and reinserted
    ts = "t",
    cs = NULL,
    priors = NULL,
    lags = NULL,
    empri = 0,
    intercs = FALSE,
    leads = NULL,
    splinetime = NULL,
    logs = NULL,
    sqrts = NULL,
    ords = "atDest_moving",
    noms = "msg_type",
    incheck = TRUE,
    collect = FALSE,
    bounds = NULL,
    max.resample = 1000,
    tolerance = 1e-04,
    overimp = NULL) # overimpute()

