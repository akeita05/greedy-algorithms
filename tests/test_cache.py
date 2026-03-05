import sys
import os
sys.path.insert(0, os.path.dirname(__file__), '..', 'src'))

from cache_sim import fifo, lru, optff_fast as optff

def test_all_hits():
	"""all requests for the same item. only 1 miss"""
	reqs = [1, 1, 1, 1, 1]
	assert fifo(3, reqs) == 1, "FIFO: all same item"
	assert lru(3, reqs) == 1, "LRU: all same item"
	assert optff(3, reqs) == 1, "OPTFF: all same item"
	print("PASS test_all_hits")

def test_all_distinct_fits_in_cache():
	"""all distinct items, all fit in cache. every request is a miss once"""
	reqs = [1, 2, 3]
	assert fifo(3, reqs) == 3
	assert lru(3, reqs) == 3
	assert optff(3, reqs) == 3
	print("PASS test_all_distinct_fits_in_cache")

def test_fifo_basic_evict():
	reqs = [1, 2, 3, 1]
	assert fifo(2, reqs) == 4, f"Expected 4, got {fifo(2, reqs)}"
	print("PASS test_fifo_basic_evict")

def test_lru_basic_evict():
	reqs = [1, 2, 1, 3, 2]
	assert lru(2, reqs) == 4, f"Expected 4, got {lru(2, reqs)}"
	print(PASS test_lru_basic_eviction")

def test_optff_evicts_never_used():
	reqs = [1, 2, 3, 1]
	assert optff(2, reqs) == 3, f"Expected 3, got {optff(2, reqs)}"
	print("PASS test_optff_evicts_never_used")

def test_optff_leq_lru():
	"""optff shouldn't have more misses than lru on the same input"""
	test_cases = [
		(3, [1, 2, 3, 4, 1, 2, 3, 4]),
		(2, [1, 2, 1, 3, 2, 3, 4, 1]),
		(3, [1, 2, 3, 1, 4, 2, 3, 1, 4, 2, 3, 1, 4]),
		(4, [1, 2, 3, 4, 5, 1, 2, 3, 4, 5]),
	]

	for k, reqs in test_cases:
		o = optff(k, reqs)
		l = lru(k, reqs)
		assert o <= l, f"optff ({o}) > lru ({l}) for k = {k}, reqs = {reqs}"
	print("PASS test_optff_leq_lru")

def test_optff_leq_fifo():
	"""optff shouldn't have more misses than fifo"""
	test_cases = [
		(3, [1, 2, 3, 4, 1, 2, 3, 4]),
		(2, [1, 2, 1, 3, 2, 3, 4, 1]),
		(3, [1, 2, 3, 1, 4, 2, 3, 1, 4, 2, 3, 1, 4]),
	]

	for k, reqs in test_cases:
		o = optff(k, reqs)
		f = fifo(k, reqs)
		assert o <= f, f"optff ({o}) > fifo ({f}) for k = {k}, reqs = {reqs}"
	print("PASS test_optff_leq_fifo")

def test_lru_adversarial():
	"""classic adversarial sequence: lru > fifo > optff"""
	k = 3
	reqs = [1, 2, 3, 1, 4, 2, 3, 1, 4, 2, 3, 1, 4]
	f = fifo(k, reqs)
	l = lru(k, reqs)
	o = optff(k, reqs)
	assert l > f, f"expected lru ({l}) > fifo ({f})"
	assert f > o, f"expected fifo ({f}) > optff ({o})"
	assert f == 8 and l == 12 and o == 6, f"got fifo = {f} lru = {l} optff = {o}"
	print("PASS test_lru_adversarial")

def test_capacity_one():
	"""cache size of 1. every request should be a miss"""
	reqs = [1, 1, 2, 2, 3, 3]
	assert fifo(1, reqs) == 3
	assert lru(1, reqs) == 3
	assert optff(1, reqs) == 3
	print("PASS test_capacity_one")

def test_single_request():
	"""single request should always miss"""
	assert fifo(5, [42]) == 1
	assert lru(5, [42]) == 1
	assert optff(5, [42]) == 1
	print("PASS test_single_request")

def test_example_file():
	"""match the expected outcome from the example file"""
	reqs = [1,2,3,4,1,2,5,1,2,3,4,5,3,2,1,4,5,2,3,1]
	assert fifp(3, reqs) == 13, f"got {fifo(3, reqs)}"
	assert lru(3, reqs) == 17, f"got {lru(3, reqs)}"
	assert optff(3, reqs) == 11, f"got {optff(3, reqs)}"
	print("PASS test_example_file")

if __name__ == "__main__":
	tests = [
		test_all_hits,
		test_all_distinct_fits_in_cache,
		test_fifo_basic_evict,
		test_lru_basic_evict,
		test_optff_evicts_never_used,
		test_optff_leq_lru,
		test_optff_leq_fifo,
		test_lru_adversarial,
		test_capacity_one,
		test_single_request,
		test_example_file,
	]

	passed = 0
	failed = 0
	for t in tests:
		try:
			t()
			passed += 1
		except AssertionError as e:
			print(f"failed {t.__name__}: {e}")
			failed += 1
	print(f"\n{passed}/{passed+failed} tests passed.")
	if failed:
 		sys.exit(1)




