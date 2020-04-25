import random
import numpy as np
from datetime import datetime, timedelta

import matplotlib.pylab as plt
import networkx as nx
import pandas as pd

from Place import Place
from categories import Categories
# # print cats.get_top_level_categories()
# # print cats.get_top_parent('Automotive Shop')


# https://stackoverflow.com/questions/10688006/generate-a-list-of-datetimes-between-an-interval
def perdelta(start, end, delta):
    curr = start
    while curr < end:
        yield curr
        curr += delta

def get_day_period(time):
	periods = dict.fromkeys([0,1,2,3,4,5], 'OVERNIGHT')
	periods.update(dict.fromkeys([6,7,8,9], 'MORNING'))
	periods.update(dict.fromkeys([10,11,12,13,14], 'MIDDAY'))
	periods.update(dict.fromkeys([15,16,17,18], 'AFTERNOON'))
	periods.update(dict.fromkeys([19,20,21,22,23], 'NIGHT'))
	return periods.get(time.hour, "Invalid time")

class PlaceNetSim: 

	def __init__(self, cats, periods = 0):
		self.start_date = datetime(2010, 12, 21, 20, 0, 0)
		# just simulate a day for development 
		self.end_date = datetime(2010, 12, 22, 20, 0, 0)
		#self.end_date = datetime(2011, 9, 19, 17, 0, 0)
		self.cats = cats #place categories management class
		self.cats_to_infected_info = {}
		self.cur_time = None 
		self.NYC_graph = nx.DiGraph()
		self.NYC_graph_periods = dict.fromkeys(['OVERNIGHT','MORNING','MIDDAY','AFTERNOON','NIGHT'], nx.DiGraph())
		self.places = {}
		self.places_periods = dict.fromkeys(['OVERNIGHT','MORNING','MIDDAY','AFTERNOON','NIGHT'], {})
		if periods:
			self.init_graph_period()
		else:
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
			#0 means initially place is not infected. We will set to 1 if it is.
			self.NYC_graph.nodes[venue_id]['infected_status'] = 0

			#initialise place and within place, population information 
			self.places[venue_id] = Place(venue_info, places_group, venue_id)
			#add reference to main graph to Place Object so we can track which parts of the graph are infected.
			self.places[venue_id].add_main_graph(self.NYC_graph)
			try:
				initial_place_population = int(len(places_group.get_group(venue_id))*0.2)
				self.places[venue_id].set_total_movements(initial_place_population)
			except KeyError:
				self.places[venue_id].set_total_movements(0)
			

			#this will be used for drawing the network
			self.pos_dict[venue_id] = (venue_info[1], venue_info[0])
	
	# new graph initialization function to consider the time period
	def init_graph_period(self):
		# the following requires a small change in the NYC_movements_v2 file
		# remove the \" from the strings
		# change the month-year column to two separate columns
		# TODO: the following is timeconsuming (~ 5 seconds each time that it is loaded), so most probably we can pass it as an argument as well
		self.df_transitions_all = pd.read_csv('./shared_data/NYC_movements_v2.csv', error_bad_lines=False, names = ['venue1','venue2','year','month','period','weight'])
		for p in ['OVERNIGHT','MORNING','MIDDAY','AFTERNOON','NIGHT','OVERNIGHT']:
			self.df_transitions = self.df_transitions_all[self.df_transitions_all['period'] == p]
			period_groups = self.df_transitions.groupby('period')
			p_group = period_groups.get_group(p)
			p_places_group = p_group.groupby('venue1')
			for l in open('./shared_data/NYC_venue_info_v2.csv'):
				splits = l.split(";")
				venue_id = splits[0]
				venue_info = splits[2] ## this does not include information such number of users/checkins
				self.NYC_graph_periods[p].add_node(venue_id)
				self.NYC_graph_periods[p].nodes[venue_id]['info'] = venue_info
				self.NYC_graph_periods[p].nodes[venue_id]['infected_status'] = 0
				# TODO: the initialization at class Place will need to change to account for the fact that each entry is weighted with the number of transitions of the type observed rather than corresponding to one only transition
				self.places_periods[p][venue_id] = Place(venue_info, p_places_group, venue_id)
				self.places_periods[p][venue_id].add_main_graph(self.NYC_graph_periods[p])
				try:
					initial_place_population = int(sum(p_places_group.get_group(venue_id)['weight'])*0.2)
					self.places_periods[p][venue_id].set_total_movements(initial_place_population)
				except KeyError:
					self.places_periods[p][venue_id].set_total_movements(0)
		
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
			# find the time period we are so we choose the transitions accordingly
			period = get_day_period(date2)
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
			infected_to_move = []
			for v in self.NYC_graph.nodes():
				# self.places[v].incubate_cycle(date1)
				self.places[v].incubate_cycle_v2(date1)

				total_infected += self.places[v].get_total_infected()
				try:
					top_category = self.cats.get_top_parent(self.places[v].get_category())
				except:
					top_category = 'None'
				self.cats_to_infected_info.setdefault(top_category, 0)
				self.cats_to_infected_info[top_category] += total_infected
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
				try:
					next_place = np.random.choice(list(self.places[v].transitions.keys()), size = len(v_population_set), p = list(self.places[v].transitions.values()))
				except ValueError: # there is no outgoing transitions recorded for this venue. Randomly jump to a venue chosen uniformly -- change this to be proportional to check-ins (or better)  
					next_place = np.random.choice(self.NYC_graph.nodes(),size = len(v_population_set))
				set([self.places[vp.location].remove_person(vp) for vp in v_population_set])
				set([v_population_set[i].set_location(next_place[i]) for i in range(len(v_population_set))])
				set([v_population_set[i].set_arrival(v_population_set[i].leave_time) for i in range(len(v_population_set))])
				tds = list(np.random.uniform(10,200,size=len(v_population_set)))
				set([v_population_set[i].set_leave(tds[i]) for i in range(len(v_population_set))])
				set([self.places[vp.location].add_person(vp) for vp in v_population_set])

			# increment epoch index and reset date
			self.draw_infection_graphs(epoch)
			epoch += 1
			date1 = date2

			self.frac_infected_over_time.append(total_infected) # / self.total_population_in_data)  # total_pop_in_epoch)


	def draw_infection_graphs(self, epoch):
	    # TODO: fix this so it displays geographically infected population fractions vs infected places

	    # draw the network of infected nodes
	    infected_node_list = [venue for venue in self.NYC_graph.nodes() if self.NYC_graph.nodes[venue]['infected_status'] == 1]
	    inf_pos_dict = dict((k, self.pos_dict[k]) for k in infected_node_list)
	    infected_graph = self.NYC_graph.subgraph(infected_node_list)
	    frac_infected = round(infected_graph.order() / self.NYC_graph.order() * 10, 2)

	    # plt.figure(1,figsize=(50,50))
	    plt.xlabel('longitude')
	    plt.ylabel('latitude')
	    plt.grid(True)
	    # nx.draw_networkx_nodes(infected_graph, pos=pos_dict, nodelist = infected_node_list , node_size=1, alpha=0.1)
	    nx.draw(infected_graph, pos=inf_pos_dict, node_size=0.1, node_color='red', alpha=0.1)
	    # plt.title(self.date2.strftime("%m/%d/%Y") + ' ' + str(frac_infected) + '%' + ' of 85k places infected')
	    plt.title(str(frac_infected) + '%' + ' of 85k places infected')

	    plt.savefig('./netgraphs/nyc_net_' + str(epoch) + '.png')
	    plt.close()


	def plot_infections_per_category(self):
		cat_infection_freqs = np.array([freq for cat, freq in self.cats_to_infected_info.items()])
		df = pd.DataFrame([cat_infection_freqs], columns = self.cats_to_infected_info.keys()) 
		fig = df.plot.bar().get_figure()
		fig.savefig('infections_per_category.pdf')
  		

	def plot_infected_vs_total(self):

	    xs = [i for i in range(len(self.frac_infected_over_time))]
	    ys = self.frac_infected_over_time
	    plt.xlabel('epoch')
	    plt.ylabel('Fraction Infected')
	    plt.plot(xs, ys, 'k.')
	    plt.grid(True)
	    plt.savefig('infected_per_epoch.pdf')
	    plt.close()


if __name__ == "__main__":
	cats = Categories()
	psim = PlaceNetSim(cats)
	psim.run_simulation()
	psim.plot_infected_vs_total()
	psim.plot_infections_per_category()
