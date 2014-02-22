from . import objects, validator

def fd_of_fname(fname):
  try:
    return open(fname, 'tr+', buffering=1)
  except EnvironmentError:
    logging.debug('[fd_of_fname] Unable to open file ({}), returning a dummy StringIO'.format(fname))
    return io.StringIO()

def contents_of_fnames(*fnames, **vars):
  for fname in (fname.format(**vars) for fname in fnames):
    try:
      with open(fname) as f:
        return f.readlines()
    except EnvironmentError:
      logging.debug('[contents_of_fname] Unable to open file: {}'.format(fname))
  logging.debug('[contents_of_fname] Unable to open any file, returning empty list.')
  return []

def read(server, fname, defaults):
  with fd_of_fname(fname) as f:
    config = {}
    try:
      config = validator.is_server(json.load(f))
    except ValueError as err: # TODO: json decoder failure
      logging.warning(_('Configuration file {} is not valid JSON: {}').format(fname, err))
    except validator.ValidationError as err: # TODO
      logging.warning(_('JSON configuration file {} is not a pyanthologger configuration file: {}').format(fname, err))
    return objects.ServerConfig(server, defaults, config)