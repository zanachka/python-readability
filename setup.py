#!/usr/bin/env python
from setuptools import setup, find_packages

version = "0.2.5"
install_requires = [
    "chardet",
    "lxml",
]
tests_require = [
    'coverage',
    'nose',
    'pep8',
]

setup(
    name="readability-lxml",
    version=version,
    author="Yuri Baburov",
    author_email="burchik@gmail.com",
    description="fast python port of arc90's readability tool",
    keywords='readable read parse html document readability',
    long_description=open("README").read(),
    license="Apache License 2.0",
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    url="http://github.com/buriy/python-readability",
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    extras_require={'test': tests_require},
    test_suite = "nose.collector",
    entry_points={
        'console_scripts':
            ['readability=readability_lxml:client.main']
    },

)
