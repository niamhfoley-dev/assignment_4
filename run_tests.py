import unittest

if __name__ == "__main__":
    # Discover and run all tests in the "tests" folder
    loader = unittest.TestLoader()
    suite = loader.discover('tests')

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
