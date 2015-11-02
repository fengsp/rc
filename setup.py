import re
from setuptools import setup


with open('rc/__init__.py', 'rb') as f:
    version = str(eval(re.search(r'__version__\s+=\s+(.*)',
        f.read().decode('utf-8')).group(1)))


setup(
    name='rc',
    author='Shipeng Feng',
    author_email='fsp261@gmail.com',
    version=version,
    url='http://github.com/fengsp/rc',
    packages=['rc'],
    description='rc, the redis cache',
    install_requires=[
        'redis>=2.6',
    ],
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
    ],
)
