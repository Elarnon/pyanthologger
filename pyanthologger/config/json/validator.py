# -*- coding: utf-8 -*-

class ValidationError(Exception):
  def __init__(self, err):
    self.err = err

  def __str__(self):
    return self.err

class ValidationAny(ValidationError):
  def __init__(self, *args):
    super().__init__(_(', or ').join(verr.err for verr in args))

class then:
  def __init__(self, *fns):
    self.fns = fns

  def __call__(self, val, name):
    for fn in self.fns:
      val = fn(val, name)
    return val

class is_any:
  def __init__(self, *convs):
    if __debug__ and len(convs) is 0:
      logging.debug('is_any called without arguments, will meaninglessly fail.')
    self.convs = convs

  def __call__(self, val, name):
    errs = []
    for conv in self.convs:
      try:
        return conv(val, name)
      except ValidationError as verr:
        errs.extend(verr)
    raise ValidationAny(*errs)

class has_type:
  def __init__(self, typ, error):
    self.typ, self.error = typ, error

  def __call__(self, val, name):
    if isinstance(val, self.typ): return val
    else: raise ValidationError('{name} should be {atype}'.format(name='.'.join(name), atype=self.error))

is_str = has_type(str, _('a string'))
is_int = has_type(int, _('an integer'))
is_dict = has_type(dict, _('a dictionary'))
is_list = has_type(list, _('a list'))

def map_list(cv):
  return lambda val, name: [cv(x, name + [str(i)]) for i, x in enumerate(val)]

def structure_of_dict(st):
  return lambda val, name: { k: cv(val[k], name + [k]) for k, cv in st.items() if k in val }

def map_dict(cv):
  return lambda val, name: { k: cv(v, name + [k]) for k, v in val.items() }

def is_glist(cv):
  return is_any(then(is_list, map_list(cv)),
                then(cv, lambda val, name: [val]))

chan_structure = {
  'help_file': is_glist(is_str),
  'replies_file': is_glist(is_str),
  'log_file': is_glist(is_str),
  'quotes_file': is_glist(is_str),
  'name': is_str,
  'log_size': is_int,
  'max_length': is_int,
}
chan_of_dict = structure_of_dict(chan_structure)
is_chan = then(is_dict, chan_of_dict)

server_structure = chan_structure.copy()
server_structure.update(
  chans=then(is_dict, map_dict(is_chan)),
)
server_of_dict = structure_of_dict(server_structure)
is_server = then(is_dict, server_of_dict)