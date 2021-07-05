import io
import os
import re

from setuptools import find_packages, setup


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


with io.open('bulletin/version.py', 'rt', encoding='utf-8') as f:
    version = re.search(r"__version__ = '(.*?)'", f.read()).group(1)

description = 'WebObs to seismic bulletin utility library.'

setup(
    name='bulletin',
    version=version,
    description=description,
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    license='MIT',
    install_requires=[
        'numpy',
        'pandas',
        'sqlalchemy',
        'obspy',
        'webobsclient',
    ],
    author='Indra Rudianto',
    author_email='indrarudianto.official@gmail.com',
    url='https://gitlab.com/bpptkg/bulletin',
    zip_safe=True,
    packages=find_packages(exclude=['tests', 'docs']),
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Operating System :: POSIX :: Linux',
        'Intended Audience :: Science/Research',
        'Natural Language :: Indonesian',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ]
)
