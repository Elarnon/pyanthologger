def merge(self, parent, merger):
  return {
    k: fn(self[k], parent[k]) if k in self else parent[k]
    for k, fn in merger.items()
  }

chan_merger = {
  'help_file': lambda self, parent: self + parent,
  'replies_file': lambda self, parent: self + parent,
  'log_file': lambda self, parent: self,
  'quotes_file': lambda self, parent: self,
  'name': lambda self, parent: self,
  'log_size': lambda self, parent: self,
  'max_length': lambda self, parent: self,
}
merge_chan = lambda self, parent: merge(self, parent, chan_merger)

server_merger = chan_merger.copy()
server_merger.update(
  chans=lambda self, parent: merge_chan(self, parent),
)
merge_server = lambda self, parent: merge(self, parent, server_merger)