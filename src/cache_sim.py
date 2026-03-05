import sys
from collections import OrderedDict, deque

def fifo(k: int, requests: list[int]) -> int:
# evicts the item that has been in the cache longest

	cache = set()
	queue = deque()
	misses = 0

	for req in requests:
		if req in cache:
		# if theres a cache hit, do nothing
			pass
		else:
		# cache miss
			misses += 1
			if len(cache) == k:
			# evict the oldest inserted item
				evict = queue.popleft()
				cache.remove(evict)
			cache.add(req)
			queue.append(req)

	return misses

def lru(k: int, requests: list[int]) -> int:
# eveict the item whose most recently accessed is the oldest

	cache = OrderedDict()
	misses = 0

	for req in requests:
		if req in cache:
		# if theres a cache hit, move it to the end
			cache.move_to_end(req)
		else:
		# cache miss
			misses += 1
			if len(cache) == k:
				# evict the least recently used
				cache.popitem(last=False)
			cache[req] = True

	return misses

def optff(k: int, requests: list[int]) -> int:
# evicts the item whose next request occurs farthest in the future

	m = len(requests)

	next_use = [float('inf')] * m
	last_seen = {}
	for i in range(m - 1, -1, -1):
		r = requests[i]
		if r in last_seen:
			next_use[i] = last_seen[r]
		last_seen[r] = i

	cache = set()
	misses = 0

	for i, req in enumerate(requests):
		if req in cache:
		# if theres a cache hit, do nothing
			pass
		else:
		# cache miss
			misses += 1
			if len(cache) == k:
			# evict item with farthest next use
			# for each cached item, find the next occurrence
				def future_use(item):
					for j in range(i + 1, m):
						if requests[j] == item:
							return j
					return float('inf')

				evict = max(cache, key=future_use)
				cache.remove(evict)
			cache.add(req)

	return misses

def optff_fast(k: int, requests: list[int]) -> int:

	m = len(requests)

	next_occurence = {}

	next_after = [float('inf')] * m
	last = {}
	for i in range(m - 1, -1, -1):
		r = requests[i]
		if r in last:
			next_after[i] = last[r]
		last[r] = i

	cache = set()
	misses = 0

	for i, req in enumerate(requests):
		if req in cache:
			pass
		else:
			misses += 1
			if len(cache) == k:
				# find the next use
				def next_use_after_i(item):
					for j in range(i + 1, m):
						if requests[j] == item:
							return j
					return float('inf')

				evict = max(cache, key=next_use_after_i)
				cache.remove(evict)
			cache.add(req)

	return misses

def parse_input(filename: str) -> tuple[int, list[int]]:
	with open(filename, 'r') as f:
		lines = f.read().split()

	if len(lines) < 2:
		raise ValueError("input file must contain at least k and m values.")

	k = int(lines[0])
	m = int(lines[1])

	if len(lines) < 2 + m:
		raise ValueError(f"expected {m} requests but found {len(lines) - 2}.")

	requests = [int(lines[2 + i]) for i in range(m)]
	return k, requests

def main(): 
	if len(sys.argv) != 2:
		sys.exit(1)

	filename = sys.argv[1]

	try:
		k, requests = parse_input(filename)
	except FileNotFoundError:
		print(f"error: file '{filename}' not found.")
		sys.exit(1)
	except ValueError as e:
		print(f"error parsing input: {e}")
		sys.exit(1)

	fifo_misses = fifo(k, requests)
	lru_misses = lru(k, requests)
	optff_misses = optff_fast(k, requests)

	print(f"FIFO  : {fifo_misses}")
	print(f"LRU   : {lru_misses}")
	print(f"OPTFF : {optff_misses}")

if __name__ == "__main__":
	main()
