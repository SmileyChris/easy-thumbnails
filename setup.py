#!/usr/bin/env python
from distutils.core import setup
import easy_thumbnails


def read_files(*filenames):
    """
    Output the contents of one or more files to a single concatenated string.
    """
    output = []
    for filename in filenames:
        f = open(filename)
        try:
            output.append(f.read())
        finally:
            f.close()
    return '\n\n'.join(output)


setup(
    name='easy-thumbnails',
    version=easy_thumbnails.VERSION,
    url='http://github.com/SmileyChris/easy-thumbnails',
    description='Easy thumbnails for Django',
    long_description=read_files('README.rst', 'CHANGES.rst'),
    author='Chris Beaven',
    author_email='smileychris@gmail.com',
    platforms=['any'],
    packages=[
        'easy_thumbnails',
        'easy_thumbnails.management',
        'easy_thumbnails.management.commands',
        'easy_thumbnails.migrations',
        'easy_thumbnails.templatetags',
        'easy_thumbnails.tests',
    ],
    package_data={'easy_thumbnails': ['docs/*', 'docs/ref/*.rst']},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    zip_safe=False,
)
