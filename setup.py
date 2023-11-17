from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pathlib

from setuptools import find_packages, setup

here = pathlib.Path(__file__).parent.resolve()

install_requires = (here / 'requirements.txt').read_text(encoding='utf-8').splitlines()

setup(
    install_requires=install_requires,
    package_dir={'': 'lib',
                 'distronode_test': 'test/lib/distronode_test'},
    packages=find_packages('lib') + find_packages('test/lib'),
    entry_points={
        'console_scripts': [
            'distronode=distronode.cli.adhoc:main',
            'distronode-config=distronode.cli.config:main',
            'distronode-console=distronode.cli.console:main',
            'distronode-doc=distronode.cli.doc:main',
            'distronode-galaxy=distronode.cli.galaxy:main',
            'distronode-inventory=distronode.cli.inventory:main',
            'distronode-playbook=distronode.cli.playbook:main',
            'distronode-pull=distronode.cli.pull:main',
            'distronode-vault=distronode.cli.vault:main',
            'distronode-connection=distronode.cli.scripts.distronode_connection_cli_stub:main',
        ],
    },
)
