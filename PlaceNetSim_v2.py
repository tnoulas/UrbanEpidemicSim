import random
import numpy as np
from datetime import datetime, timedelta

import matplotlib.pylab as plt
import networkx as nx
import pandas as pd

from Place import Place


# https://stackoverflow.com/questions/10688006/generate-a-list-of-datetimes-between-an-interval
def perdelta(start, end, delta):
    curr = start
    while curr < end:
        yield curr
        curr += delta


class PlaceNetSim: 

	def __init__(self):
		self.start_date = datetime(2010, 12, 21, 20, 0, 0)
		# just simulate a day for development 
		self.end_date = datetime(2010, 12, 22, 20, 0, 0)
		#self.end_date = datetime(2011, 9, 19, 17, 0, 0)
		self.cur_time = None 
		self.NYC_graph = nx.DiGraph()
		self.places = {}
		self.init_graph()
		#self.load_transitions_data()

	def init_graph(self):
		#read venue (node) data 
		# node_data = {}
		self.pos_dict = {} #will be used to draw the nodes in the graph with geographic topology
		self.df_transitions = pd.read_csv('./shared_data/newyork_placenet_transitions.csv', error_bad_lines=False)
		places_group = self.df_transitions.groupby('venue1')
		for l in open('./shared_data/newyork_anon_locationData_newcrawl.txt'):
			splits = l.split('*;*')
			venue_id = int(splits[0])
			venue_info = eval(splits[1])

			#add place to graph
			self.NYC_graph.add_node(venue_id)
			# at the venue info we need to add an average duration as well
			self.NYC_graph.nodes[venue_id]['info'] = venue_info #(40.760265, -73.989105, 'Italian', '217', '291', 'Ristorante Da Rosina')
			#NEW: 0 means initially place is not infected. We will set to 1 if it is.
			self.NYC_graph.nodes[venue_id]['infected_status'] = 0

			#initialise place and within place, population information 
			self.places[venue_id] = Place(venue_info, places_group, venue_id)
			#NEW: add reference to main graph to Place Object so we can track which parts of the graph are infected.
			self.places[venue_id].add_main_graph(self.NYC_graph)
			try:
				initial_place_population = int(len(places_group.get_group(venue_id))*0.2)
				self.places[venue_id].set_total_movements(initial_place_population)
			except KeyError:
				self.places[venue_id].set_total_movements(0)
			

			#this will be used for drawing the network
			self.pos_dict[venue_id] = (venue_info[1], venue_info[0])

	
	def run_simulation(self):
		#create temporal snapshots of the network: these will be our simulation  
		#first date 2010-12-21 20:27:13
		#last date 2011-09-19 16:08:50
		# start_date = datetime(2010, 12, 21, 20, 0, 0)
		# end_date = datetime(2011, 9, 19, 17, 0, 0)
		epoch = 0
		date1 = None
		date2 = None
		self.frac_infected_over_time = [] #store for each epoch the fraction of infected population 

		for date2 in perdelta(self.start_date, self.end_date, timedelta(hours = 1)):
			print(datetime.now())

			total_infected = 0

			#kick start
			if date1 == None:
				date1 = date2
				continue

			print ('epoch: ' + str(epoch))

			#simulate 'spread': each row in the transitions graph is a movement from place 1 to place 2
			# this information will be used to describe population exchanges between places
			#for row in df_transitions_snap.iterrows():
			# go over all venues and make an incubation cycle
			for v in self.NYC_graph.nodes():
				self.places[v].incubate_cycle(date1)
				total_infected += self.places[v].get_total_infected()
				#NEW: if no one is infected, add status to corresponding node in graph
				if self.places[v].get_total_infected() == 0:
					self.NYC_graph.nodes[v]['infected_status'] = 0
			# go over all venues and exchange population
			for v in self.NYC_graph.nodes():
				#NEW: ignore graph node if it is not infected
				if self.NYC_graph.nodes[v]['infected_status'] == 0:
					continue
				v_population_set = [vp for vp in self.places[v].get_population() if vp.leave_time < date1+timedelta(hours=1)]
				#NEW: move only infected people
				# v_population_set = [vp for vp in self.places[v].get_population() if vp.leave_time < date1+timedelta(hours=1) and vp.get_status() == 1]

				# this currently does not consider the time between transitions
				# also since the incubation happens before the movement (start of the epoch) a person that moves within 10 minutes of the epoch, whill not have a chance to be infected during this epoch at its new location -- he will have though a chance of being infected at the original location during this epoch (this might not be that bad)	
				for vp in v_population_set:
					try:
						next_place = np.random.choice(list(self.places[vp.location].transitions.keys()), p = list(self.places[vp.location].transitions.values())) 
					except ValueError: # there is no outgoing transitions recorded for this venue. Randomly jump to a venue chosen uniformly -- change this to be proportional to check-ins (or better)  
						next_place = np.random.choice(self.NYC_graph.nodes())
					self.places[vp.location].remove_person(vp)
					vp.location = next_place
					vp.arrival_time = vp.leave_time
					vp.leave_time = vp.arrival_time + timedelta(minutes = random.uniform(10,200))
					self.places[next_place].add_person(vp)	

			# increment epoch index and reset date
			epoch += 1
			date1 = date2

			self.frac_infected_over_time.append(total_infected) # / self.total_population_in_data)  # total_pop_in_epoch)


	def draw_infection_graphs(self):
	    # TODO: fix this so it displays geographically infected population fractions vs infected places

	    # draw the network of infected nodes
	    infected_node_list = [venue for venue in self.NYC_graph.nodes() if self.NYC_graph.nodes[venue]['status'] == 1]
	    inf_pos_dict = dict((k, self.pos_dict[k]) for k in infected_node_list)
	    infected_graph = self.NYC_graph.subgraph(infected_node_list)
	    frac_infected = round(infected_graph.order() / self.NYC_graph.order() * 10, 2)

	    # plt.figure(1,figsize=(50,50))
	    plt.xlabel('longitude')
	    plt.ylabel('latitude')
	    plt.grid(True)
	    # nx.draw_networkx_nodes(infected_graph, pos=pos_dict, nodelist = infected_node_list , node_size=1, alpha=0.1)
	    nx.draw(infected_graph, pos=inf_pos_dict, node_size=0.1, node_color='red', alpha=0.1)
	    plt.title(self.date2.strftime("%m/%d/%Y") + ' ' + str(frac_infected) + '%' + ' of 85k places infected')

	    plt.savefig('./netgraphs/nyc_net_' + str(self.epoch) + '.png')
	    plt.close()

	def plot_infected_vs_total(self):

	    print(self.frac_infected_over_time)
	    xs = [i for i in range(len(self.frac_infected_over_time))]
	    ys = self.frac_infected_over_time
	    plt.xlabel('epoch')
	    plt.ylabel('Fraction Infected')
	    plt.plot(xs, ys, 'k.')
	    plt.grid(True)
	    plt.savefig('infected_per_epoch.pdf')
	    plt.close()


if __name__ == "__main__":
    psim = PlaceNetSim()
    psim.run_simulation()
    psim.plot_infected_vs_total()
