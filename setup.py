from setuptools import find_packages, setup

setup(
    name="mawk",
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
)
