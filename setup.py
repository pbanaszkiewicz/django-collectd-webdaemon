#!/usr/bin/env python
# coding: utf-8

from setuptools import setup

setup(
    name="django-collectd-webdaemon",
    version="0.1",
    description="A proxy-like application which talks with collectd-webdaemon"
    " server.",
    author="Piotr Banaszkiewicz",
    author_email="piotr@banaszkiewicz.org",
    url="https://github.com/pbanaszkiewicz/django-collectd-webdaemon",
    packages=["collectd_webdaemon"],
    include_package_data=True,
    install_requires=["requests>=0.9", "pygal>=0.10"],
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Framework :: Django",
        "Topic :: System :: Monitoring",
    ],
)
