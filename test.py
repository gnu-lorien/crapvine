import unittest

if __name__ == "__main__":
	from crapvine.test.test_traits import suite
	runner = unittest.TextTestRunner()
	runner.run(suite())
