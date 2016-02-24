try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
 
# from options["setup"] in build.vel

config = {
 'name': 'snappergui',
 'version': '0.1',
 'packages': ['snappergui'],
 'description': 'snapper-gui grafical user interface for snapper btrfs snapshot manager',
 'author': 'Ricardo Vieira',
 'url': 'https://github.com/ricardo-vieira/snapper-gui',
 'download_url': 'https://github.com/ricardo-vieira/snapper-gui',
 'author_email': 'ricardo.vieira@ist.utl.pt',
 'package_data' : {"snappergui": ["glade/*.glade",
 								"icons/*.svg",
 								"ui/*.ui"]},
 'data_files': [ ('share/applications', ['snapper-gui.desktop'])],
 'entry_points' : { 'gui_scripts' : 
                    [ 'snapper-gui = snappergui.application:start_ui' ] }
}

setup(**config)
