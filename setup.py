#!/usr/bin/env python
from setuptools import setup, find_packages

version = "0.3.0"
install_requires = [
    "chardet",
    "lxml",
]
tests_require = [
    'coverage',
    'nose',
    'pep8',
    'PyYaml',
]


setup(
    name="readability-lxml",
    version=version,
    author="Yuri Baburov",
    author_email="burchik@gmail.com",
    description="fast python port of arc90's readability tool",
    keywords='readable read parse html document readability',
    long_description=open("README.rst").read(),
    license="Apache License 2.0",
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    url="http://github.com/buriy/python-readability",
    packages=find_packages('src', exclude=["*.tests", "*.tests.*"]),
    package_dir = {'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={'test': tests_require},
    test_suite = "nose.collector",
    entry_points={
        'console_scripts':
            ['readability=readability_lxml:client.main']
    },
)
