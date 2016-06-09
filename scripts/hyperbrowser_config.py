import sys, os
from getopt import GetoptError, getopt

new_path = [ os.path.join( os.getcwd(), "lib" ) ]
new_path.extend( sys.path[1:] )  # remove scripts/ from the path
sys.path = new_path

def usage():
    print '''
Script to print a config constant for The Genomic HyperBrowser config

Usage: python setup.py -c CONSTANT

OPTIONS:
    -c CONSTANT:
        The constant whose value should be printed.

    -h, --help:
        Returns this help screen.
'''


if __name__ == '__main__':
    configConstant = ''

    try:
        opts, args = getopt(sys.argv[1:], 'hc:', ['help', 'config-constant'])
    except GetoptError:
        usage()
        sys.exit(1)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit(0)
        if opt in ('-c', '--config-constant'):
            configConstant = arg

    if not configConstant:
        print 'Error, config constant needs to be specified. Usage:'
        usage()
        sys.exit(0)

    if len(args) > 0:
        usage()
        sys.exit(0)

    if not os.environ.get('GALAXY_CONFIG_FILE'):
        os.environ['GALAXY_CONFIG_FILE'] = 'config/galaxy.ini'

    import config.Config as Config
    print Config.__dict__.get(configConstant)

