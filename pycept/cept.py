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

import os
import json
import requests

DEFAULT_BASE_URL = "http://api.cept.at"
DEFAULT_VERSION = "v1"
DEFAULT_CACHE_DIR = "/tmp/pycept"
DEFAULT_VERBOSITY = 0

class Cept(object):
  """
  Main class for the Cept API.
  """

  def __init__(self, app_id, app_key, base_url=DEFAULT_BASE_URL, 
      version=DEFAULT_VERSION, cache_dir=DEFAULT_CACHE_DIR,
      verbosity=DEFAULT_VERBOSITY):
    self.app_id = app_id
    self.app_key = app_key
    self.api_url = "%s/%s" % (base_url, version)
    # Create the cache directory if necessary.
    if not os.path.exists(cache_dir):
      os.mkdir(cache_dir)
    self.cache_dir = cache_dir
    self.verbosity = verbosity



  def getBitmap(self, term):
    urlParams = self._buildUrlParams()
    urlParams['term'] = term
    url = "%s/term2bitmap" % (self.api_url,)
    # Create a cache location for each term, where it will either be read in from
    # or cached within if we have to go to the CEPT API to get the SDR.
    cache_file = os.path.join(self.cache_dir, term + '.json')
    # Get it from the cache if it's there.
    if os.path.exists(cache_file):
      cached_sdr = json.loads(open(cache_file).read())
    # Get it from CEPT API if it's not cached.
    else:
      if self.verbosity > 0:
        print '\tfetching %s from CEPT API' % term
      response = requests.get(url, params=urlParams)
      cached_sdr = response.json['bitmap']
      # attach the sparsity for reference
      total = float(cached_sdr['width']) * float(cached_sdr['height'])
      on = len(cached_sdr['positions'])
      sparsity = round((on / total) * 100)
      cached_sdr['sparsity'] = sparsity
      # write to cache
      with open(cache_file, 'w') as f:
        f.write(json.dumps(cached_sdr))

    return cached_sdr


  def getSdr(self, term):
    return self._bitmapToSdr(self.getBitmap(term))


  def bitmapToTerms(self, width, height, onBits):
    if len(onBits) is 0:
      raise(Exception("Cannot convert empty bitmap to term!"))
    response = self.bitmapToTermsRaw(width, height, onBits)
    similar = []
    for term in response['similarterms']:
      similar.append(
        {'term': term['term'], 'rank': term['rank']}
      )
    return similar


  def bitmapToTermsRaw(self, width, height, onBits):
    urlParams = self._buildUrlParams()
    data = json.dumps({'width': width, 'height': height, 'positions': onBits})
    url = "%s/bitmap2terms" % (self.api_url)
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, params=urlParams, headers=headers, data=data)
    return response.json

  def _buildUrlParams(self):
    return {
      'app_id': self.app_id,
      'app_key': self.app_key
    }


  def _bitmapToSdr(self, bitmap):
    width = bitmap['width']
    height = bitmap['height']
    total = width * height
    positions = bitmap['positions']
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
