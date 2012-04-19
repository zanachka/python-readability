"""Process all of the samples and make sure that process without error."""
import os
import unittest

from readability_lxml.readability import Document


SAMPLES = os.path.join(os.path.dirname(__file__), 'samples')

sample_list = [
    'nyt.sample.html',
    'si-game.sample.html',
]


def load_sample(filename):
    """Helper to get the content out of the sample files"""
    return open(os.path.join(SAMPLES, filename)).read()


def test_processes():
    for article in sample_list:
        yield process_article, article


def process_article(article):
    sample = load_sample(article)
    doc = Document(sample)
    res = doc.summary()
    failed_msg = "Failed to process the article: " + article
    assert '<html><body><div><div class' == res[0:27], failed_msg
