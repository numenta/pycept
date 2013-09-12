import pycept
import unittest

class ClientTestCase(unittest.TestCase):

  def testTinyEmptyBitMapToSdr(self):
    client = pycept.Cept('foo', 'bar')
    result = client._bitmapToSdr({
      'width': 1, 
      'height': 1,
      'positions': []
    })
    self.assertEqual(result, "0")


  def testTinyFullBitMapToSdr(self):
    client = pycept.Cept('foo', 'bar')
    result = client._bitmapToSdr({
      'width': 1, 
      'height': 1,
      'positions': [0]
    })
    self.assertEqual(result, "1")


  def testSmallEmptyBitMapToSdr(self):
    client = pycept.Cept('foo', 'bar')
    result = client._bitmapToSdr({
      'width': 4, 
      'height': 4,
      'positions': []
    })
    self.assertEqual(result, "0000000000000000")


  def testSmallFullBitMapToSdr(self):
    client = pycept.Cept('foo', 'bar')
    result = client._bitmapToSdr({
      'width': 4, 
      'height': 4,
      'positions': [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
    })
    self.assertEqual(result, "1111111111111111")


  def testSmallPartialBitMapToSdr(self):
    client = pycept.Cept('foo', 'bar')
    result = client._bitmapToSdr({
      'width': 4, 
      'height': 4,
      'positions': [2,3,6,7,10,11,14,15]
    })
    self.assertEqual(result, "0011001100110011")

