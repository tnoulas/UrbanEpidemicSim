import networkx as nx
import random
import pandas as pd
import csv
import pylab as plt
import categories
from datetime import date, datetime, timedelta
import pylab as plt

#https://stackoverflow.com/questions/10688006/generate-a-list-of-datetimes-between-an-interval
def perdelta(start, end, delta):
    curr = start
    while curr < end:
        yield curr
        curr += delta

NYC_graph = nx.DiGraph()

#read venue (node) data 
# node_data = {}
pos_dict = {} #will be used to draw the nodes in the graph with geographic topology
for l in open('./shared_data/newyork_anon_locationData_newcrawl.txt'):
	splits = l.split('*;*')
	venue_id = int(splits[0])
	venue_info = eval(splits[1])
	NYC_graph.add_node(venue_id)
	NYC_graph.nodes[venue_id]['info'] = venue_info #(40.760265, -73.989105, 'Italian', '217', '291', 'Ristorante Da Rosina')

	# randomly infect a number of nodes #0 susceptible, 1 infected, 2 recovered
	if random.random() < 0.0001:
		# print ('hi')
		NYC_graph.nodes[venue_id]['status'] = 1
	else:
		NYC_graph.nodes[venue_id]['status'] = 0 

	pos_dict[venue_id] = (venue_info[1], venue_info[0])


#read transitions and respective timestamp information 
df_transitions = pd.read_csv('./shared_data/newyork_placenet_transitions.csv', error_bad_lines=False)
df_transitions['timestamp1'] = pd.to_datetime(df_transitions.timestamp1)
df_transitions['timestamp2'] =pd.to_datetime(df_transitions.timestamp2)

#sort transitions by date
df_transitions =df_transitions.sort_values(by='timestamp1')

#create temporal snapshots of the network: these will be our simulation  
#first date 2010-12-21 20:27:13
#last date 2011-09-19 16:08:50
start_date = datetime(2010, 12, 21, 20, 0, 0)
end_date = datetime(2011, 9, 19, 17, 0, 0)
epoch = 0
date1 = None
date2 = None
for date2 in perdelta(start_date, end_date, timedelta(days=1)):

	#kick start
	if date1 == None:
		date1 = date2
		continue

	# print (result)
	print ('epoch: ' + str(epoch))

	#filter snapshot from original dataset
	mask = (df_transitions['timestamp1'] > date1) & (df_transitions['timestamp2'] <= date2)
	df_transitions_snap = df_transitions.loc[mask]

	#simulate 'spread'
	# print (df_transitions_snap.head())
	for row in df_transitions_snap.iterrows():
		# print ('hi')
		# print (row[0])
		venue1 = row[1][0]
		venue2 = row[1][1]

		#check if interaction involves 'infected' nodes and if yes, spread the virus
		if (NYC_graph.nodes[venue1]['status'] == 1 and NYC_graph.nodes[venue2]['status'] == 0):
			NYC_graph.nodes[venue2]['status'] = 1

		### AT EVERY TEMPORAL SNAPSHOT WE NEED A DISEASE INCUBATION STEP (1)
		### AND A POPULATION EXCHANGE STEP (2)

	#draw the network of infected nodes 
	infected_node_list = [venue for venue in NYC_graph.nodes() if NYC_graph.nodes[venue]['status'] == 1]
	inf_pos_dict = dict((k, pos_dict[k]) for k in infected_node_list)
	infected_graph = NYC_graph.subgraph(infected_node_list)
	frac_infected = round(infected_graph.order() / NYC_graph.order()*10,2)

	# plt.figure(1,figsize=(50,50)) 
	plt.xlabel('longitude')
	plt.ylabel('latitude')
	plt.grid(True)
	# nx.draw_networkx_nodes(infected_graph, pos=pos_dict, nodelist = infected_node_list , node_size=1, alpha=0.1)
	nx.draw(infected_graph, pos=inf_pos_dict , node_size=0.1, node_color='red', alpha=0.1)
	plt.title(date2.strftime("%m/%d/%Y") + ' ' +  str(frac_infected)  + '%' + ' of 85k places infected')

	plt.savefig('./netgraphs/nyc_net_' + str(epoch) + '.png')
	plt.close()

	#increment epoch index and reset date
	epoch+=1
	date1 = date2







# nx.draw_networkx_nodes(NYC_graph, pos=pos_dict, with_labels=False, node_size=20)


# draw the graph using information about nodes geographic positions
# for node_id, node_info in node_data.items():
    # pos_dict[node_id] = (node_info[2], node_info[1])
# nx.draw(nyc_net, pos=pos_dict, with_labels=False, node_size=20)
# plt.savefig('nyc_net_graph.png')
# plt.close()


# for result in perdelta(date(2010, 21, 12, 20, 00, 00), date(2011, 09, 19, 17, 00, 00), timedelta(hours=4)):
# 	print (result)


#code to retrieve upper venue category
# cats = Categories()
# # print cats.get_top_level_categories()
# print cats.get_top_parent('Automotive Shop')

### LOAD NETWORK FROM FILE ###
# nyc_net = nx.read_edgelist(
#     'newyork_net.txt', create_using=nx.DiGraph(), nodetype=int)


# node_data = {}
# for l in open('new york_anon_locationData_newcrawl.txt'):
# 	splits = l.split('*;*')
# 	venue_id = splits[0]
# 	venue_info = eval(splits[1])
# 	node_data[venue_id] = venue_info #(40.760265, -73.989105, 'Italian', '217', '291', 'Ristorante Da Rosina')



#read transitions 34814,32616,2011-04-01 21:46:59,2011-04-03 23:25:17
# node_info = {}
# for l in open('./shared_data/newyork_placenet_transitions.txt'):
# 	splits = l.split(',')
# 	node1 = int(splits[0])
# 	node2 = int(splits[1])
# 	time1 = splits[2] 
# 	time2 = splits[3]
# 	NYC_graph.add_node(node1)
# 	NYC_graph.add_node(node2)
# 	NYC_graph[node1]['']
# 	node_info[node1]
# print (NYC_graph)
