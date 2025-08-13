#!/usr/bin/env python3
"""
Replicate Batch Process - Setup for PyPI distribution
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements
def read_requirements():
    """Read requirements from requirements.txt if exists"""
    req_file = os.path.join(this_directory, 'requirements.txt')
    if os.path.exists(req_file):
        with open(req_file, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return [
        'replicate>=0.15.0',
        'requests>=2.25.0',
        'asyncio-throttle>=1.0.2',
        'python-dotenv>=0.19.0',
    ]

setup(
    name='replicate-batch-process',
    version='1.1.0',
    author='preangelleo',
    author_email='',
    description='Intelligent batch processing tool for Replicate models with automatic fallback mechanisms',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/preangelleo/replicate_batch_process',
    project_urls={
        'Bug Reports': 'https://github.com/preangelleo/replicate_batch_process/issues',
        'Source': 'https://github.com/preangelleo/replicate_batch_process',
        'Documentation': 'https://github.com/preangelleo/replicate_batch_process#readme',
    },
    packages=find_packages(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Multimedia :: Graphics',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
    install_requires=read_requirements(),
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-asyncio>=0.21.0',
            'black>=22.0',
            'flake8>=4.0',
            'mypy>=0.950',
        ],
        'test': [
            'pytest>=6.0',
            'pytest-asyncio>=0.21.0',
        ]
    },
    entry_points={
        'console_scripts': [
            'replicate-batch=replicate_batch_process.main:main',
            'replicate-init=replicate_batch_process.init_environment:main',
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords=[
        'replicate',
        'ai',
        'batch-processing',
        'image-generation',
        'machine-learning',
        'api-client',
        'fallback-mechanism',
        'concurrent-processing'
    ],
)