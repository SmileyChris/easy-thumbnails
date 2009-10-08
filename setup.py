#!/usr/bin/env python
from distutils.core import setup


VERSION = '1.0a' 

README_FILE = open('README')
try:
    long_description = README_FILE.read()
finally:
    README_FILE.close()

 
setup(
    name='easy-thumbnails',
    version=VERSION,
    #url='',
    #download_url=''  % VERSION,
    description='Easy thumbnails for Django',
    long_description=long_description,
    author='Chris Beaven',
    email='smileychris@gmail.com',
    platforms=['any'],
    packages=[
        'easy_thumbnails',
        'easy_thumbnails.templatetags',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
