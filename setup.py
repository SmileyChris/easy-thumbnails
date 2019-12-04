#!/usr/bin/env python
from __future__ import unicode_literals
import codecs
import os
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

import easy_thumbnails


class DjangoTests(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        from django.core import management
        DSM = 'DJANGO_SETTINGS_MODULE'
        if DSM not in os.environ:
            os.environ[DSM] = 'easy_thumbnails.tests.settings'
        management.execute_from_command_line()


def read_files(*filenames):
    """
    Output the contents of one or more files to a single concatenated string.
    """
    output = []
    for filename in filenames:
        f = codecs.open(filename, encoding='utf-8')
        try:
            output.append(f.read())
        finally:
            f.close()
    return '\n\n'.join(output)


setup(
    name='easy-thumbnails',
    version=easy_thumbnails.get_version(),
    url='http://github.com/SmileyChris/easy-thumbnails',
    description='Easy thumbnails for Django',
    long_description=read_files('README.rst', 'CHANGES.rst'),
    author='Chris Beaven',
    author_email='smileychris@gmail.com',
    platforms=['any'],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'django>=1.8,<2;python_version<"3"',
        'django>=1.8;python_version>="3"',
        'pillow<4;python_version<"2.7"',
        'pillow;python_version>="2.7"',
        'six'
    ],
    cmdclass={'test': DjangoTests},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    zip_safe=False,
)
