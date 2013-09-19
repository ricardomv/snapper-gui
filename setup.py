try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
 
# from options["setup"] in build.vel

config = {
 'description': 'snapper-gui grafical user interface for snapper btrfs snapshot manager',
 'author': 'Ricardo Vieira',
 'url': 'https://github.com/ricardo-vieira/snapper-gui',
 'download_url': 'https://github.com/ricardo-vieira/snapper-gui',
 'author_email': 'ricard.vieira@ist.utl.pt',
 'version': '0.1',
 'packages': ['snapper-gui'],
 'name': 'python-snapper-gui'
}

setup(**config)