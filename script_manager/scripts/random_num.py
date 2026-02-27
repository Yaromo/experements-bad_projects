from random import randint
import argparse


def arguments():
    return ['--max', '--min']


def create_parser():
    parser = argparse.ArgumentParser(description="max-min")
    parser.add_argument('--max', default=100, help='max')
    parser.add_argument('--min', default=1, help='min')
    return parser


if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()
    print(randint(*sorted([int(args.min), int(args.max)])))