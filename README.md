# Pycept [![Build Status](https://travis-ci.org/numenta/pycept.svg?branch=master)](https://travis-ci.org/numenta/pycept) [![Coverage Status](https://coveralls.io/repos/numenta/pycept/badge.png)](https://coveralls.io/r/numenta/pycept)

## A python client for the CEPT API

This is a *very* minimal HTTP client library for the [CEPT API](http://www.cortical.io/developers_apidocumentation.html).

## CEPT Account

[Get CEPT API credentials here](http://www.cortical.io/developers_apikey.html). This will give you a free trail.

### Installation

    python setup.py install

### Usage

#### Retrieve SDR string for term

    import pycept
    ceptClient = pycept.Cept("your_api_key")
    catSdr = ceptClient.getSdr("cat")

#### Retrieve bitmap representation of SDR for term

    catBitmap = ceptClient.getBitmap("cat")

#### Convert bitmap SDR to closest terms

    similarTerms = ceptClient.bitmapToTerms(
      catBitmap['width'], 
      catBitmap['height'], 
      catBitmap['positions']
    )

### Caching

To prevent duplicate requests to the CEPT API, pycept will cache SDR responses by default to `/tmp/pycept`. You can provide your own cache directory location by specifying a `cache_dir` value to the constructor:

    pycept.Cept("your_api_key", cache_dir="./my-cache")

### Run Tests

    nosetests
