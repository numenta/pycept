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

DEFAULT_BASE_URL = "http://s_api.cortical.io:80/rest/"
DEFAULT_RETINA = "eng_syn"
DEFAULT_CACHE_DIR = "/tmp/pycept"
DEFAULT_VERBOSITY = 0

class Cept(object):
  """
  Main class for the Cept API.
  """

  def __init__(self, api_key,
               base_url=DEFAULT_BASE_URL, 
               retina=DEFAULT_RETINA,
               cache_dir=DEFAULT_CACHE_DIR,
               verbosity=DEFAULT_VERBOSITY):
    self.api_key = api_key
    self.api_url = base_url
    self.retina = retina
    # Create the cache directory if necessary.
    if not os.path.exists(cache_dir):
      os.mkdir(cache_dir)
    self.cache_dir = cache_dir
    self.verbosity = verbosity



  def getBitmap(self, term):
    url = self._buildUrl("text")
    # Create a cache location for each term, where it will either be read in from
    # or cached within if we have to go to the CEPT API to get the SDR.
    cache_file = os.path.join(self.cache_dir, term + '.json')
    # Get it from the cache if it's there.
    if os.path.exists(cache_file):
      sdr = json.loads(open(cache_file).read())
    # Get it from CEPT API if it's not cached.
    else:
      if self.verbosity > 0:
        print '\tfetching %s from CEPT API' % term
      headers = {'Content-Type': 'application/json'}
      response = requests.post(url,
                               headers=headers,
                               data=term)
      sdr = json.loads(response.content)[0]

      # Default width and height
      if not 'width' in sdr:
        sdr['width']  = 64
      if not 'height' in sdr:
        sdr['height'] = 64

      # attach the sparsity for reference
      total = float(sdr['width']) * float(sdr['height'])
      on = len(sdr['positions'])
      sparsity = round((on / total) * 100)
      sdr['sparsity'] = sparsity
      # write to cache
      with open(cache_file, 'w') as f:
        f.write(json.dumps(sdr))

    return sdr


  def getSdr(self, term):
    return self._bitmapToSdr(self.getBitmap(term))


  def bitmapToTerms(self, _width, _height, onBits):
    if len(onBits) is 0:
      raise(Exception("Cannot convert empty bitmap to term!"))
    response = self.bitmapToTermsRaw(onBits)
    similar = []
    for term in response:
      similar.append(
        {'term': term['term'], 'score': term['score']}
      )
    return similar


  def bitmapToTermsRaw(self, onBits):
    url = self._buildUrl("expressions/similarTerms")
    data = json.dumps({'positions': onBits})
    cache_path = 'bitmap-' + hashlib.sha224(data).hexdigest() + '.json'
    cache_file = os.path.join(self.cache_dir, cache_path)
    
    # Get it from the cache if it's there.
    if os.path.exists(cache_file):
      return json.loads(open(cache_file).read())
    else:
      headers = {'Content-Type': 'application/json'}
      response = requests.post(url,
                               headers=headers,
                               data=data)

      with open(cache_file, 'w') as f:
        f.write(response.content)

      return json.loads(response.content)


  def _buildUrl(self, endpoint, params={}):
    params['api_key']    = self.api_key
    params['retinaName'] = self.retina
    return "%s%s?%s" % (self.api_url, endpoint, urllib.urlencode(params))


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
