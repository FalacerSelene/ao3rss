#! /usr/bin/env python

from setuptools import setup

setup(
    name='ao3rss',
    version='1.0.0',
    url='https://github.com/FalacerSelene/ao3rss',
    scripts=['ao3rss'],
    license='Unlicense',
    install_requires=[
        'flask',
        'bs4',
        'requests',
    ],
)
