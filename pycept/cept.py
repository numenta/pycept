# The MIT License (MIT)
#
# Copyright (c) 2013 Numenta, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import hashlib
import os
import json
import requests
import urllib



DEFAULT_BASE_URL = "http://numenta.cortical.io:80/rest/"
DEFAULT_RETINA = "eng_syn"
DEFAULT_CACHE_DIR = "/tmp/pycept"
DEFAULT_VERBOSITY = 0

RETINA_SIZES = {
  "eng_syn": {
    "width": 64,
    "height": 64
  },
  "eng_syn_morph": {
    "width": 64,
    "height": 64
  },
  "eng_gen": {
    "width": 128,
    "height": 128
  }
}



class Cept(object):
  """
  Main class for the Cept API.
  """

  def __init__(self,
               apiKey=None,
               baseUrl=DEFAULT_BASE_URL,
               retina=DEFAULT_RETINA,
               cacheDir=DEFAULT_CACHE_DIR,
               verbosity=DEFAULT_VERBOSITY):
    if apiKey:
      self.apiKey = apiKey
    else:
      self.apiKey = os.environ["CEPT_API_KEY"]

    self.apiUrl = baseUrl
    self.retina = retina
    # Create the cache directory if necessary.
    cacheDir = os.path.join(cacheDir, retina)
    if not os.path.exists(cacheDir):
      os.makedirs(cacheDir)
    self.cacheDir = cacheDir
    self.verbosity = verbosity


  def tokenize(self, text):
    """Get a list of sentence tokens from a text string.

    Example:
      >>> c = cept.Cept(apiKey)
      >>> c.tokenize('The cow jumped over the moon. Then it ran to the other '
                     'side. And then the sun came up.')
      [[u'cow', u'jumped', u'moon'], [u'ran', u'other side'], [u'sun', u'came']]

    :param text: string to tokenize
    :returns: a list of lists where each inner list contains the string tokens
        from a sentence in the input text
    """
    cachePath = os.path.join(self.cacheDir,
                  "tokenize-" + hashlib.sha224(text).hexdigest() + ".json")
    if os.path.exists(cachePath):
      with open(cachePath) as cacheFile:
        response = json.load(cacheFile)
    else:
      url = self._buildUrl("text/tokenize")
      headers = {"Content-Type": "application/json"}
      response = requests.post(url, headers=headers, data=text).json()
      with open(cachePath, 'w') as f:
        json.dump(response, f)

    return [sentence.split(",") for sentence in response]


  def getBitmap(self, term):
    url = self._buildUrl("text")

    # Create a cache location for each term, where it will either be read in
    # from or cached within if we have to go to the CEPT API to get the SDR.
    cachePath = os.path.join(self.cacheDir,
                  "bitmap-" + hashlib.sha224(term).hexdigest() + ".json")

    # Get it from the cache if it's there
    if os.path.exists(cachePath):
      sdr = json.loads(open(cachePath).read())

    # Get it from CEPT API if it's not cached
    else:
      if self.verbosity > 0:
        print "\tfetching %s from CEPT API" % term
      headers = {"Content-Type": "application/json"}
      response = requests.post(url,
                               headers=headers,
                               data=term,
                               auth=(self.apiKey, ""))
      responseObj = json.loads(response.content)
      if type(responseObj) == list:
        sdr = responseObj[0]
      else:
        sdr = {"positions": []}

      if (not "width" in sdr) or (not "height" in sdr):
        size = RETINA_SIZES[self.retina]
        sdr["width"] = size["width"]
        sdr["height"] = size["height"]

      # attach the sparsity for reference
      total = float(sdr["width"]) * float(sdr["height"])
      on = len(sdr["positions"])
      sparsity = round((on / total) * 100)
      sdr["sparsity"] = sparsity

      # write to cache
      with open(cachePath, 'w') as f:
        f.write(json.dumps(sdr))

    return sdr


  def getSdr(self, term):
    return self._bitmapToSdr(self.getBitmap(term))


  def compare(self, bitmap1, bitmap2):
    """
    Given two bitmaps, return their comparison, i.e. a dict with the CEPT
    comparison metrics.

    Here's an example return dict:

      {
        "Cosine-Similarity": 0.6666666666666666,
        "Euclidean-Distance": 0.3333333333333333,
        "Jaccard-Distance": 0.5,
        "Overlapping-all": 6,
        "Overlapping-left-right": 0.6666666666666666,
        "Overlapping-right-left": 0.6666666666666666,
        "Size-left": 9,
        "Size-right": 9,
        "Weighted-Scoring": 0.4436476984102028
      }

    """
    url = self._buildUrl("compare")
    data = json.dumps(
      [
        {"positions": bitmap1},
        {"positions": bitmap2}
      ]
    )
    headers = {"Content-Type": "application/json"}
    response = requests.post(url,
                             headers=headers,
                             data=data)
    return json.loads(response.content)


  def bitmapToTerms(self, onBits):
    if len(onBits) is 0:
      raise Exception("Cannot convert empty bitmap to term!")
    response = self.bitmapToTermsRaw(onBits)
    similar = []
    for term in response:
      similar.append(
        {"term": term["term"], "score": term["score"]}
      )
    return similar


  def bitmapToTermsRaw(self, onBits):
    url = self._buildUrl("expressions/similarTerms")
    data = json.dumps({"positions": onBits})
    cachePath = "similarTerms-" + hashlib.sha224(data).hexdigest() + ".json"
    cachePath = os.path.join(self.cacheDir, cachePath)

    # Get it from the cache if it's there.
    if os.path.exists(cachePath):
      return json.loads(open(cachePath).read())
    else:
      headers = {"Content-Type": "application/json"}
      response = requests.post(url,
                               headers=headers,
                               data=data)

      with open(cachePath, 'w') as f:
        f.write(response.content)

      return json.loads(response.content)


  def _buildUrl(self, endpoint, params=None):
    if params is None:
      params = {}
    params["retinaName"] = self.retina
    return "%s%s?%s" % (self.apiUrl, endpoint, urllib.urlencode(params))


  @staticmethod
  def _bitmapToSdr(bitmap):
    width = bitmap["width"]
    height = bitmap["height"]
    total = width * height
    positions = bitmap["positions"]
    sdr = ""
    if len(positions) is 0:
      nextOn = None
    else:
      nextOn = positions.pop(0)

    for sdrIndex in range(0, total):

      if nextOn is None or nextOn != sdrIndex:
        sdr += "0"
      else:
        sdr += "1"
        if len(positions) is 0:
          nextOn = None
        else:
          nextOn = positions.pop(0)

    return sdr
