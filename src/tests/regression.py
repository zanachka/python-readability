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


DIFF_SUFFIX = '-diff.html'
ORIGINAL_SUFFIX = '-orig.html'
READABLE_SUFFIX = '-rdbl.html'
RESULT_SUFFIX = '-result.html'
YAML_EXTENSION = '.yaml'

TESTDIR = os.path.dirname(__file__)
TEST_DATA_PATH = os.path.join(TESTDIR, 'test_data')
TEST_OUTPUT_PATH = os.path.join(TESTDIR, 'test_output')


class ReadabilityTest:

    def __init__(self, dir_path, enabled, name, desc, orig_path, rdbl_path):
        self.dir_path = dir_path
        self.enabled = enabled
        self.name = name
        self.desc = desc
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

def make_readability_test(dir_path, name, spec_dict):
    if 'enabled' in spec_dict:
        enabled = spec_dict['enabled']
    else:
        enabled = True
    return ReadabilityTest(
            dir_path,
            enabled,
            name,
            spec_dict['test_description'],
            make_path(dir_path, name, ORIGINAL_SUFFIX),
            make_path(dir_path, name, READABLE_SUFFIX)
            )


def load_test_data(test):
    orig = open(test.orig_path, 'r').read()
    rdbl = open(test.rdbl_path, 'r').read()
    return ReadabilityTestData(test, orig, rdbl)


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
    doc = readability.Document(test_data.orig_html)
    summary = doc.summary_with_metadata()
    benchmark_doc = (test_data.rdbl_html, 'benchmark')
    result_doc = (summary.html, 'result')
    # diff = lxml.html.diff.html_annotate([benchmark_doc, result_doc])
    diff = lxml.html.diff.htmldiff(test_data.rdbl_html, summary.html)
    # diff = test_data.orig_html
    return ReadabilityTestResult(test_data, summary.html, diff)


CSS = '''
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

def add_css(doc):
    style = B.STYLE(CSS, type = 'text/css')
    head = B.HEAD(style)
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
    for test in tests:
        print_test_info(test)
        if test.enabled:
            test_data = load_test_data(test)
            result = execute_test(test_data)
            write_result(TEST_OUTPUT_PATH, result)

def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'unittest':
        del sys.argv[1]
        return unittest.main()
    run_readability_tests()


if __name__ == '__main__':
    main()
