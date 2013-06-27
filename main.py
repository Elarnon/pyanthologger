#!/usr/bin/env python3
# -*- coding: utf8 -*-
import config
from time import time
from sys import stdin, stdout, stderr
def _(s):
  return s

class Matcher:
  def __init__(self, it, max_length):
    self.it, self.max_length = it, max_length

  def __call__(self, begin, end=None):
    result = [] if end is None else None
    max_len, it = self.max_length, self.it
    for line in it:
      if len(result) > max_len:
        print(_("Désolé, cette citation est trop longue (plus de {0:d} lignes).").format(max_len))
        return None
      if end in line: # Reset result each time we find end - [x, y, y] -> [x, y]
        result = []
      if result is not None:
        result.insert(0, line)
        if begin in line:
          return result
    if result is None:
      print(_('Je ne saisis pas à quoi vous faites allusion. Essayez "help".'))
    else:
      print(_("Je perçois bien la fin, mais n'entrevois pas le début."))

class Talker:
  class Context:
    def __init__(self, talker, old):
      self._talker, self._old = talker, old

    def __enter__(self):
      pass

    def __exit__(self, exc_type, exc_value, traceback):
      self._talker._fstr = self._old

  def __init__(self, chan):
    self._chan = chan
    self.talk_to(None)

  def talk_to(self, talk_to=None, public=True):
    chan, fstr = self._chan, self._fstr
    if talk_to is not None:
      if public:
        self._fstr = '[{0}] {1}: {{0}}'.format(chan, talk_to)
      else:
        self._fstr = '[{1}] ({0}) {{0}}'.format(chan, talk_to)
    else:
      self._fstr = '[{0}] {{0}}'.format(chan)
    return Context(self, fstr)

  def __call__(self, *args):
    fstr = self._fstr
    print(*(fstr.format(s) for s in args), sep='\n')

class Logger:
  def __init__(self, file):
    self._file = file

  def __iter__(self):
    return self._file.__iter__()

  def __call__(self, content):
    print('{:d} [BACKWARDS_COMPATIBILITY] {}'.format(int(time()), content), file=self._file)

class Chan:
  cmd_regex = re.compile('^ <(?P<author>[^>]*)>\\s*(?P<name>[^\\s]*)\\s*:\\s*(?P<cmd>.*)$')
  find_regex = re.compile('^(?P<begin>.*?)\\s*(?:\.\.\.\\s*(?P<end>.*?)\\s*)?$')

  def __init__(self, chan):
    self.chan = chan
    self.log = Logger(chan, config.log_fd(chan))
    self.match = Matcher(self.log, config.max_length(chan))
    self.talk = Talker(chan)

  def help():
    return config.help(chan)

  def reply():
    return choice(config.replies(self.chan))

  def save(self, quotes):
    quotes_fd = config.quotes_fd(self.chan)
    print(*quotes, sep='\n', file=quotes_fd)
    quotes_fd.flush()

  def parse(self, content):
    infos = cmd_regex.match(content)
    # TODO: Should we log commands, in order to provide a consistent view
    # with the user's of the contents of the channel?
    if infos is None or infos['name'] != self.config['name']:
      self.log(content)
    else:
      author, _name, cmd = infos.groups()
      talk = self.talk
      with talk.talk_to(author, public=True):
        if cmd.strip() == 'help':
          talk(*self.help())
        else:
          res = self.match(*(find_regex.match(cmd).groups()))
          if res is not None:
            self.save(res)
            talk(*self.reply())
          else:
            talk(*res)

class Irctk:
  regex = re.compile('^\[(?P<chan>[^]]*)\](?P<content>.*)$')

  def __iter__(self):
    for line in stdin:
      infos = regex.match(line)
      if infos is None: # Should not happen
        print("[DEBUG] Ill-formed input line {!r}".format(line), file=stderr)
        continue
      yield infos.groups()

  def write(self, chan, message):
    print('[{}]{}'.format(chan, message), file=self.fout)

if __name__ == "__main__":
  import sys, argparse, re, atexit, os
  from random import choice
  parser = argparse.ArgumentParser(description='Quote bot')
  parser.add_argument('--name', default='anthologger', help='name of the bot (anthologger)')
  parser.add_argument('--quote-prefix', default='quote_', help='prefix for the quote files (quote_)')
  parser.add_argument('--log-prefix', default='/tmp/log_', help='prefix for the chan log files (/tmp/log_)')
  parser.add_argument('--mem-size', default=1000, type=int, help='maximum number of lines to keep in memory (1000)')
  parser.add_argument('--replies-file', default='replies', help='file containing the replies (replies)')
  parser.add_argument('--help-prefix', default='./', help='prefix for help files (./)')
  parser.add_argument('--max-len', default=100, type=int, help='maximum length of a quote (in lines, 100)')
  config.set(parser.parse_args())
  chans = {}
  irc = Irctk()

  {'name': 'anthologger',
   'quotes_file': 'quote_{chan}',
   'log_file': '/tmp/log_{chan}',
   'mem_size': 1000, # TODO: Unit change...
   'replies_file': 'replies',
   'help_file': '{chan}',
   'max_length': 100,
   'chans': { '#ulminfo': { 'quotes_file': '/dev/null' } }
  }

  def save():
    for chan in chans:
      chans[chan]['logger'].flush()
  atexit.register(save)

  for chan, content in irc:
    # Load chan at first use
    if chan not in chans:
      chans[chan] = Chan(chan)

    res = chans[chan].parse(content)
    if res is not None:
      irc.write(chan, res)




class Buffer: # TODO: Remove this shit

  def write():
  if len(mem) > self.mem_size:
      self.flush(int(len(mem)/2))

  def flush(self, keep=0):
    mem = self.mem
    print(*mem[keep:], file=self.file, sep='\n', flush=True) # TODO: Really flush?
    self.mem = mem[:keep]