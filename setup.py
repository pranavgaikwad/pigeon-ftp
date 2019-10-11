from setuptools import setup

setup(
    name='Pigeon FTP',
    version='0.0-dev',
    packages=['pftp', 'pftp.proto', 'pftp.server', 'pftp.utils', 'pftp.client'],
    author='Pranav Gaikwad, Jaymin Desai',
    include_package_data=True,
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=open('README.md').read(),
)
