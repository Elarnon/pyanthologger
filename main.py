#!/usr/bin/env python3

import smtplib
from email.mime.text import MIMEText


class BocalEmailQuoter:
    def quote(self, chan, author, lines):
        mail = MIMEText("{} a considéré que la citation suivante, "
                        "toute fraîche sortie d'IRC, pourrait "
                        "constituer une brève.\n\n" +
                        "> ".join(lines))
        mail['Subject'] = "Brève sur IRC"
        mail['From'] = 'anthologger@ulminfo.fr'
        mail['To'] = 'bocal@clipper.ens.fr'
        s = smtplib.SMTP('localhost')
        s.send_message(mail)
        s.quit()

special_quoters = {
    '#bocal': BocalEmailQuoter(),
}


class Logger:

    def __init__(self, log_file, mem_size, max_len):
        self.f = log_file
        self.mem = []
        self.MAX_MEM_SIZE = mem_size
        self.MAX_LENGTH = max_len

    def __iter__(self):
        for line in reversed(self.mem):
            yield line
        with open(self.f, 'r') as f:
            for line in reversed(f.readlines()):  # TODO: improve
                yield line

    def log(self, line):
        self.mem.append(line + '\n')
        while len(self.mem) > self.MAX_MEM_SIZE:
            self.flush(int(len(self.mem) / 2))

    def flush(self, size=None):
        if size is None:
            size = len(self.mem)
        with open(self.f, 'a') as f:
            f.writelines(self.mem[:size])
        self.mem = self.mem[size:]

    def find(self, begin, end=None):
        if end is None:
            end = begin
        result, matched = [], False
        for line in self:
            if len(result) > self.MAX_LENGTH:
                return (
                    "Désolé, cette citation est trop longue (max. {} lignes)."
                    .format(self.MAX_LENGTH)
                )
            close = line.find(']')
            if close != -1 and line[close+1:].find(end) != -1:
                matched = True
                result = []  # log until the *last* occurrence of end
            if matched:
                result.insert(0, line)
                if line.find(begin) != -1:
                    break
        if matched:
            return result
        elif result == []:
            return (
                'Je ne saisis pas à quoi vous faites allusion. Essayez "help".'
            )
        else:
            return "Je perçois bien la fin, mais n'entrevois pas le début."

if __name__ == "__main__":
    import sys
    import argparse
    import re
    import atexit
    import time
    import os
    from random import choice
    parser = argparse.ArgumentParser(description='Quote bot')
    parser.add_argument(
        '--name', default='anthologger', help='name of the bot (anthologger)')
    parser.add_argument(
        '--quote-prefix', default='quote_',
        help='prefix for the quote files (quote_)')
    parser.add_argument('--log-prefix', default='/tmp/log_',
                        help='prefix for the chan log files (/tmp/log_)')
    parser.add_argument('--mem-size', default=1000, type=int,
                        help='max. number of messages to keep in RAM (1000)')
    parser.add_argument('--replies-file', default='replies',
                        help='file containing the replies (replies)')
    parser.add_argument(
        '--help-prefix', default='./', help='prefix for help files (./)')
    parser.add_argument('--max-len', default=100, type=int,
                        help='maximum length of a quote (in lines, 100)')
    args = parser.parse_args()
    talk = sys.stdout
    irctk = re.compile(r'^\[(?P<chan>[^]]*)\](?P<content>.*)$')
    command = re.compile(
        r'^ <(?P<author>[^>]*)>\s*' + args.name + r'\s*:\s*(?P<cmd>.*)$')
    regex = re.compile(r'^(?P<begin>.*?)\s*(?:\.\.+\s*(?P<end>.*?)\s*)?$')
    with open(args.replies_file, 'r') as f:
        replies = f.readlines()
    chans, helps = {}, {}

    def save():
        for chan in chans:
            chans[chan].flush()
    atexit.register(save)

    for line in sys.stdin:
        infos = irctk.match(line)
        if infos is None:  # Should never happen
            continue
        chan, content = infos.groups()
        # Load chan at first use
        if chan not in chans:
            chans[chan] = Logger(
                args.log_prefix + chan, args.mem_size, args.max_len)
            helps[chan] = []
            if os.path.exists(args.help_prefix + chan):
                with open(args.help_prefix + chan, 'r') as f:
                    helps[chan] = f.readlines()

        cmdinfos = command.match(content)
        if cmdinfos is None:
            chans[chan].log('{0} [{1}] {2}'.format(time.time(), chan, content))
        else:
            author, cmd = cmdinfos.groups()
            if cmd.strip() == 'help':
                talk.writelines(
                    '[{chan}] {line}\n'.format(
                        chan=chan, line=line
                    )
                    for line in helps[chan]
                )
                talk.flush()
            else:
                begin, end = regex.match(cmd).groups()
                res = chans[chan].find(begin, end)
                if type(res) == list:
                    if chan in special_quoters:
                        special_quoters[chan].quote(chan, author, res)
                    with open(args.quote_prefix + chan, 'a') as f:
                        f.writelines(res + ['\n'])
                    talk.write('[{chan}] {reply}'.format(
                        chan=chan,
                        reply=choice(replies)
                    ))
                    talk.flush()
                else:
                    talk.write('[{chan}] {res}\n'.format(chan=chan, res=res))
                    talk.flush()
