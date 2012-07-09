# -*- coding: utf-8 -*-
from distutils.core import setup

setup(
    name='3scale',
    version='1.0',
    py_modules=['ThreeScalePY'],
    py_modules=['ThreeScalePY'],

    author_email = "support@3scale.net",
    url = "https://github.com/3scale/3scale_ws_api_for_python",

    classifiers = [
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Internet",
        "Topic :: Software Development",
        ],

    long_description=open('README.markdown').read(),
)

