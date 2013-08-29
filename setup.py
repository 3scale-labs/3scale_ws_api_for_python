# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='ThreeScalePY',
    version='1.5.2',
    author='3scale',
    author_email='support@3scale-net',
    url="https://github.com/3scale/3scale_ws_api_for_python",
    py_modules=['ThreeScalePY'],
    dependency_links=[
        "ftp://xmlsoft.org/libxml2/python/libxml2-python-2.6.21.tar.gz"
    ]
)

