from datetime import date, datetime, timedelta
from Person import Person
import random

class Place: 

	def __init__(self, place_info): 
		self.population = set()
		self.place_info = place_info #(40.760265, -73.989105, 'Italian', '217', '291', 'Ristorante Da Rosina')
		self.time_to_recover = 14

		

	def get_population(self):
		return self.population

	def set_population(self, new_population):
		self.population = new_population

	def set_total_movements(self, number):
		self.total_movements = number
		self.init_population(self.total_movements) #initilise population according to place popularity 

	def init_population(self, number):
		start_time = datetime(2010, 12, 21, 20, 0, 0)
		for i in range(number):
			person = Person()
			#infect with a certain probability 
			if random.random() > 0.001:
				person.set_infected(start_time)
			self.add_person(person)

	def get_total_movements(self):
		return self.total_movements

	def add_person(self, person):
		self.population.add(person)
		

	def incubate_cycle(self, current_time_o):
		''' Process local population at a place and yield a new cycle of infections '''

		#calculate number of infected people 
		infected_pop = [p for p in self.population if p.get_status() == 1]

		total_infected = len(infected_pop)
		if total_infected == 0:
			#if there is no infected person at place, no one else can be infected (ie do not execute code below)
			return

		total_pop = len(self.population)

		#calculate newly infected
		susceptible_pop = self.population.difference(infected_pop)

		#calculate probability of infection
		prob_infection = total_infected / total_pop
		
		#calculate newly infected number 
		newly_infected_num = int(len(susceptible_pop)*prob_infection)

		#set newly infected persons accordingly
		newly_infected_pop = random.choices(tuple(susceptible_pop), k = newly_infected_num)
		for i in range(newly_infected_num):
			newly_infected_pop[i].set_infected(current_time_o)

		#set recovered timedelta(days=1): set time_to_recover, current_time
		recovered_pop = [p.set_immune(current_time_o) for p in infected_pop if current_time_o - p.get_time_infected() > timedelta(days = self.time_to_recover)]


		

	def set_recovered(self):
		''' Process local population and yield a new cycle of recoveries (death case will be added later)'''
		pass

