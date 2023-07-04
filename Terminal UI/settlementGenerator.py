import math
import sys
import time

import psutil

class perfAnnouncer:
	def __init__(self):
		self.process = psutil.Process()

		self.recordedtime = 0
		self.recordedmemory = 0
		self.record()
	
	def record(self):
		self.recordedtime = time.perf_counter()
		self.recordedmemory = self.process.memory_info().rss
	
	def announce(self, message, record = True):
		newtime = time.perf_counter()
		timedelta = newtime - self.recordedtime

		newmemory = self.process.memory_info().rss
		memorydelta = newmemory - self.recordedmemory

		if abs(memorydelta) > 1024 ** 2:
			memorystring = f"{abs(memorydelta) / 1024 ** 2} MB"
		elif abs(memorydelta) > 1024:
			memorystring = f"{abs(memorydelta) / 1024} KB"
		elif abs(memorydelta) > 0:
			memorystring = f"{abs(memorydelta)} B"

		if memorydelta > 0:
			memorystring = f"Memory increased by {memorystring}."
		elif memorydelta < 0:
			memorystring = f"Memory decreased by {memorystring}."
		else:
			memorystring = "Memory didn't change."
		
		if abs(newmemory) > 1024 ** 3:
			memorystring = f"{memorystring} Total memory is currently {abs(newmemory) / 1024 ** 3} GB."
		elif abs(newmemory) > 1024 ** 2:
			memorystring = f"{memorystring} Total memory is currently {abs(newmemory) / 1024 ** 2} MB."
		elif abs(newmemory) > 1024:
			memorystring = f"{memorystring} Total memory is currently {abs(newmemory) / 1024} KB."
		elif abs(newmemory) > 0:
			memorystring = f"{memorystring} Total memory is currently {abs(newmemory)} B."

		outputmessage = f"{message} took {timedelta} seconds. {memorystring}"
		print(outputmessage)

		if record == True:
			self.recordedtime = newtime
			self.recordedmemory = newmemory

# perfmanager = perfAnnouncer()
# perfmanager.announce("Startup")

class Falloff_functions:
	def none(value, distance, range):
		return value

	def linear(value, distance, range):
		return value * (1 - ((1/(range + 1)) * distance))

	def linear_inv(value, distance, range):
		return value * ((1/(range + 1)) * (distance + 1))
		
	def cubic_hermine(value, distance, range):
		distance_ratio = 1 - (distance / (range + 1))
		falloff = distance_ratio * distance_ratio * (3 - 2 * distance_ratio)
		return value * falloff

	def quintic_hermite(value, distance, range):
		distance_ratio = 1 - (distance / (range + 1))
		falloff = distance_ratio * distance_ratio * distance_ratio * (distance_ratio * (distance_ratio * 6 - 15) + 10)
		return value * falloff


class Emitter:
	def __init__(self, parent_cell, radius, stat_name, power, multiplicative = False, falloff_function = Falloff_functions.none) -> None:
		self.pos_x = parent_cell.pos_x
		self.pos_y = parent_cell.pos_y
		self.parent_cell = parent_cell
		self.radius = radius
		self.stat_name = stat_name
		self.power = power
		self.multiplicative = multiplicative
		self.falloff_function = falloff_function
		
		self.targets = self.get_targets()
		self.distribute()

	def get_targets(self):
		targets = list()
		radius = round(self.radius)
		largest_x = radius
		radius2 = (self.radius + .2) ** 2
		if self.radius < 1:
			targets.append(self.parent_cell)
		else:
			for y in range(radius + 1):
				y2 = y ** 2
				for x in range(largest_x, -1, -1):
					if (x ** 2) + y2 <= radius2:
						for x_draw in range(self.pos_x - x, self.pos_x + x + 1):
							targets.append(self.parent_cell.parent_grid.get_cell(x_draw, self.pos_y + y))
							if y != 0:
								targets.append(self.parent_cell.parent_grid.get_cell(x_draw, self.pos_y - y))
						largest_x = x
						break
		return targets

	def distribute(self):
		for target in self.targets:
			if target != None:
				target.received_emitters.append(self)
	
	def apply(self, target_x, target_y):
		distance = math.sqrt((target_x - self.pos_x)**2 + (target_y - self.pos_y)**2)
		if self.radius != 0:
			output_value = self.falloff_function(self.power, distance, self.radius)
		else:
			output_value = self.power
		if self.multiplicative:
			output_value = output_value + 1
		return self.multiplicative, self.stat_name, output_value

	def remove_from_targets(self, recalculate = True):
		for target_cell in self.targets:
			if target_cell != None:
				target_cell.remove_received_emitter(self, recalculate)
		return self.targets
		
	def change_radius(self, new_radius, recalculate = True):
		recalculated_targets = list()
		if new_radius != self.radius:
			old_radius = self.radius
			self.radius = new_radius
			old_targets = self.remove_from_targets(recalculate = False)
			self.targets = self.get_targets()
			self.distribute()
			if new_radius < old_radius:
				recalculated_targets = old_targets
			elif new_radius > old_radius:
				recalculated_targets = self.targets
			if recalculate:
				for target in recalculated_targets:
					if target != None:
						target.calculate_stats()
		return recalculated_targets


class Gridcell:
	def __init__(self, pos_x, pos_y, parent_grid) -> None:
		self.pos_x = pos_x
		self.pos_y = pos_y
		self.parent_grid = parent_grid

		self.emitters = list()
		self.received_emitters = list()
		self.stats = dict()
	
	def reset_input(self):
		self.received_emitters = list()
		self.stats = dict()
	
	def add_emitter(self, radius, stat_name, power, multiplicative = False, falloff_function = Falloff_functions.none):
		self.emitters.append(Emitter(self, radius, stat_name, power, multiplicative, falloff_function))
	
	def remove_received_emitter(self, emitter, recalculate):
		try:
			self.received_emitters.remove(emitter)
			if recalculate:
				self.calculate_stats()
		except:
			pass
	
	def distribute_emitters(self):
		for emitter in self.emitters:
			emitter.distribute()
		
	def calculate_stats(self):
		self.stats = dict()
		stats_multiplicative = dict()
		for received_emitter in self.received_emitters:
			multiplicative, stat_name, value = received_emitter.apply(self.pos_x, self.pos_y)
			if multiplicative:
				if stat_name in stats_multiplicative:
					stats_multiplicative[stat_name] = stats_multiplicative[stat_name] * value
				else:
					stats_multiplicative[stat_name] = value
			elif not multiplicative:
				if stat_name in self.stats:
					self.stats[stat_name] = self.stats[stat_name] + value
				else:
					self.stats[stat_name] = value
		if len(stats_multiplicative) > 0:
			for stat_name in stats_multiplicative.keys():
				if stat_name in self.stats:
					self.stats[stat_name] = self.stats[stat_name] * value

	def __str__(self) -> str:
		return f"Position: ({self.pos_x}, {self.pos_y})"
    
class Grid:
	def __init__(self, size_x, size_y) -> None:
		self.size_x = size_x
		self.size_y = size_y
		self.array = list()
		self.array_flat = list()
		for y in range(size_y):
			self.array.append(list())
			for x in range(size_x):
				self.array[y].append(Gridcell(x, y, self))
				self.array_flat.append(self.array[y][x])
	
	def get_cell(self, pos_x, pos_y, rounding = "floor"):
		if rounding == "floor":
			pos_x = math.floor(pos_x)
			pos_y = math.floor(pos_y)
		elif rounding == "ceil":
			pos_x = math.ceil(pos_x)
			pos_y = math.ceil(pos_y)
		elif rounding == "nearest":
			pos_x = round(pos_x, 0)
			pos_y = round(pos_y, 0)

		if 0 > pos_x or pos_x >= self.size_x or 0 > pos_y or pos_y >= self.size_y:
			return None
		else:
			return self.array[pos_y][pos_x]
	
	def run_emitters(self, gridcells = None):
		if gridcells == None:
			gridcells = self.array_flat
		for gridcell in gridcells:
			gridcell.reset_input()
		for gridcell in gridcells:
			gridcell.distribute_emitters()
		for gridcell in gridcells:
			gridcell.calculate_stats()


# testgrid = grid(50, 50)

# perfmanager.announce("Grid creation")

# for y in testgrid.array:
# 	for x in y:
# 		x.get_targets(10)

# perfmanager.announce("Target lists with radius 10")