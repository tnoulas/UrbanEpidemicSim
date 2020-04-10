import random
from datetime import datetime, timedelta

from Person import Person


class Place:

    def __init__(self, place_info,places_group,place_id):
        self.population = set()
        self.place_info = place_info  # (40.760265, -73.989105, 'Italian', '217', '291', 'Ristorante Da Rosina')
        # time-to-recover most probably should be an attribute of the person (leaving it here for now)
        self.time_to_recover = 14
        self.total_infected_number = 0
        self.immune_population = set()
        self.vid = place_id
        # if places_group and place_id are both None, then there is no transition probabilities estimated
        try:
            place_transitions = places_group.get_group(place_id)
            self.transitions = (place_transitions['venue2'].value_counts()/len(place_transitions)).to_dict()
        except (KeyError, AttributeError):
            self.transitions = dict()

    def get_population(self):
        return self.population

    def get_total_infected(self):
        return self.total_infected_number

    def set_population(self, new_population):
        self.population = new_population

    def set_total_movements(self, number):
        self.total_movements = number
        self.init_population(self.total_movements)  # initilise population according to place popularity

    def init_population(self, number):
        start_time = datetime(2010, 12, 21, 20, 0, 0)
        for i in range(number):
            # this need to change based on data
            stay_time = random.uniform(10,200)
            person = Person(self.vid, start_time, stay_time)
            # infect with a certain probability
            if random.random() <= 0.01:
                person.set_infected(start_time)
            self.add_person(person)

    def get_total_movements(self):
        return self.total_movements

    def add_person(self, person):
        self.population.add(person)

    def remove_person(self, person):
        self.population.remove(person)

    def incubate_cycle(self, current_time_o):
        ''' Process local population at a place and yield a new cycle of infections '''

        # set recovered timedelta(days=1): set time_to_recover, current_time
        infected_pop = [p for p in self.population if p.get_status() == 1]
        recovered_pop = [p.set_immune(current_time_o) for p in infected_pop if
                         current_time_o - p.get_time_infected() > timedelta(days=self.time_to_recover)]
        infected_pop = set(infected_pop).difference(recovered_pop)  # infected pop - recovered

        # calculate number of infected people
        total_infected = len(infected_pop)

        # calculate susceptible to infection
        susceptible_pop = self.population.difference(infected_pop)
        susceptible_pop = susceptible_pop.difference(self.immune_population)
        self.immune_population = self.immune_population.union(recovered_pop)

        # calculate probability of infection
        total_pop = len(self.population)
        if total_pop == 0:
            prob_infection = 0.0
        else:
            prob_infection = total_infected / total_pop

        # calculate newly infected number
        newly_infected_num = int(len(susceptible_pop) * prob_infection)

        # set newly infected persons accordingly
        newly_infected_pop = random.choices(tuple(susceptible_pop), k=newly_infected_num)
        for i in range(newly_infected_num):
            newly_infected_pop[i].set_infected(current_time_o)

        # count number infected
        self.total_infected_number = len(infected_pop) + newly_infected_num

    def set_recovered(self):
        ''' Process local population and yield a new cycle of recoveries (death case will be added later)'''
        pass
