import networkx as nx
import random
import pandas as pd
import csv
import pylab as plt
import categories
from datetime import date, datetime, timedelta
import pylab as plt
from Place import Place


#https://stackoverflow.com/questions/10688006/generate-a-list-of-datetimes-between-an-interval
def perdelta(start, end, delta):
    curr = start
    while curr < end:
        yield curr
        curr += delta

class PlaceNetSim: 

	def __init__(self):
		self.start_date = datetime(2010, 12, 21, 20, 0, 0)
		self.end_date = datetime(2011, 9, 19, 17, 0, 0)
		self.cur_time = None 
		self.NYC_graph = nx.DiGraph()
		self.places = {}
		self.init_graph_and_populations()


	def init_graph_and_populations(self):
		#read venue (node) data 
		# node_data = {}
		self.pos_dict = {} #will be used to draw the nodes in the graph with geographic topology
		for l in open('./shared_data/newyork_anon_locationData_newcrawl.txt'):
			splits = l.split('*;*')
			venue_id = int(splits[0])
			venue_info = eval(splits[1])

			#add place to graph
			self.NYC_graph.add_node(venue_id)
			self.NYC_graph.nodes[venue_id]['info'] = venue_info #(40.760265, -73.989105, 'Italian', '217', '291', 'Ristorante Da Rosina')

			#initialise placee and within place, population information 
			self.places[venue_id] = Place(venue_info)

			#this will be used for drawing the network
			self.pos_dict[venue_id] = (venue_info[1], venue_info[0])



	def load_transitions_data(self):
		#read transitions and respective timestamp information 
		self.df_transitions = pd.read_csv('./shared_data/newyork_placenet_transitions.csv', error_bad_lines=False)
		self.df_transitions['timestamp1'] = pd.to_datetime(self.df_transitions.timestamp1)
		self.df_transitions['timestamp2'] =pd.to_datetime(self.df_transitions.timestamp2)

		#sort transitions by date
		self.df_transitions = self.df_transitions.sort_values(by='timestamp1')

		#load total movements originating at each place 
		for place in self.places:
			mask = (self.df_transitions['venue1'] == venue)
			place_transitions = self.df_transitions.loc[mask]
			
			place.set_total_movements(len(place_transitions))

	
	def run_simulation(self):
		#create temporal snapshots of the network: these will be our simulation  
		#first date 2010-12-21 20:27:13
		#last date 2011-09-19 16:08:50
		# start_date = datetime(2010, 12, 21, 20, 0, 0)
		# end_date = datetime(2011, 9, 19, 17, 0, 0)

		epoch = 0
		date1 = None
		date2 = None
		for date2 in perdelta(self.start_date, self.end_date, timedelta(days=1)):

			#kick start
			if date1 == None:
				date1 = date2
				continue

			# print (result)
			print ('epoch: ' + str(epoch))

			#filter snapshot from original dataset
			mask = (self.df_transitions['timestamp1'] > date1) & (self.df_transitions['timestamp2'] <= date2)
			df_transitions_snap = self.df_transitions.loc[mask]

			### AT EVERY TEMPORAL SNAPSHOT WE NEED A DISEASE INCUBATION STEP (1)
			venue1.incubate_cycle(date1)
			venue2.incubate_cycle(date2) #check

			#simulate 'spread': each row in the transitions graph is a movement from place 1 to place 2
			# this information will be used to describe population exchanges between places
			for row in df_transitions_snap.iterrows():
				# print ('hi')
				# print (row[0])
				venue1 = row[1][0]
				venue2 = row[1][1]

				#check if interaction involves 'infected' nodes and if yes, spread the virus
				# if (NYC_graph.nodes[venue1]['status'] == 1 and NYC_graph.nodes[venue2]['status'] == 0):
				# 	NYC_graph.nodes[venue2]['status'] = 1


				### AND A POPULATION EXCHANGE STEP (2)
				#for the time being: move a randomly chosen 'fraction' of population at place 1 to place 2
				#fraction size is equal to the number of transitions / total number of transitions out-going from place 1
				venue1_population_set =  self.places[venue1].get_population()
				venue2_population_set =  self.places[venue2].get_population()

				moving_population_size = 1.0 / self.places[venue1].get_total_movements() 

				#pick random sample of population at origin, then remove from place 1 and add to place 2
				moving_pop = random.sample(venue1_population_set, moving_population_size)
				new_venue1_pop = venue1_population_set.difference(moving_pop)
				self.places[venue1].set_population(new_venue1_pop)

				new_venue2_pop = venue2_population_set.add(moving_pop)
				self.places[venue1].set_population(new_venue2_pop)

				#increment epoch index and reset date
				epoch+=1
				date1 = date2




	def draw_infection_graphs(self):
		#TODO: fix this so it displays geographically infected population fractions vs infected places

		#draw the network of infected nodes 
		infected_node_list = [venue for venue in self.NYC_graph.nodes() if self.NYC_graph.nodes[venue]['status'] == 1]
		inf_pos_dict = dict((k, pos_dict[k]) for k in infected_node_list)
		infected_graph = self.NYC_graph.subgraph(infected_node_list)
		frac_infected = round(infected_graph.order() / self.NYC_graph.order()*10,2)

		# plt.figure(1,figsize=(50,50)) 
		plt.xlabel('longitude')
		plt.ylabel('latitude')
		plt.grid(True)
		# nx.draw_networkx_nodes(infected_graph, pos=pos_dict, nodelist = infected_node_list , node_size=1, alpha=0.1)
		nx.draw(infected_graph, pos=inf_pos_dict , node_size=0.1, node_color='red', alpha=0.1)
		plt.title(date2.strftime("%m/%d/%Y") + ' ' +  str(frac_infected)  + '%' + ' of 85k places infected')

		plt.savefig('./netgraphs/nyc_net_' + str(epoch) + '.png')
		plt.close()





