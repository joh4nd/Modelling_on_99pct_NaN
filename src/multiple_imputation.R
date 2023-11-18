# multiple impute wrangled data

pacman::p_load("Amelia", "dplyr")

########## load data ##########
rebels <- read.csv("./repos/opg_RR/data/dfs_MI.csv") # %>% as_tibble() # https://jtr13.github.io/cc21fall1/tibble-vs.-dataframe.html
summary(rebels) # inspect number of NAs

# test a slice of rebels on the 10 concatenated datasets
# rebels1 <- select(filter(rebels,sampleNo==1),everything())
# summary(rebels1)

# run
MI <- amelia(x = rebels,
    m = 1, # start creating just 1 instead of 5
    p2s = 1, # 2 is detailed console output
    idvars = c("index","sampleNo"), # "index",
    noms = c("messengerId","nearestStarId_truth"), # ,"shipId_truth"
    ords = "atDest_moving",
    ts = "t",
    cs = "shipId_truth", # cross-section although the units move in space and time
    empri = 0.05 * nrow(rebels), # ridge prior for high missingness, small n, large correlations. 0.01 = 1% of n
    polytime = 3, # 0-3, power of polynomial time effects. 0 constant, 1 linear, 2 squared, 3 cubic
    splinetime = 6, # cubic smoothing splines of time. 0-3 is same as polytime. max 6.
    intercs = TRUE, # 0/1 should polytime vary across cross-section
    # lags = NULL, # c("","") # vector of vars to include lags for
    # leads = NULL, # c("","") # vector of vars to include leads for
    bounds = matrix(c(11,0,1000, 12,0,1000, 13,0,1000), nrow = 3, ncol = 3, byrow = TRUE), # a matrix of 3 cols, 1 var number, 2 lower bound, 3 upper bound
    # overimp = NULL # if the observed values are deemed to have measurement error
    # collect = TRUE, # slows down MI but helps alleviate RAM issues
    parallel = 'multicore', # unix setting
    ncpus = 8) 

# inspect output
MI_df <- MI$imputations[[1]]
summary(select(rebels,c("x","y","z")))
summary(select(MI_df,c("x","y","z")))

summary(MI)
plot(MI)
tscsPlot(output=MI,var="x",cs=unique(rebels$shipId_truth)) 
# unique(rebels$shipId_truth)
# 
# MI$arguments$cs
# MI$orig.vars[4]

unique(MI$arguments$cs)
MI$orig.vars[4]
