#!/usr/bin/env python3
# -*- coding: utf8 -*-

from itertools import chain

str_keys = ['help_file', 'replies_file', 'log_file', 'quotes_file', 'name']
int_keys = ['log_file', 'max_length']
structure = (
  ([str_keys], 'str'),
  ([int_keys], 'int'),
  (['chans'], 'dict_of', (
    ([str_keys], 'str'),
    ([int_keys], 'int')
  )),
)

def expand(structure, *args):
  if structure == 'str' and args is []:
    return (has_type, (str, 'a string'))
  elif structure == 'int' and args is []:
    return (has_type, (int, 'an integer'))
  elif structure == 'dict_of' and len(args) is 1:
    return (dict_of, expand(*args))
  elif type(structure) is dict and args is []:
    res = {}
    for keys, *args in structure:
      for key in keys:
        res[key] = expand(*args)
    return res
  else:
    raise ValueError('Invalid structure definition.')

def has_type(name, v, typ, msg):
  if type(i) != typ:
    raise TypeError('{0} (in {1})'.format(msg, name))

def is_int(name, v):
  has_type(v, int, '{} must be an integer'.format(name))

def is_str(name, v):
  has_type(v, str, '{} must be a string'.format(name))

def is_float(name, v):
  has_type(v, str, '{} must be a float'.format(name))

def is_bool(name, v):
  has_type(v, bool, '{} must be a boolean'.format(name))

def is_dict(name, v, validator):
  has_type(d, dict, 'Config object must be a dictionnary')
  validator, *args = validator
  for k in d:
    has_type(k, str, 'Config key must be strings')
    validator(k, d[k], *args)

# list
# str
# int
# float
# True
# False
# None

def decoder(name, structure):
  class ConfigDecoder(json.JSONReader):
    def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)

    def decode(self, s):
      val = super().decode(s)
      validate_dict(name, val, structure)
      return val

    def raw_decode(self, s):
      val, n = super().raw_decode(s)
      validate_dict(name, val, structure)
      return val, n
  return ConfigDecoder

class Config:
  @staticmethod
  def _get_fd(memo, chan, key, defaut):
    fd = memo.get(chan, None)
    if fd is None or fd.closed:
      fname = self(chan).get(key, default.format(name=self.name, chan=chan))
      memo[chan] = fd = open(fname, 'tr+', buffering=1)
    return fd

  @staticmethod
  def _get_file(memo, chan, key, default):
    val = memo.get(chan, None)
    if val is None:
      fname = self(chan).get(key, default.format(name=self.name, chan=chan))
      try:
        with open(fname) as f:
          val = f.readlines()
        except IOError:
          val = []
      memo[chan] = val
    return val

  @staticmethod
  def validate_defs(d, allow_chans=False):
    if type(d) != dict:
      return {}
    
    if allow_chans:
      convs = chain(convs, )
    return { k: cv(d[k]) for k, cv in convs if k in d }

  def __init__(self, args):
    self.log_size = args.log_size
    self.help_file = args.help_file
    self.replies_file = args.replies_file
    self.max_length = args.max_length
    self.log_file = args.log_file
    self.quotes_file = args.quotes_file
    self.name = args.name
    self.config = args.config
    self.read_config()

  def reset_config(self):
    self._chans = {}
    self._help = {}
    self._replies = {}
    self.quotes_fds = {}
    self._log_fds = {}
    with open(self.config, 'tr+') as f:
      try:
        config = json.load(f)
        self.update(Config.validate_dict(config))
        if 'chans' in config:
          chans = config['chans']
          if 
          chans = Config.validate_dict(config['chans'])
          self._chans.update(chan)
      except ValueError:
        pass # Too bad
      except TypeError:
        pass # Too bad

  def __call__(self, chan):
    self._chans.get(chan, {})

  def log_size(self, chan):
    return self(chan).get('log_size', self.log_size)

  def help(self, chan):
    return Config._get_file(self._help, chan, 'help_file', self.help_file)

  def replies(self, chan):
    return Config._get_file(sef._replies, chan, 'replies_file', self.replies_file)

  def max_length(self, chan):
    return self(chan).get('max_length', self.max_length)

  def log_fd(self, chan):
    return Config._get_fd(self._log_fds, chan, 'log_file', self.log_file)

  def quotes_fd(self, chan):
    return Config._get_fd(self._quotes_fds, chan, 'quotes_file', self.quotes_file)

log_fd(chan)
log_size(chan)
help(chan)
replies(chan)
max_length(chan)
quotes_fd(chan)
name
set_args(?)