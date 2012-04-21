import lxml.html
import lxml.html.diff
import os
import os.path
import readability
import sys
import unittest
import yaml

from lxml.html import builder as B


ORIGINAL_SUFFIX = '-orig.html'
READABLE_SUFFIX = '-rdbl.html'
RESULT_SUFFIX = '-result.html'

TEST_DATA_PATH = 'test_data'
TEST_OUTPUT_PATH = 'test_output'


class ReadabilityTest:

    def __init__(self, dir_path, name, orig_path, rdbl_path):
        self.dir_path = dir_path
        self.name = name
        self.orig_path = orig_path
        self.rdbl_path = rdbl_path


class ReadabilityTestData:

    def __init__(self, test, orig_html, rdbl_html):
        self.test = test
        self.orig_html = orig_html
        self.rdbl_html = rdbl_html


class ReadabilityTestResult:

    def __init__(self, test_data, result_html, diff_html):
        self.test_data = test_data
        self.result_html = result_html
        self.diff_html = diff_html


def strip_with_suffix(suffix, files):
    filtered = [x for x in files if x.endswith(suffix)]
    stripped = [x.replace(suffix, '') for x in filtered]
    return set(stripped)


def check_missing(lhs, rhs, rhs_description):
    only_lhs = lhs.difference(rhs)
    if len(only_lhs) != 0:
        is_are = 'is' if len(only_lhs) == 1 else 'are'
        file_files = 'file' if len(only_lhs) == 1 else 'files'
        s = ('(%s) %s missing %s %s' %
                (', '.join(only_lhs), is_are, rhs_description, file_files)
                )
        raise Exception(s)


def resolve_test_names(files):
    orig_names = strip_with_suffix(ORIGINAL_SUFFIX, files)
    rdbl_names = strip_with_suffix(READABLE_SUFFIX, files)
    check_missing(orig_names, rdbl_names, READABLE_SUFFIX)
    check_missing(rdbl_names, orig_names, ORIGINAL_SUFFIX)
    return orig_names


def make_path(dir_path, name, suffix):
    return os.path.join(dir_path, ''.join([name, suffix]))


def make_readability_test(dir_path, name):
    return ReadabilityTest(
            dir_path,
            name,
            make_path(dir_path, name, ORIGINAL_SUFFIX),
            make_path(dir_path, name, READABLE_SUFFIX)
            )


def load_test_data(test):
    orig = open(test.orig_path, 'r').read()
    rdbl = open(test.rdbl_path, 'r').read()
    return ReadabilityTestData(test, orig, rdbl)


def load_readability_tests(dir_path, files):
    names = resolve_test_names(files)
    return [make_readability_test(dir_path, name) for name in names]


def execute_test(test_data):
    doc = readability.Document(test_data.orig_html)
    summary = doc.summary()
    benchmark_doc = (test_data.rdbl_html, 'benchmark')
    result_doc = (summary.html, 'result')
    # diff = lxml.html.diff.html_annotate([benchmark_doc, result_doc])
    diff = lxml.html.diff.htmldiff(test_data.rdbl_html, summary.html)
    # diff = test_data.orig_html
    return ReadabilityTestResult(test_data, summary.html, diff)


DIFF_CSS = '''
    #article {
        margin: 0 auto;
        max-width: 705px;
        min-width: 225px;
        font-family: Georgia, 'Times New Roman', serif;
        font-size: 19px;
        line-height: 29px;
    }

    #article p {
        font-size: 19px;
        line-height: 29px;
        margin: 19px 0px 19px 0px;
    }

    ins {
        background-color: #C6F7C3;
        text-decoration: none;
    }

    ins img {
        border-width: 3px;
        border-style: dotted;
        border-color: #51B548;
    }

    del {
        background-color: #F7C3C3;
        text-decoration: none;
    }

    del img {
        border-width: 3px;
        border-style: dotted;
        border-color: #D12626;
    }
'''


def add_diff_css(doc):
    style = B.STYLE(DIFF_CSS, type = 'text/css')
    head = B.HEAD(style)
    doc.insert(0, head)


def write_result(output_dir_path, result):
    doc = lxml.html.document_fromstring(result.diff_html)
    add_diff_css(doc)
    output_file = ''.join([result.test_data.test.name, RESULT_SUFFIX])
    output_path = os.path.join(output_dir_path, output_file)
    with open(output_path, 'w') as f:
        f.write(lxml.html.tostring(doc))


def run_readability_tests():
    files = os.listdir(TEST_DATA_PATH)
    tests = load_readability_tests(TEST_DATA_PATH, files)
    for test in tests:
        test_data = load_test_data(test)
        result = execute_test(test_data)
        write_result(TEST_OUTPUT_PATH, result)


class TestStripWithSuffix(unittest.TestCase):

    def test_no_files(self):
        expected = set()
        actual = strip_with_suffix('.test', [])
        self.assertEqual(expected, actual)

    def test_files(self):
        expected = {'foo', 'bar'}
        actual = strip_with_suffix('.test', ['foo.test', 'bar.test'])
        self.assertEqual(expected, actual)

    def test_extra_files(self):
        expected = {'foo', 'bar'}
        actual = strip_with_suffix('.test', ['foo.test', 'bar.test', 'extra'])
        self.assertEqual(expected, actual)


class TestResolveTestNames(unittest.TestCase):

    def test_no_files(self):
        expected = set()
        actual = resolve_test_names([])
        self.assertEqual(expected, actual)

    def test_files(self):
        expected = {'foo', 'bar'}
        files = [
                'foo-orig.html',
                'foo-rdbl.html',
                'bar-orig.html',
                'bar-rdbl.html'
                ]
        actual = resolve_test_names(files)
        self.assertEqual(expected, actual)

    def test_missing_rdbl(self):
        files = [
                'foo-orig.html',
                'foo-rdbl.html',
                'bar-orig.html'
                ]
        with self.assertRaisesRegexp(
                Exception,
                r'\(bar\) is missing -rdbl.html file'
                ):
            resolve_test_names(files)

    def test_missing_multiple_rdbl(self):
        files = [
                'foo-orig.html',
                'bar-orig.html'
                ]
        with self.assertRaisesRegexp(
                Exception,
                r'\(foo, bar\) are missing -rdbl.html files'
                ):
            resolve_test_names(files)

    def test_missing_orig(self):
        files = [
                'foo-orig.html',
                'foo-rdbl.html',
                'bar-rdbl.html'
                ]
        with self.assertRaisesRegexp(
                Exception,
                r'\(bar\) is missing -orig.html file'
                ):
            resolve_test_names(files)

    def test_missing_multiple_orig(self):
        files = [
                'foo-rdbl.html',
                'bar-rdbl.html'
                ]
        with self.assertRaisesRegexp(
                Exception,
                r'\(foo, bar\) are missing -orig.html files'
                ):
            resolve_test_names(files)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'unittest':
        del sys.argv[1]
        return unittest.main()
    run_readability_tests()


if __name__ == '__main__':
    main()
