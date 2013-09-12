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

import requests

DEFAULT_BASE_URL = "http://api.cept.at"
DEFAULT_VERSION = "v1"

class Cept(object):
  """
  Main class for the Cept API.
  """

  def __init__(self, app_id, app_key, base_url=DEFAULT_BASE_URL, version=DEFAULT_VERSION):
    self.app_id = app_id
    self.app_key = app_key
    self.api_url = "%s/%s" % (base_url, version)


  def getSdr(self, term):
    payload = self._buildPayload()
    payload['term'] = term
    url = "%s/term2bitmap" % (self.api_url,)
    response = requests.get(url, params=payload)
    return self._bitmapToSdr(response.json['bitmap'])


  def _buildPayload(self):
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
      print("nextOn: %s  sdrIndex: %s" % (str(nextOn), str(sdrIndex)))

      if nextOn is None or nextOn != sdrIndex:
        sdr += "0"
      else:
        sdr += "1"
        if len(positions) is 0:
          nextOn = None
        else:
          nextOn = positions.pop(0)

    
    return sdr
