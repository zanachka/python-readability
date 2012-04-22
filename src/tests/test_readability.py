import os
import unittest

from lxml.html import document_fromstring
from lxml.html.diff import htmldiff

from helpers import load_regression_data
from helpers import REGRESSION_DATA
from readability_lxml.readability import Document
from readability_lxml import readability as r
from readability_lxml import urlfetch


class TestReadabilityDocument(unittest.TestCase):
    """Test the Document parser."""

    def test_none_input_raises_exception(self):
        """Feeding a None input to the document should blow up."""

        doc = None
        self.assertRaises(ValueError, Document, doc)


class TestFindBaseUrl(unittest.TestCase):

    def setUp(self):
        self.longMessage = True

    def _assert_url(self, url, expected_base_url, msg = None):
        actual_base_url = r.find_base_url(url)
        self.assertEqual(expected_base_url, actual_base_url, msg)

    def _run_urls(self, specs):
        """
        Asserts expected results on a sequence of specs, where each spec is a
        pair: (URL, expected base URL).
        """
        for spec in specs:
            url = spec[0]
            expected = spec[1]
            if len(spec) > 2:
                msg = spec[2]
            else:
                msg = None
            self._assert_url(url, expected, msg)

    def test_none(self):
        self._assert_url(None, None)

    def test_no_change(self):
        url = 'http://foo.com/article'
        self._assert_url(url, url)

    def test_extension_stripping(self):
        specs = [
                (
                'http://foo.com/article.html',
                'http://foo.com/article',
                'extension should be stripped'
                ),
                (
                'http://foo.com/path/to/article.html',
                'http://foo.com/path/to/article',
                'extension should be stripped'
                ),
                (
                'http://foo.com/article.123not',
                'http://foo.com/article.123not',
                '123not is not extension'
                ),
                (
                'http://foo.com/path/to/article.123not',
                'http://foo.com/path/to/article.123not',
                '123not is not extension'
                )
                ]
        self._run_urls(specs)

    def test_ewcms(self):
        self._assert_url(
                'http://www.ew.com/ew/article/0,,20313460_20369436,00.html',
                'http://www.ew.com/ew/article/0,,20313460_20369436'
                )

    def test_page_numbers(self):
        specs = [
                (
                'http://foo.com/page5.html',
                'http://foo.com',
                'page number should be stripped'
                ),
                (
                'http://foo.com/path/to/page5.html',
                'http://foo.com/path/to',
                'page number should be stripped'
                ),
                (
                'http://foo.com/article-5.html',
                'http://foo.com/article',
                'page number should be stripped'
                )
                ]
        self._run_urls(specs)

    def test_numbers(self):
        specs = [
                (
                'http://foo.com/5.html',
                'http://foo.com',
                'number should be stripped'
                ),
                (
                'http://foo.com/path/to/5.html',
                'http://foo.com/path/to',
                'number should be stripped'
                )
                ]
        self._run_urls(specs)

    def test_index(self):
        specs = [
                (
                'http://foo.com/index.html',
                'http://foo.com',
                'index should be stripped'
                ),
                (
                'http://foo.com/path/to/index.html',
                'http://foo.com/path/to',
                'index should be stripped'
                )
                ]
        self._run_urls(specs)

    def test_short(self):
        specs = [
                (
                'http://foo.com/en/1234567890',
                'http://foo.com/1234567890',
                'short segment should be stripped'
                ),
                (
                'http://foo.com/en/de/1234567890',
                'http://foo.com/en/1234567890',
                'short segment should be stripped'
                )
                ]
        self._run_urls(specs)


class TestMultiPageHelpers(unittest.TestCase):

    def test_find_next_page_url(self):
        """Verify we can find a next page url in the html body"""
        html = """
            <html><body><a href="/?page=2">next</a></body></html>
        """
        from lxml.html import document_fromstring
        doc = document_fromstring(html)

        res = r.find_next_page_url(set(), None, doc)
        self.assertEqual('/?page=2', res,
            'Should find out page 2 url in the body.')


class TestFindNextPageLink(unittest.TestCase):

    def _test_page(self, url, html_path, expected):
        html = load_regression_data(html_path)
        doc = r.parse(html, url)
        parsed_urls = {url}
        actual = r.find_next_page_url(parsed_urls, url, doc)
        self.assertEqual(expected, actual)

    def test_basic(self):
        self._test_page(
                'http://basic.com/article.html',
                'basic-multi-page.html',
                'http://basic.com/article.html?pagewanted=2'
                )

    def test_nytimes(self):
        # This better work for the New York Times.
        self._test_page(
                'http://www.nytimes.com/2011/07/10/magazine/the-dark-art-of-breaking-bad.html',
                'nytimes-next-page.html',
                'http://www.nytimes.com/2011/07/10/magazine/the-dark-art-of-breaking-bad.html?pagewanted=2&_r=1'
                )


class TestMultiPage(unittest.TestCase):
    """
    Tests the full path of generating a readable page for a multi-page article.
    The test article is very simple, so this test should be resilient to tweaks
    of the algorithm.
    """

    def _make_basic_urldict(self):
        url_fmt = 'http://basic.com/article.html?pagewanted=%s'
        file_fmt = 'basic-multi-page-%s.html'

        pairs = [(url_fmt % i, os.path.join(REGRESSION_DATA, file_fmt % i)) for i in ['2', '3']]
        return dict(pairs)

    def test_basic(self):
        html = load_regression_data('basic-multi-page.html')
        urldict = self._make_basic_urldict()
        fetcher = urlfetch.MockUrlFetch(urldict)
        options = {
                'url': 'http://basic.com/article.html',
                'multipage': True,
                'urlfetch': fetcher
                }
        doc = Document(html, **options)
        res = doc.summary_with_metadata()

        self.assertIn('Page 2', res.html, 'Should find the page 2 heading')
        self.assertIn('Page 3', res.html, 'Should find the page 3 heading')

        expected_html = load_regression_data('basic-multi-page-expected.html')
        diff_html = htmldiff(expected_html, res.html)
        diff_doc = document_fromstring(diff_html)

        insertions = diff_doc.xpath('//ins')
        deletions = diff_doc.xpath('//del')

        if len(insertions) != 0:
            for i in insertions:
                print('unexpected insertion: %s' % i.xpath('string()'))
            self.fail('readability result does not match expected')

        if len(deletions) != 0:
            for i in deletions:
                print('unexpected deletion: %s' % i.xpath('string()'))
            self.fail('readability result does not match expected')


class TestIsSuspectedDuplicate(unittest.TestCase):

    def setUp(self):
        super(TestIsSuspectedDuplicate, self).setUp()
        html = load_regression_data('duplicate-page-article.html')
        self._article = r.fragment_fromstring(html)

    def test_unique(self):
        html = load_regression_data('duplicate-page-unique.html')
        page = r.fragment_fromstring(html)
        self.assertFalse(r.is_suspected_duplicate(self._article, page))

    def test_duplicate(self):
        html = load_regression_data('duplicate-page-duplicate.html')
        page = r.fragment_fromstring(html)
        self.assertTrue(r.is_suspected_duplicate(self._article, page))
