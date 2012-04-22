"""Process all of the samples and make sure that process without error."""
import os
import unittest

from helpers import load_sample
from readability_lxml.readability import Document

sample_list = [
    'nyt.sample.html',
    'si-game.sample.html',
]


def test_processes():
    for article in sample_list:
        yield process_article, article


def process_article(article):
    sample = load_sample(article)
    doc = Document(sample)
    res = doc.summary()
    failed_msg = "Failed to process the article: " + res[0:37]
    assert '<html><body id="page"><div><div class' == res[0:37], failed_msg
