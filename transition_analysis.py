import pickle
import numpy as numpy
import pandas as pd
import geopy.distance
from calendar import monthrange
from statsmodels.distributions.empirical_distribution import ECDF

nyc_move = pd.read_csv("shared_data/NYC_movements_v2.csv",names=['v1','v2','month','day_period','transitions'])

# first group by the day period
periods = list(nyc_move.day_period.unique())
nyc_move_period = nyc_move.groupby('day_period')

transition_counts = dict()

for p in periods:
    transition_counts[p] = nyc_move_period.get_group(p).groupby('month').apply(lambda x: np.sum(x.transitions))
    for m in list(transition_counts[p].index):
        transition_counts[p][m] = transition_counts[p][m]/monthrange(int(m.split("-")[0]),int(m.split("-")[1]))[1]

transition_counts_df = pd.DataFrame(data = {'month': list(transition_counts['MORNING'].index), 'MORNING': list(transition_counts['MORNING']), 'AFTERNOON': list(transition_counts['AFTERNOON']), 'MIDDAY': list(transition_counts['MIDDAY']), 'NIGHT': list(transition_counts['NIGHT']), 'OVERNIGHT': list(transition_counts['OVERNIGHT'])})

# venue info

venues = { line.split(";")[0] : (float(line.split(";")[2].split(",")[0]), float(line.split(";")[2].split(",")[1])) for line in open("shared_data/NYC_venue_info_v2.csv","r") }

v1 = [venues[v] for v in nyc_move['v1'].values]
v2 = [venues[v] for v in nyc_move['v2'].values]

trans_dist = list(map(lambda x, y: geopy.distance.vincenty(x,y).miles, v1, v2))
nyc_move['dist'] = trans_dist

nyc_move_period = nyc_move.groupby('day_period')

distances_covered = dict()
distances_covered_ecdf = dict()

months = set(list(nyc_move['month']))

for p in periods:
    groupp = nyc_move_period.get_group(p).groupby('month')
    for m in months:
        distances_covered[p+":"+m] = list(groupp.get_group(m)['dist'])
        distances_covered_ecdf[p+":"+m] = edf.ECDF(distances_covered[p+":"+m])


pickle.dump( [transition_counts_df, distances_covered_ecdf], open( "transitions_simulations.pkl", "wb" ) )


'''
This can be used for sampling transition distances for "random" jumps using the inverted CDF method
e.g.,

sample_edf = edf.ECDF(distances_covered[p])
d = [sample_edf(x) for x in np.linspace(0,np.max(nyc_move['dist']),10000)]

r = random.uniform(0,1)
adf = lambda x : abs(x - r)
x_hat = min(d, key=adf)
sample = np.linspace(0,np.max(nyc_move['dist']),10000)[d.index(x_hat)]
'''
