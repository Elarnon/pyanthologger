from . import merger

class ChanConfig:
  def __init__(self, server, chan, defaults, config={}):
    self.server, self.chan, self._defaults = server, chan, defaults
    self.overwrite(config)

  def overwrite(self, new={}):
    config = merger.merge_chan(new, self._defaults)
    kws = { 'name': config['name'], 'chan': self.chan, 'server': self.server }
    self.help = contents_of_fnames(*config['help_file'], **kws)
    self.replies = contents_of_fnames(*config['replies_file'], **kws)
    self._log_fd = config['log_file'].format(**kws)
    self._quotes_fd = config['quotes_file'].format(**kws)
    self.name = config['name']
    self.log_size = config['log_size']
    self.max_length = config['max_length']

  def log_fd(self):
    return fd_of_fname(self._log_fd)

  def quotes_fd(self):
    return fd_of_fname(self._quotes_fd)

class ServerConfig:
  def __init__(self, server, defaults, config={}):
    self.server, self._defaults = server, defaults
    self.overwrite(config)

  def overwrite(self, new={}):
    self._config = merger.merge_server(new, self._defaults)
    self._chans = {}

  def __getitem__(self, chan):
    chans = self._chans
    if chan not in chans:
      defaults = self._defaults
      chans[chan] = ChanConfig(self.server, chan,
                               merger.merge_chan(defaults['chans'].get(chan, {}), defaults),
                               self._config['chans'].get(chan, {}))
    return chans[chan]