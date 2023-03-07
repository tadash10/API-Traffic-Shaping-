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

def print_menu():
    print("""
        __   __ __  __          _____ _          _ _ 
        \ \ / /|  \/  |   /\   / ____| |        | | |
         \ V / | \  / |  /  \ | |    | |__   ___| | |
          > <  | |\/| | / /\ \| |    | '_ \ / _ \ | |
         / . \ | |  | |/ ____ \ |____| | | |  __/ | |
        /_/ \_\|_|  |_/_/    \_\_____|_| |_|\___|_|_|

        API Traffic Shaping Tool

        Choose an option:
        1) Start traffic shaping
        2) Exit
    """)

def main():
    log_level = logging.ERROR

    while True:
        print_menu()
        choice = input('Enter your choice: ')

        if choice == '1':
            args = parse_args()

            if args.verbose:
                log_level = logging.INFO
            elif args.quiet:
                log_level = logging.CRITICAL

            logging.basicConfig(level=log_level)
            logging.info(f'Starting API traffic shaping on interface {args.interface} with rate limit {args.rate} kbps...')
            configure_tc(args.interface, args.rate)
            logging.info(f'Traffic shaping configuration applied according to {ISO_STANDARD} standard.')
        elif choice == '2':
            sys.exit(0)
        else:
            print('Invalid choice. Please enter 1 or 2.\n')

if __name__ == '__main__':
    main()
