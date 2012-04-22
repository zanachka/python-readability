import os
import unittest

from readability_lxml.readability import Document


SAMPLES = os.path.join(os.path.dirname(__file__), 'samples')


def load_sample(filename):
    """Helper to get the content out of the sample files"""
    return open(os.path.join(SAMPLES, filename)).read()


class TestArticleOnly(unittest.TestCase):
    """The option to not get back a full html doc should work

    Given a full html document, the call can request just divs of processed
    content. In this way the developer can then wrap the article however they
    want in their own view or application.

    """

    def test_si_sample(self):
        """Using the si sample, load article with only opening body element"""
        sample = load_sample('si-game.sample.html')
        doc = Document(
            sample,
            url='http://sportsillustrated.cnn.com/baseball/mlb/gameflash/2012/04/16/40630_preview.html')
        res = doc.summary()
        self.assertEqual('<html><body id="page"><div><div class', res[0:37])

    def test_si_sample_html_partial(self):
        """Using the si sample, make sure we can get the article alone."""
        sample = load_sample('si-game.sample.html')
        doc = Document(sample, url='http://sportsillustrated.cnn.com/baseball/mlb/gameflash/2012/04/16/40630_preview.html')
        res = doc.summary(enclose_with_html_tag=False)
        self.assertEqual('<div id="page"><div class="', res[0:27])

    def test_si_sample_full_summary(self):
        """We should parse the doc and get a full summary with confidence"""
        sample = load_sample('si-game.sample.html')
        doc = Document(sample, url='http://sportsillustrated.cnn.com/baseball/mlb/gameflash/2012/04/16/40630_preview.html')
        res = doc.summary_with_metadata(enclose_with_html_tag=False)
        self.assertTrue(hasattr(res, 'html'),
            'res should have an html attrib')
        self.assertTrue(hasattr(res, 'confidence'),
            'res should have an html attrib')
        self.assertTrue(hasattr(res, 'title'),
                'res should have an titile attrib')
        self.assertTrue(hasattr(res, 'short_title'),
            'res should have an short_title attrib')
        self.assertEqual('<div id="page"><div class="', res.html[0:27])
        self.assertTrue(res.confidence > 50,
            'The confidence score should be larger than 50: ' + str(res.confidence))
