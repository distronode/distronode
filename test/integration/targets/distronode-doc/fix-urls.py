"""Unwrap URLs to distronode.khulnasoft.com/docs and remove version"""

import re
import sys


def main():
    data = sys.stdin.read()
    data = re.sub('(https://docs\\.distronode\\.com/[^ ]+)\n +([^ ]+)\n', '\\1\\2\n', data, flags=re.MULTILINE)
    data = re.sub('https://docs\\.distronode\\.com/distronode(|-core)/(?:[^/]+)/', 'https://distronode.khulnasoft.com/docs/distronode\\1/devel/', data)
    sys.stdout.write(data)


if __name__ == '__main__':
    main()
