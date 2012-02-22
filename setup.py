#! /usr/bin/env python

from setuptools import setup

setup(name='bdblog',
	version='0.1',
	description='Small Django Blog',
	keywords=['django', 'blog'],
	author='Dario Bertini',
	author_email='berdario@gmail.com',
	url='https://launchpad.net/bdblog',
	license='AGPL3',
	packages=[],
	install_requires=['django>=1.3', 'unidecode', 'diff_match_patch', 'python-openid', 'django_openid_auth', 'Pillow', 'pytz'])

