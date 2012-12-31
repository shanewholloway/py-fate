# -*- coding: utf-8 -*- vim: set ts=4 sw=4 expandtab
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##
##~ Copyright (C) 2002-2013  TechGame Networks, LLC.              ##
##~                                                               ##
##~ This library is free software; you can redistribute it        ##
##~ and/or modify it under the terms of the MIT style License as  ##
##~ found in the LICENSE file included with this distribution.    ##
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##

from distutils.core import setup

__version__ = '0.0.0'

setup(
    name='fate', 
    version=__version__,
    license='MIT',
    author='Shane Holloway',
    author_email='shane@techgame.net',
    description='Futures, Promises and Deferreds',
    url='http://github.com/shanewholloway/py-fate.git',
    download_url='https://github.com/shanewholloway/py-fate.git',
    py_modules=['fate'],

    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
        'Development Status :: 1 - Planning', #'Development Status :: 3 - Alpha',
        ])


