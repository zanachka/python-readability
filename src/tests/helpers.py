import os


SAMPLES = os.path.join(os.path.dirname(__file__), 'samples')
REGRESSION_DATA = os.path.join(os.path.dirname(__file__), 'regression_test_data')


def load_sample(filename):
    """Helper to get the content out of the sample files"""
    return open(os.path.join(SAMPLES, filename)).read()


def load_regression_data(filename):
    """Get the content of a test_data regression file"""
    return open(os.path.join(REGRESSION_DATA, filename)).read()
