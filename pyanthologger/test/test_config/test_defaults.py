#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
from pyanthologger.config import defaults

class ConfigTestCase(unittest.TestCase):
  def __init__(self):
    self.__chan_keys = {
      'config', 'name', 'quotes_file', 'log_file', 'log_size', 'replies_file',
      'help_file', 'max_length'
    }
    self.__server_keys = self.__chan_keys.union({ 'chans' })

  def assertHasKeys(self, val, keys, exact=True):
    all(self.assertIn(k, val) for k in keys)
    if exact:
      all(self.assertIn(k, keys) for k in vals)

  def assertIsChan(self, val, exact=True):
    self.assertHasKeys(val, self.__chan_keys, exact)
    self.assertIsInstance(val['config'], str)
    self.assertIsInstance(val['name'], str)
    self.assertIsInstance(val['quotes_file'], str)
    self.assertIsInstance(val['log_file'], str)
    self.assertIsInstance(val['log_size'], int)
    all(self.assertIsInstance(x, str) for x in val['replies_file'])
    all(self.assertIsInstance(x, str) for x in val['help_file'])
    self.assertIsInstance(val['max_length'], int)

  def assertIsServer(self, val, exact=True):
    self.assertHasKeys(val, self.__server_keys, exact)
    self.assertIsChan(val, exact=False)
    all(self.assertIsChan(chan) for chan in val['chans'].values())

class DefaultsTestCase(ConfigTestCase):
  def test_is_server(self):
    self.assertIsServer(vars(defaults))