#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import config, re, atexit
from time import time
from sys import stdin, stdout, stderr
from random import choice

def _(s):
  return s

class BufferLogger:
  "A simple file-based logger that keeps its most recent logs into memory"

  def __init__(self, file, mem_size):
    """Creates a new BufferLogger.

    Keyword arguments:
    file     -- a read/write file descriptor to the underlying file
    mem_size -- maximal size of the in-memory buffer

    """
    self._mem_size, self._file = mem_size, file
    self._mem = []

  def __iter__(self):
    """Iterates over the buffered content, then the actual file in FILO order.

    WARNING: If the iterator reaches the file-stored logs, it loads the whole
    file in memory, possibly resulting in memory overflow with huge files.
    It should NOT happen with a text-only file, so the only danger is if the
    log file has been externally replaced with a huge binary file.

    """
    for line in reversed(self._mem):
      yield line
    for line in reversed(self._file.readlines()): # TODO: Write into file in reverse order
      yield line

  def __call__(self, s):
    "Logs a new line and records its timestamp, flushing the buffer as needed."
    mem = self._mem
    mem.append('{:d} {}'.format(int(time()), s))
    if flush or len(mem) > self.mem_size:
      self.flush(int(len(mem)/2))

  def flush(self, keep=0, close=False):
    """Flushes in-memory content into the underlying file.

    Keyword arguments:
    keep -- the number of lines to keep in memory (default 0, everything is flushed)

    """ 
    mem, file = self._mem, self._file
    print(*mem[keep:], file=file, sep='\n')
    if close: file.close()
    else: file.flush()
    self.mem = mem[:keep]

class ChanLogger:
  cmd_regex = re.compile('^ <(?P<author>[^>]*)>\\s*(?P<name>[^\\s]*)\\s*:\\s*(?P<cmd>.*)$')
  find_regex = re.compile('^(?P<begin>.*?)\\s*(?:\.\.\.\\s*(?P<end>.*?)\\s*)?$')

  def __init__(self, chan):
    "Creates a new ChanLogger for a given chan."
    self.chan, self.log = chan, None
    self.reload_config()

  def reload_config(self):
    "Hot reloading of configuration from the config module."
    chan = self.chan
    if self.log is not None: # We don't want to lose any logged message
      self.log.flush(close=True)
    self.log = BufferLogger(config[chan].log_fd(), config.log_size(chan))
    self.help = config.help(chan)
    self.replies = config.replies(chan)
    self.max_length = config.max_length(self.chan)

  def talk_to(self, target=None, private=False):
    """Creates a function responsible for formatting and printing text
    destined to a given person.

    Keyword arguments:
    target  -- the name of the targetted user, or None for the whole channel (default None)
    private -- when True and target is not None, will talk in a query and not on the channel (default False)

    """
    if target is not None:
      if private: # Privately talking to a target: say "(chan) message" in a query
        fstr = '[{1}] ({0}) {{0}}'.format(chan, talk_to)
      else: # Publicly talking to a target: say "target: message" in the chan
        fstr = '[{0}] {1}: {{0}}'.format(chan, talk_to)
    else: # Publicly talking to everyone: just say "message" in the chan
      fstr = '[{0}] {{0}}'.format(chan)
    return lambda *args: print(*(fstr.format(s) for s in args), sep='\n')

  def save(self, quote):
    "Save a quote (a list of string) into the quotes file."
    with config[self.chan].quotes_fd() as quotes_fd:
      print(*quote, sep='\n', file=quotes_fd)

  def match(self, begin, end=''):
    """Find the last match in the logged messages.

    Keyword arguments:
    begin -- match the first line of the seeked interval
    end   -- match the last line of the seeked interval (default "")

    The match is non-greedy - matching for 'x' ... 'y' in  ['x', 'y', 'y']
    will yield ['x', 'y'] and not ['x', 'y', 'y'].

    """
    result, max_len = None, self.max_length
    # We want to non-greedily find the last match [begin, ..., end] in the iterator.
    # In order to achieve this, we do the following:
    #  - Iterate over the internal iterator in reverse order, searching for end
    #  - When end is found, start collecting the lines
    #  - If finding end again, reset the result to ensure non-greediness
    #  - Stop once begin has been encountered
    for line in self.log:
      # Guard ourselves against matches that are too big
      if max_len is not None and len(result) > max_len:
        break
      if end in line:
        result = []
      if result is not None:
        result.insert(0, line)
        if begin in line:
          return result
    if result is None:
      print(_('Je ne saisis pas à quoi vous faites allusion. Essayez "help".'))
    else:
      print(_("Je perçois bien la fin, mais n'entrevois pas le début (les citations les plus courtes étant les meilleures, je me limite à {0:d} lignes).").format(max_len))


  def treat_message(self, content):
    """Parses a message posted to the underlying chan, and process it.

    A message is a command if it starts with the string "NAME:", where NAME is
    pyanthologger's name (available in config.name).

    Available commands are:
    help            -- gives some help about pyanthologger
    begin [... end] -- try to find a match in the last logged messages

    Every message that is NOT a command is logged.
    Note that ONLY messages given to treat_message are logged - in particular,
    the answer generated by the commands are NOT logged.

    """
    infos = cmd_regex.match(content)
    if infos is None or infos['name'] != config.name:
      self.log(content)
    else:
      author, _name, cmd = infos.groups()
      say = self.talk_to(author, private=False)
      if cmd.strip() == 'help':
        say(*self.help)
      else:
        res = self.match(*(find_regex.match(cmd).groups()))
        if res is not None:
          self.save(res)
          say(choice(self.replies))
        else:
          say(*res)

class Anthologger:
  regex = re.compile('^\[(?P<chan>[^]]*)\](?P<content>.*)$')

  def __init__(self):
    self.chans = {}

  def run(self, config):
    atexit.register(self.flush)
    chans = self.chans
    for line in stdin:
      infos = Anthologger.regex.match(line)
      if infos is None: # Should not happen
        print("[DEBUG] Ill-formed input line {!r}".format(line), file=stderr)
        continue
      chan, message = infos.groups()
      if chan not in chans:
        chans[chan] = ChanLogger(chan, config)
      yield chans[chan].treat_message(message)

  def flush():
    for chan in chans.values():
      chan.log.flush()

  def reload_config(config):
    for chan in chans.values():
      chan.reload_config(config)

if __name__ == "__main__":
  import argparse
  parser = argparse.ArgumentParser(description='Anthologger')
  parser.add_argument('--config',
                      default='~/.config/pyanthologger/config.json',
                      help='configuration file to use (%(default)s)')
  parser.add_argument('--name', nargs='+',
                      default='anthologger',
                      help='name of the bot (%(default)s)')
  parser.add_argument('--quotes-file',
                      default='./{chan}/quotes',
                      help='format string for the quotes file (%(default)s)')
  parser.add_argument('--log-file',
                      default='./{chan}/log',
                      help='format string for the log files (%(default)s)')
  parser.add_argument('--mem-size', type=int,
                      default=1000,
                      help='maximum number of lines to keep in memory (%(default)i)')
  parser.add_argument('--replies-file', nargs='+',
                      default=['./{chan}/replies', './replies'],
                      help='format string for the replies file (%(default)s)')
  parser.add_argument('--help-file', nargs='+',
                      default=['./{chan}/help', './help'],
                      help='format string for the help files (%(default)s)')
  parser.add_argument('--max-length', type=int,
                      default=100,
                      help='maximum length of a quote in lines (%(default)i)')
  parser.add_argument('--chans', type=dict,
                      default={},
                      help='JSON configuration describing per-chan values')

  subparsers = parser.add_subparsers(help='Old-style arguments')
  oldparser = subparsers.add_parser('v0.1', help='initial arguments (override corresponding new arguments when present)')
  oldparser.add_argument('--name', default='anthologger', help='name of the bot (anthologger)')
  oldparser.add_argument('--quote-prefix', default='quote_', help='prefix for the quote files (quote_)')
  oldparser.add_argument('--log-prefix', default='/tmp/log_', help='prefix for the chan log files (/tmp/log_)')
  oldparser.add_argument('--mem-size', default=1000, type=int, help='maximum number of messages to keep in RAM (1000)')
  oldparser.add_argument('--replies-file', default='replies', help='file containing the replies (replies)')
  oldparser.add_argument('--help-prefix', default='./', help='prefix for help files (./)')
  oldparser.add_argument('--max-len', default=100, type=int, help='maximum length of a quote (in lines, 100)')

  conf = config.Config(parser.parse_args())
  anthologger = Anthologger()
  # Run forever
  for res in anthologger.run(conf):
    pass

#  {'name': 'anthologger',
#   'quotes_file': 'quote_{chan}',
#   'log_file': '/tmp/log_{chan}',
#   'mem_size': 1000, # TODO: Unit change...
#   'replies_file': 'replies',
#   'help_file': '{chan}',
#   'max_length': 100,
#   'chans': { '#ulminfo': { 'quotes_file': '/dev/null' } }
#  }