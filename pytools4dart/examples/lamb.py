import sys


def write_lamb(outfile):
    outfile.write("Mary had a little lamb.\n")


if __name__ == '__main__':
    with open(sys.argv[1], 'w') as outfile:
        write_lamb(outfile)