from distutils.core import setup

setup (name='crapvine',
      version='0.0.1',
      description='Python implementation of Grapevine',
      author='Andrew Sayman',
      author_email='lorien420@myrealbox.com',
      url='http://repo.or.cz/w/crapvine.git',
      license='GPLv3',
      packages=['crapvine'],
      package_dir={'crapvine': '.'},
      package_data={'crapvine': ['exchange_samples/*', 'interface/*'],
      requires=['dateutil']}
)
