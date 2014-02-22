#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import pyanthologger.config as c

class TestStructureCheckers(unittest.TestCase):
  def setUp(self):
    self.struct = {
              'a_string': c.is_str,
              'an_int': c.is_int,
              'a_list': lambda val, name: c.has_type(val, list, 'a list'),
              'a_dict': c.has_structure({ 'x': c.is_int })
              }
    self.smaller = {
             'a_string': 'kowabunga',
             'a_list': [1, 'foo', True],
              'another_field': 17,
             }
    self.exact = {
             'a_string': 'Churchill',
             'an_int': 17,
             'a_list': [],
             'a_dict': {},
             'another_field': 'Arthur'
             }
    self.dict_of_int = { 'a': 2, 'b': 17, }
    self.dict_of_struct = { 'a': { 'x': 12, 'y': 17 }, }
    self.dict_mixed = { 'a': 2, 'b': { 'x': 12, 'y': 29 } }

  def test_has_type(self):
    self.assertIsNone(c.has_type('Hey!', str, 'a string'))
    self.assertIsNone(c.has_type(42, int, 'an integer'))
    self.assertIsNone(c.has_type(bool(), bool, 'a boolean'))
    self.assertRaises(ValueError, c.has_type, 'd', 42, str, 'a string')
    self.assertRaises(ValueError, c.has_type, bool(), int, 'an integer')

  def test_is_str(self):
    self.assertIsNone(c.is_str('Holà!'))
    self.assertRaises(ValueError, c.is_str, 12)
    self.assertRaises(ValueError, c.is_str, [])

  def test_is_int(self):
    self.assertIsNone(c.is_int(17))
    self.assertRaises(ValueError, c.is_int, {})
    self.assertRaises(ValueError, c.is_int, [14])

  def test_has_structure(self):
    self.assertIsNone(c.has_structure(self.struct)(self.smaller))
    self.assertIsNone(c.has_structure(self.struct)(self.exact))
    self.assertRaises(ValueError, c.has_structure(self.struct, strict=True), self.smaller)
    self.assertRaises(ValueError, c.has_structure(self.struct, exact=True), self.smaller)
    self.assertRaises(ValueError, c.has_structure(self.struct, strict=True), self.exact)
    self.assertIsNone(c.has_structure(self.struct, exact=True)(self.exact))
    self.assertRaises(ValueError, c.has_structure(self.struct), 12)

  def test_dict_of(self):
    is_point = c.has_structure({ 'x': c.is_int, 'y': c.is_int }, exact=True, strict=True)

    self.assertIsNone(c.dict_of(c.is_int)(self.dict_of_int))
    self.assertRaises(ValueError, c.dict_of(c.is_int), self.dict_of_struct)
    self.assertRaises(ValueError, c.dict_of(c.is_int), self.dict_mixed)
    
    self.assertRaises(ValueError, c.dict_of(is_point), self.dict_of_int)
    self.assertIsNone(c.dict_of(is_point)(self.dict_of_struct))
    self.assertRaises(ValueError, c.dict_of(is_point), self.dict_mixed)

if __name__ == '__main__':
  unittest.main()