#!/usr/bin/python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

sdict = {}

execfile('pycept/version.py', {}, sdict)

sdict.update({
    'name' : 'pycept',
    'description' : 'Python client for CEPT API',
    'url': 'http://github.com/numenta/pycept',
    'download_url' : 'https://pypi.python.org/packages/source/g/pycept/pycept-%s.tar.gz' % sdict['version'],
    'author' : 'Matthew Taylor',
    'author_email' : 'matt@numenta.org',
    'keywords' : ['sdr', 'nlp', 'cept'],
    'license' : 'MIT',
    'install_requires': [
        'requests',
        'nose',
        'coverage',
        'httpretty'],
    'test_suite': 'tests.unit',
    'packages' : ['pycept'],
    'classifiers' : [
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python'],
})

setup(**sdict)
