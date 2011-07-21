"""
This module provides a regression test for results of running the readability
algorithm on a variety of different real-world examples.  For each page in the
test suite, a benchmark was captured that represents the current readability
results.  Note that these are not necessarily ideal results, just the ones used
as a benchmark.

This allows you to tweak and change the readability algorithm and see how it
changes existing results, hopefully for the better.

"""
import logging
import lxml.html
import lxml.html.diff
import os
import os.path
import re
import sys
import unittest
import yaml

from lxml.html import builder as B
from readability_lxml import readability
from readability_lxml import urlfetch


DIFF_SUFFIX = '-diff.html'
ORIGINAL_SUFFIX = '-orig.html'
READABLE_SUFFIX = '-rdbl.html'
RESULT_SUFFIX = '-result.html'
YAML_EXTENSION = '.yaml'

TESTDIR = os.path.dirname(__file__)
TEST_DATA_PATH = os.path.join(TESTDIR, 'regression_test_data')
TEST_OUTPUT_PATH = os.path.join(TESTDIR, 'regression_test_output')
TEST_SUMMARY_PATH = os.path.join(TEST_OUTPUT_PATH, 'index.html')

SUMMARY_CSS = '''
table, th, td {
    border: 1px solid black;
    border-collapse: collapse;
    font-family: Georgia, 'Times New Roman', serif;
}
table {
    margin: auto;
}
.skipped {
    color: gray;
}
td, th {
    font-size: 1.2em;
    border: 1px solid black;
    padding: 3px 7px 2px 7px;
}
th {
    font-size: 16px;
    text-align: left;
    padding-top: 5px;
    padding-bottom: 4px;
}
'''

READABILITY_CSS = '''
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

class ReadabilityTest:

    def __init__(
            self,
            dir_path,
            enabled,
            name,
            url,
            desc,
            notes,
            url_map,
            orig_path,
            rdbl_path
            ):
        self.dir_path = dir_path
        self.enabled = enabled
        self.name = name
        self.url = url
        self.desc = desc
        self.notes = notes
        self.url_map = url_map
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


def read_yaml(path):
    with open(path, 'r') as f:
        return yaml.load(f)


def make_path(dir_path, name, suffix):
    return os.path.join(dir_path, ''.join([name, suffix]))


def adjust_url_map(url_map):
    adjusted = dict()
    for k, v in url_map.items():
        adjusted[k] = os.path.join(TEST_DATA_PATH, v)
    return adjusted


def make_readability_test(dir_path, name, spec_dict):
    enabled = spec_dict.get('enabled', True)
    notes = spec_dict.get('notes', '')
    url_map = adjust_url_map(spec_dict.get('url_map', dict()))
    return ReadabilityTest(
            dir_path,
            enabled,
            name,
            spec_dict['url'],
            spec_dict['test_description'],
            notes,
            url_map,
            make_path(dir_path, name, ORIGINAL_SUFFIX),
            make_path(dir_path, name, READABLE_SUFFIX)
            )


def load_test_data(test):
    if test.enabled:
        orig = open(test.orig_path, 'r').read()
        rdbl = open(test.rdbl_path, 'r').read()
        return ReadabilityTestData(test, orig, rdbl)
    else:
        return None


def load_readability_tests(dir_path, files):
    yaml_files = [f for f in files if f.endswith(YAML_EXTENSION)]
    yaml_paths = [os.path.join(dir_path, f) for f in yaml_files]
    names = [re.sub('.yaml$', '', f) for f in yaml_files]
    spec_dicts = [read_yaml(p) for p in yaml_paths]
    return [
            make_readability_test(dir_path, name, spec_dict)
            for (name, spec_dict) in zip(names, spec_dicts)
            ]


def execute_test(test_data):
    if test_data is None:
        return None
    else:
        url = test_data.test.url
        fetcher = urlfetch.MockUrlFetch(test_data.test.url_map)
        doc = readability.Document(
                test_data.orig_html,
                url=url,
                urlfetch=fetcher
                )
        summary = doc.summary_with_metadata()
        diff = lxml.html.diff.htmldiff(test_data.rdbl_html, summary.html)
        return ReadabilityTestResult(test_data, summary.html, diff)


def element_string_lengths(elems):
    return [len(e.xpath('string()')) for e in elems]


class ResultSummary():

    def __init__(self, result):
        # logging.debug('diff: %s' % result.diff_html)
        doc = lxml.html.fragment_fromstring(result.diff_html)

        insertions = doc.xpath('//ins')
        insertion_lengths = element_string_lengths(insertions)
        self.insertions = sum(insertion_lengths)
        self.insertion_blocks = len(insertions)

        deletions = doc.xpath('//del')
        deletion_lengths = element_string_lengths(deletions)
        self.deletions = sum(deletion_lengths)
        self.deletion_blocks = len(deletions)
        pass


def make_summary_row(test, result):
    def data(suffix):
        return os.path.abspath(os.path.join(TEST_DATA_PATH, test.name + suffix))
    def output(suffix):
        return test.name + suffix
    if test.enabled:
        s = ResultSummary(result)
        return B.TR(
                B.TD(test.name),
                B.TD('%d (%d)' % (s.insertions, s.insertion_blocks)),
                B.TD('%d (%d)' % (s.deletions, s.deletion_blocks)),
                B.TD(
                    B.A('original', href = data(ORIGINAL_SUFFIX)),
                    ' ',
                    B.A('benchmark', href = output(READABLE_SUFFIX)),
                    ' ',
                    B.A('result', href = output(RESULT_SUFFIX)),
                    ' ',
                    B.A('diff', href = output(DIFF_SUFFIX))
                    ),
                B.TD(test.notes)
                )
    else:
        return B.TR(
                B.CLASS('skipped'),
                B.TD('%s (SKIPPED)' % test.name),
                B.TD('N/A'),
                B.TD('N/A'),
                B.TD('N/A'),
                B.TD(test.notes)
                )


def make_summary_doc(tests_w_results):
    tbody = B.TBODY(
            B.TR(
                B.TH('Test Name'),
                B.TH('Inserted (in # of blocks)'),
                B.TH('Deleted (in # of blocks)'),
                B.TH('Links'),
                B.TH('Notes')
                )
            )
    for (test, result) in tests_w_results:
        row = make_summary_row(test, result)
        tbody.append(row)
    return B.HTML(
            B.HEAD(
                B.TITLE('Readability Test Summary'),
                B.STYLE(SUMMARY_CSS, type = 'text/css')
                ),
            B.BODY(
                B.TABLE(
                    tbody
                    )
                )
            )


def write_summary(path, tests_w_results):
    doc = make_summary_doc(tests_w_results)
    with open(path, 'w') as f:
        f.write(lxml.html.tostring(doc))


def add_css(doc):
    style = B.STYLE(READABILITY_CSS, type = 'text/css')
    head = B.HEAD(style, content = 'text/html; charset=utf-8')
    doc.insert(0, head)


def write_output_fragment(fragment, output_dir_path, test_name, suffix):
    doc = lxml.html.document_fromstring(fragment)
    add_css(doc)
    html = lxml.html.tostring(doc)
    file_name = ''.join([test_name, suffix])
    path = os.path.join(output_dir_path, file_name)
    with open(path, 'w') as f:
        f.write(html)


def write_result(output_dir_path, result):
    test_name = result.test_data.test.name
    specs = [
            (result.test_data.rdbl_html, READABLE_SUFFIX),
            (result.diff_html, DIFF_SUFFIX),
            (result.result_html, RESULT_SUFFIX)
            ]
    for (html, suffix) in specs:
        write_output_fragment(html, output_dir_path, test_name, suffix)


def print_test_info(test):
    name_string = '%s' % test.name
    if test.enabled:
        skipped = ''
    else:
        skipped = ' (SKIPPED)'
    print('%20s: %s%s' % (name_string, test.desc, skipped))

def run_readability_tests():
    files = os.listdir(TEST_DATA_PATH)
    tests = load_readability_tests(TEST_DATA_PATH, files)
    test_datas = [load_test_data(t) for t in tests]
    results = [execute_test(t) for t in test_datas]
    for (test, result) in zip(tests, results):
        print_test_info(test)
        if result:
            write_result(TEST_OUTPUT_PATH, result)
    write_summary(TEST_SUMMARY_PATH, zip(tests, results))

def main():
    logging.basicConfig(level = logging.DEBUG)
    if len(sys.argv) > 1 and sys.argv[1] == 'unittest':
        del sys.argv[1]
        return unittest.main()
    run_readability_tests()


if __name__ == '__main__':
    main()
