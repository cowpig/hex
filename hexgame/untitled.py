class Tracker(object):
	def __init__(self):
		self.things = {}

	def allocate(self, name):
		if not name in self.things:
			self.things[name] = [0]
			return "{}0".format(name)
		else:
			smallest = smallest_missing(self.things[name])
			self.things[name].append(smallest)
			return "{}{}".format(name, smallest)

	def deallocate(self, full_name):
		i = -1
		while full_name[i].isdigit():
			i -= 1

		basename = full_name[:i]
		print basename, i, full_name
		number = int(full_name[i:])

		print basename, number
		self.things[basename].remove(number)

		raise Exception("Invalid input")


def smallest_missing(list_of_ints):
	set_of_ints = set(list_of_ints)
	i = 0
	while i in set_of_ints:
		i += 1
	return i

assert(smallest_missing([1,2,3,4,5]) == 0)
assert(smallest_missing([0,1,3,4,5]) == 2)
assert(smallest_missing([-1, 0,1,3,4,5]) == 2)

track = Tracker()
assert(track.allocate('apibox') == 'apibox0')
assert(track.allocate('apibox') == "apibox1")
assert(track.allocate('apibox') == "apibox2")
track.deallocate('apibox1')
assert(track.allocate('apibox') == "apibox1")
