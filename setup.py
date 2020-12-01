from setuptools import setup

requirements = [
    'click',
    'enquiries',
]

with open('README.md') as f:
    readme = f.read()

setup(
    name = 'screen_recorder',
    version = '0.9.1',
    description = "Record Android & iOS screens as GIFs from the command line",
    long_description = readme,
    long_description_content_type = "text/markdown",
    license = "MIT",
    author = "Till Hellmund",
    author_email = 'thellmund@gmail.com',
    url = 'https://github.com/thellmund/screen-recorder',
    packages = ['screen_recorder'],
    entry_points = {
        'console_scripts': [
            'screen-recorder=screen_recorder.cli:main',
        ]
    },
    install_requires = requirements,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
