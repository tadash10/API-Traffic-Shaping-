import subprocess
import argparse
import logging
import sys

ISO_STANDARD = 'ISO/IEC 9126'

def parse_args():
    parser = argparse.ArgumentParser(description='API Traffic Shaping')
    parser.add_argument('-i', '--interface', required=True, help='network interface to shape traffic for')
    parser.add_argument('-r', '--rate', required=True, help='maximum rate to shape traffic to (in kbps)')
    parser.add_argument('-v', '--verbose', action='store_true', help='enable verbose output')
    parser.add_argument('-q', '--quiet', action='store_true', help='suppress output')
    return parser.parse_args()

def configure_tc(interface, rate):
    try:
        subprocess.run(['tc', 'qdisc', 'add', 'dev', interface, 'root', 'handle', '1:', 'htb', 'default', '1'], check=True)
        subprocess.run(['tc', 'class', 'add', 'dev', interface, 'parent', '1:', 'classid', '1:1', 'htb', 'rate',
                        f'{rate}kbit', 'burst', '15k'], check=True)
        subprocess.run(['tc', 'filter', 'add', 'dev', interface, 'protocol', 'ip', 'parent', '1:', 'prio', '1',
                        'u32', 'match', 'ip', 'sport', '80', '0xffff', 'flowid', '1:1'], check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f'Error configuring traffic shaping on interface {interface}: {e}')
        sys.exit(1)

def main():
    args = parse_args()

    log_level = logging.ERROR
    if args.verbose:
        log_level = logging.INFO
    elif args.quiet:
        log_level = logging.CRITICAL
    logging.basicConfig(level=log_level)

    logging.info(f'Starting API traffic shaping on interface {args.interface} with rate limit {args.rate} kbps...')
    configure_tc(args.interface, args.rate)
    logging.info(f'Traffic shaping configuration applied according to {ISO_STANDARD} standard.')

if __name__ == '__main__':
    main()
