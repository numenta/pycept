import pycept
import unittest
from mock import patch, MagicMock
import httpretty


class ClientTestCase(unittest.TestCase):



  @httpretty.activate
  @patch('os.path.exists', return_value=False)
  @patch('os.makedirs')
  @patch('json.dump')
  def testTokenizeEmptyString(self, mockExists, mockMakedirs, mockDump):
    client = pycept.Cept("apikey")

    httpretty.register_uri(
        httpretty.POST,
        "http://numenta.cortical.io:80/rest/text/tokenize?retinaName=eng_syn",
        body='[]',
    )

    open_name = '%s.open' % __name__
    with patch(open_name, create=True) as mock_open:
      mock_open.return_value = MagicMock(spec=file)
      result = client.tokenize("")

    self.assertListEqual(result, [])


  @httpretty.activate
  @patch('os.path.exists', return_value=False)
  @patch('os.makedirs')
  @patch('json.dump')
  def testTokenizeSingleSentence(self, mockExists, mockMakedirs, mockDump):
    client = pycept.Cept("apikey")

    httpretty.register_uri(
        httpretty.POST,
        "http://numenta.cortical.io:80/rest/text/tokenize?retinaName=eng_syn",
        body='["cow,jumped,moon"]',
    )

    open_name = '%s.open' % __name__
    with patch(open_name, create=True) as mock_open:
      mock_open.return_value = MagicMock(spec=file)
      result = client.tokenize("The cow jumped over the moon.")

    self.assertEqual(len(result), 1, "Wrong number of sentences in results")
    self.assertListEqual(result[0], ["cow", "jumped", "moon"])


  @httpretty.activate
  @patch('os.path.exists', return_value=False)
  @patch('os.makedirs')
  @patch('json.dump')
  def testTokenizeMultipleSentences(self, mockExists, mockMakedirs, mockDump):
    client = pycept.Cept("apikey")

    httpretty.register_uri(
        httpretty.POST,
        "http://numenta.cortical.io:80/rest/text/tokenize?retinaName=eng_syn",
        body='["cow,jumped,moon","sun,came"]',
    )

    open_name = '%s.open' % __name__
    with patch(open_name, create=True) as mock_open:
      mock_open.return_value = MagicMock(spec=file)
      result = client.tokenize(
          "The cow jumped over the moon. And then the sun came up.")

    self.assertEqual(len(result), 2, "Wrong number of sentences in results")
    self.assertListEqual(result[0], ["cow", "jumped", "moon"])
    self.assertListEqual(result[1], ["sun", "came"])


  def testTinyEmptyBitMapToSdr(self):
    client = pycept.Cept("apikey")
    result = client._bitmapToSdr({
      'width': 1,
      'height': 1,
      'positions': []
    })
    self.assertEqual(result, "0")


  def testTinyFullBitMapToSdr(self):
    client = pycept.Cept("apikey")
    result = client._bitmapToSdr({
      'width': 1,
      'height': 1,
      'positions': [0]
    })
    self.assertEqual(result, "1")
  
  
  def testSmallEmptyBitMapToSdr(self):
    client = pycept.Cept("apikey")
    result = client._bitmapToSdr({
      'width': 4,
      'height': 4,
      'positions': []
    })
    self.assertEqual(result, "0000000000000000")
  
  
  def testSmallFullBitMapToSdr(self):
    client = pycept.Cept("apikey")
    result = client._bitmapToSdr({
      'width': 4,
      'height': 4,
      'positions': [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
    })
    self.assertEqual(result, "1111111111111111")
  
  
  def testSmallPartialBitMapToSdr(self):
    client = pycept.Cept("apikey")
    result = client._bitmapToSdr({
      'width': 4,
      'height': 4,
      'positions': [2,3,6,7,10,11,14,15]
    })
    self.assertEqual(result, "0011001100110011")



if __name__ == "__main__":
  unittest.main()
