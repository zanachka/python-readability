"""
This program facilitates the creation of a regression test case as used by the
test module.  It uses the current readability algorithm to capture a benchmark
and construct a new test case.

"""
import argparse
import errno
import os
import os.path
import readability
import sys
import test
import urllib2
import yaml

OVERWRITE_QUESTION = '%s exists; overwrite and continue (y/n)? '

def y_or_n(question):
    while True:
        response = raw_input(question).strip()
        if len(response) > 0:
            return response[0] in ['y', 'Y']

def write_file(test_name, suffix, data):
    path = os.path.join(test.TEST_DATA_PATH, test_name + suffix)
    mode = 0644
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode)
    except OSError as e:
        if e.errno == errno.EEXIST:
            if y_or_n(OVERWRITE_QUESTION % path):
                fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, mode)
            else:
                return False
        else:
            raise e
    f = os.fdopen(fd, 'w')
    f.write(data)
    return True


def gen_test(url, test_name, test_description, gen_yaml = True):
    if gen_yaml:
        spec_dict = {'url': url, 'test_description': test_description}
        spec = yaml.dump(spec_dict, default_flow_style = False)
        if not write_file(test_name, test.YAML_EXTENSION, spec):
            return False
    orig = urllib2.urlopen(url).read()
    if not write_file(test_name, test.ORIGINAL_SUFFIX, orig):
        return False

    rdbl_doc = readability.Document(orig)
    summary = rdbl_doc.summary()
    if not write_file(test_name, test.READABLE_SUFFIX, summary.html):
        return False

    return True

DESCRIPTION = 'Create a readability regression test case.'

def main():
    parser = argparse.ArgumentParser(description = DESCRIPTION)
    parser.add_argument(
            '--no-yaml',
            dest = 'no_yaml',
            action = 'store_const',
            const = True,
            default = False,
            help = 'if set, no yaml file will be generated'
            )
    parser.add_argument(
            'url',
            metavar = 'url',
            help = 'the url for which to generate a test'
            )
    parser.add_argument(
            'test_name',
            metavar = 'test-name',
            help = 'the name of the test'
            )
    parser.add_argument(
            'test_description',
            metavar = 'test-description',
            help = 'the description of the test'
            )
    args = parser.parse_args()
    result = gen_test(
            args.url,
            args.test_name,
            args.test_description,
            gen_yaml = not args.no_yaml
            )
    if not result:
        print('test was not fully generated')

if __name__ == '__main__':
    main()
