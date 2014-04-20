#! /usr/bin/env python2

import sys
from distutils.core import setup

# Patch distutils if it can't cope with
# the "classifiers" or "download_url" keywords.
if sys.version < '2.2.3':
  from distutils.dist import DistributionMetadata
  DistributionMetadata.classifiers = None
  DistributionMetadata.download_url = None

#
# Setup.
#
setup(name='myagtd',
      version='0.3.4',
      description='My Yet Another Getting Things Done',
      author='Mikael NAVARRO & wxg',
      author_email='klnavarro@free.fr & wxg4dev@gmail.com',
      contact='wxg',
      contact_email='wxg4dev@gmail.com',
      long_description='A primitive Getting Things Done to-do list manager.',
      license='GNU General Public License',
      url='https://github.com/wxg4net/myagtd',
      download_url = 'https://github.com/wxg4net/myagtd/archive/master.zip',
      platforms='Theorically all platforms.',
      package_dir = {'': 'src'},
      packages = [''],
      data_files = [('share/doc/myagtd', ['AUTHORS', 'COPYING', 'LICENCE',
                                         'README', 'LISEZMOI', 'INSTALL',
                                         'NEWS', 'ChangeLog']),
                    ('share/doc/myagtd/rest', ['doc/myagtd.rest', 'doc/myagtd.png',
                                              'doc/myagtd.html', 'doc/default.css']),
                    ('share/man/man1', ['doc/myagtd.1']),
                    ('share/myagtd', ['src/client_secrets.json']),
                    ('share/doc/myagtd/tools', ['tools/myagtd-mode.el',
                                               'tools/myagtd-s60.py',
                                               'tools/myagtd-cli.py',
                                               'tools/myagtd.sh'])],
      scripts=['src/myagtd.py'],
      classifiers = ['Development Status :: 4 - Beta',
                     'Intended Audience :: End Users/Desktop',
                     'Environment :: Console (Text Based)',
                     'License :: OSI Approved :: GNU General Public License (GPL)',
                     'Operating System :: OS Independent',
                     'Programming Language :: Python',
                     'Topic :: Office/Business']
      )
