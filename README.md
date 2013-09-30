# Pycept
## A python client for the CEPT API

This is a *very* minimal HTTP client library for the [CEPT API](https://cept.3scale.net/docs). Currently, it only converts words into standard distributed representations based on the bitmap values return by the [/term2bitmap](https://cept.3scale.net/docs#/term2bitmap) endpoint.

### Installation

    python setup.py install

### Usage

#### Retrieve SDR string for term

    import pycept
    ceptClient = new pycept.Cept("your_app_id", "your_app_key")
    catSdr = ceptClient.getSdr("cat")

#### Retrieve bitmap representation of SDR for term

    catBitmap = ceptClient.getBitmap("cat")

#### Convert bitmap SDR to closest terms

    similarTerms = ceptClient.bitmapToTerms(
      catBitmap['width'], 
      catBitmap['height'], 
      catBitmap['positions']
    )

### Run Tests

    nosetests