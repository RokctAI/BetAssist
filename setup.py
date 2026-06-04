from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in betassist/__init__.py
from betassist import __version__ as version

setup(
	name="betassist",
	version=version,
	description="Betting intelligence and risk management platform",
	author="Rokct",
	author_email="hello@rokct.io",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
