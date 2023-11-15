# multiple impute wrangled data

pacman::p_load("Amelia", "dplyr")

########## load data ##########
rebels <- read.csv("./repos/opg_RR/data/dfs_MI.csv") # %>% as_tibble() # https://jtr13.github.io/cc21fall1/tibble-vs.-dataframe.html
summary(rebels) # NAs

# test a slice of rebels
rebels1 <- select(filter(rebels,sampleNo==1),everything())
summary(rebels1)

# run
MI <- amelia(x = rebels1,
    m = 1, # start creating just 1 instead of 5
    p2s = 1, # 2 is detailed console output
    idvars = c("index","sampleNo"), # "index",
    noms = c("messengerId","nearestStarId_truth"), # ,"shipId_truth"
    ords = "atDest_moving",
    ts = "t",
    cs = "shipId_truth", # cross-section although the units move in space and time
    empri = 0.05 * nrow(rebels1), # ridge prior for high missingness, small n, large correlations. 0.01 = 1% of n
    # lags = NULL, # c("","") # vector of vars to include lags for
    # leads = NULL, # c("","") # vector of vars to include leads for
    # splinetime = NULL, # 0+, cubic smoothing splines of time. 0-3 is same as polytime. 
    polytime = 2, # 0-3, power of polynomial time effects. 0 constant, 1 linear, 2 squared, 3 cubic
    intercs = TRUE, # 0/1 should polytime vary across cross-section
    bounds = matrix(c(11,0,1000, 12,0,1000, 13,0,1000), nrow = 3, ncol = 3, byrow = TRUE), # a matrix of 3 cols, 1 var number, 2 lower bound, 3 upper bound
    # overimp = NULL # if the observed values are deemed to have measurement error
    # collect = TRUE, # slows down MI but helps alleviate RAM issues
    parallel = 'multicore', # unix setting
    ncpus = 8) 

# inspect output
MI1 <- MI$imputations[[1]]
summary(select(rebels1,c("x","y","z")))
summary(select(MI1,c("x","y","z")))


