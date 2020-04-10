from datetime import timedelta

class Person:

	def __init__(self, loc_id, loc_time, stay_time):
		self.time_infected = None
		self.status = 0  # 0 susceptible, 1 infected, 2 recovered (herd immunity)
		self.location = loc_id
		self.arrival_time = loc_time
		self.leave_time = loc_time + timedelta(minutes = stay_time)

	def set_infected(self, datetime_o):
		self.time_infected = datetime_o
		self.status = 1

	def set_immune(self, datetime_o):
		self.time_recovered = datetime_o
		self.status = 2

	def get_status(self):
		return self.status

	def get_time_infected(self):
		return self.time_infected
