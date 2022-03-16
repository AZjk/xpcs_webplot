"""Top-level package for xpcs_webplot."""

__author__ = """Miaoqi Chu"""
__email__ = 'mqichu@anl.gov'


from pkg_resources import get_distribution, DistributionNotFound
try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    __version__ = "0.0.0"


import logging
logging.getLogger('xpcs_webplot').addHandler(logging.NullHandler())