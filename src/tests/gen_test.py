"""
This program facilitates the creation of a regression test case as used by the
test module.  It uses the current readability algorithm to capture a benchmark
and construct a new test case.
"""
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

def gen_test(url, test_name, test_description):
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

USAGE = '''
usage: %s <url> <test name> <test description>
'''

def usage(prog_name):
    print(USAGE % prog_name)

def main():
    if len(sys.argv) != 4:
        usage(sys.argv[0])
        return
    url = sys.argv[1]
    test_name = sys.argv[2]
    test_description = sys.argv[3]
    result = gen_test(url, test_name, test_description)
    if not result:
        print('test was not fully generated')

if __name__ == '__main__':
    main()
