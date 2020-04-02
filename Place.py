from datetime import date, datetime, timedelta
import Person from Person


class Place: 

	def __init__(self, place_info): 
		self.population = set()
		self.place_info = place_info #(40.760265, -73.989105, 'Italian', '217', '291', 'Ristorante Da Rosina')
		self.time_to_recover = 14

		#initilise population according to place popularity 
		self.init_population(self.place_info[4])


	def init_population(self, number):
		for i in range(number):
			self.add_person(Person())

	def get_population(self):
		return self.population

	def set_population(self, new_population):
		self.population = new_population

	def set_total_movements(self, number):
		self.total_movements = number

	def get_total_movements(self):
		return self.total_movements

	def add_person(self, person):
		self.population.add(person)
		

	def incubate_cycle(self, current_time_o):
		''' Process local population and yield a new cycle of infections '''

		#calculate number of infected people 
		infected_pop = [p for p in self.population if p.get_status() == 1]
		total_infected = len(infected_pop)
		total_pop = len(self.population)

		#calculate newly infected
		susceptible_pop = total_pop.difference(infected_pop)

		#calculate probability of infection
		prob_infection = total_infected / total_pop
		
		#calculate newly infected number 
		newly_infected_num = len(susceptible_pop)*prob_infection

		#set newly infected persons accordingly
		for i in range(newly_infected_num):
			susceptible_pop[i].set_infected(datetime_o)

		#set recovered timedelta(days=1): set time_to_recover, current_time
		infected_pop = [p.set_immune(current_time_o) for p in self.infected_pop if current_time - p.get_time_infected() > timedelta(days = self.time_to_recover)]

		

	def set_recovered(self):
		''' Process local population and yield a new cycle of recoveries (death case will be added later)'''
		pass

