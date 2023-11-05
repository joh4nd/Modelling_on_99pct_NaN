# calculate nearest star

# to wrangling_rebels v3

import pandas as pd
import numpy as np
import networkx as nx
import bin.rebel_decode as rd
from sklearn.neighbors import NearestNeighbors
import matplotlib.pyplot as plt
import seaborn as sns

# extract pandas objects
p_info = rd.parse_public_data(f"../data/0001_public.txt")
truth = rd.parse_truth_data(f"../data/0001_truth.txt")
    
# calculate ship distance from stars
## ship_movements: shipid and coordinates
ship_movements = truth.get_moves().loc[:,'t':'id']
ship_movements.columns=['t', 'x_truth', 'y_truth', 'z_truth','shipid']

## star_coords: starID and coordinates
star_coords = truth.get_stars()
star_coords.columns=['nearestStar_x', 'nearestStar_y', 'nearestStar_z', 'nNeigh','starid']

## convert pd df to np array
ship_coordinates = ship_movements[['x_truth', 'y_truth', 'z_truth']].values
star_coordinates = star_coords[['nearestStar_x', 'nearestStar_y', 'nearestStar_z']].values

## calculate distances between ships and stars
distance_matrix = np.linalg.norm(ship_coordinates[:, np.newaxis] - star_coordinates, axis=2) # 3d distances in 4000 (ship movements) x 4157 (stars) matrix

## find index of the nearest star for each ship
nearest_star_indices = np.argmin(distance_matrix, axis=1) # index of stars minimizing distances to ships at each move e.g. shipmovement 0; star 155

## add nearest star to ship movements
ship_movements['nearestStar'] = star_coords.loc[nearest_star_indices, 'starid'].values
ship_movements['nearestStar_x'] = star_coords.loc[nearest_star_indices, 'nearestStar_x'].values
ship_movements['nearestStar_y'] = star_coords.loc[nearest_star_indices, 'nearestStar_y'].values
ship_movements['nearestStar_z'] = star_coords.loc[nearest_star_indices, 'nearestStar_z'].values




# calculate number of nearby stars based on fixed radius

##region: check assumptions for choosing Euclidian, Manhattan, or Mahalanobis distances
### scale
same_scale = all(star_coords['nearestStar_x'].between(0, 1000)) and \
             all(star_coords['nearestStar_y'].between(0, 1000)) and \
             all(star_coords['nearestStar_z'].between(0, 1000))
print("Is the data on the same scale (0-1000)?", same_scale) # TRUE
### variance
data_variance = star_coords[['nearestStar_x', 'nearestStar_y', 'nearestStar_z']].var()
isotropic = (data_variance.max() - data_variance.min()) < 0.1
print("Is the data isotropic?", isotropic) # FALSE
### correlations
correlation_matrix = star_coords[['nearestStar_x', 'nearestStar_y', 'nearestStar_z']].corr()
plt.figure(figsize=(8, 6))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm')
plt.title("Feature Correlation Heatmap")
plt.show() # corr ~ < 0.1
### outliers
plt.figure(figsize=(8, 6))
sns.boxplot(data=star_coords[['nearestStar_x', 'nearestStar_y', 'nearestStar_z']])
plt.title("Box Plot for Outlier Detection")
plt.show() # normally distributed
### range
feature_ranges = star_coords[['nearestStar_x', 'nearestStar_y', 'nearestStar_z']].max() - star_coords[['nearestStar_x', 'nearestStar_y', 'nearestStar_z']].min()
unit_variation = feature_ranges.var()
print("Do features have varying units?", unit_variation > 1) # TRUE
### spherical/ellipsoidal distributions
plt.figure(figsize=(8, 6))
sns.pairplot(data=star_coords[['nearestStar_x', 'nearestStar_y', 'nearestStar_z']], diag_kind="kde")
plt.suptitle("Pairwise Distributions")
plt.show()
##endregion


## calculate distance
neighbor_stars = NearestNeighbors(radius=45.0) # defaults to Euclidian norm
neighbor_stars.fit(star_coordinates)
all_neighbors = neighbor_stars.radius_neighbors(star_coordinates, return_distance=False) # find neighbors for each star
all_neighbors = [np.array(neighbors) for neighbors in all_neighbors] # to np array
num_neighbors = [len(neighbors) for neighbors in all_neighbors] # Calculate the number of neighbors for each star
# Add the number of neighbors to the star DataFrame
star_coords['nNeigh_truth'] = num_neighbors
star_coords[['nNeigh_truth','nNeigh']]
ship_movements['nNeigh_truth'] = star_coords.loc[nearest_star_indices, 'nNeigh_truth'].values


## messages: rebelID, shipid
# messages = truth.get_messages()
