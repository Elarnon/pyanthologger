import argparse, defaults

parser = argparse.ArgumentParser(description='Anthologger')
parser.add_argument('--config',
                    default=defaults.config,
                    help='configuration file to use (%(default)s)')
parser.add_argument('--name',
                    default=defaults.name,
                    help='name of the bot (%(default)s)')
parser.add_argument('--quotes-file',
                    default=defaults.quotes_file,
                    help='format string for the quotes file (%(default)s)')
parser.add_argument('--log-file',
                    default=defaults.log_file,
                    help='format string for the log files (%(default)s)')
parser.add_argument('--mem-size', type=int, dest='log_size',
                    default=defaults.log_size,
                    help='maximum number of lines to keep in memory (%(default)i)')
parser.add_argument('--replies-file', nargs='+',
                    default=defaults.replies_file,
                    help='format string for the replies file (%(default)s)')
parser.add_argument('--help-file', nargs='+',
                    default=defaults.help_file,
                    help='format string for the help files (%(default)s)')
parser.add_argument('--max-length', type=int,
                    default=defaults.max_length,
                    help='maximum length of a quote in lines (%(default)i)')
parser.add_argument('--chans', type=dict,
                    default=defaults.chans,
                    help='JSON configuration describing per-chan values')