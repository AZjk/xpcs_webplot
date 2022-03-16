"""Top-level package for xpcs_webplot."""

__author__ = """Miaoqi Chu"""
__email__ = 'mqichu@anl.gov'


from pkg_resources import get_distribution, DistributionNotFound
try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    __version__ = "0.0.0"


import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s.%(msecs)03d %(name)s %(levelname)s | %(message)s',
                    datefmt='%m-%d %H:%M:%S')
logging.getLogger('boost_corr').addHandler(logging.NullHandler())