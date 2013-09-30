# Pycept

## A python client for the CEPT API

This is a *very* minimal HTTP client library for the [CEPT API](https://cept.3scale.net/docs). Currently, it only converts words into standard distributed representations based on the bitmap values return by the [/term2bitmap](https://cept.3scale.net/docs#/term2bitmap) endpoint.

## CEPT Account

[Get CEPT API credentials here](https://cept.3scale.net/signup). This will give you a free trail. To upgrade to the "Beta Program", you'll need to go to the [admin page](https://cept.3scale.net/admin/) and click on "Change Plan" on the right, which will notify CEPT that you'd like expanded API access. **This is required for usage of pycept!** Pycept depends on expanded API endpoints unavailable to the free trial.

### Installation

    python setup.py install

### Usage

#### Retrieve SDR string for term

    import pycept
    ceptClient = pycept.Cept("your_app_id", "your_app_key")
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

    pycept.Cept("your_app_id", "your_app_key", cache_dir="./my-cache")

### Run Tests

    nosetests