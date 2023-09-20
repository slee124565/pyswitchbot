from setuptools import setup, find_packages
from switchbot import __title__
from switchbot import __email__
from switchbot import __version__
from switchbot import __author__


def read_files(files):
    data = []
    for file in files:
        with open(file, encoding='utf-8') as f:
            data.append(f.read())
    return "\n".join(data)


long_description = read_files(['README.md'])

with open('requirements.txt') as f:
    install_requires = f.read().split('\n')

setup(
    name=__title__,
    version=__version__,
    description="A Python library for OpenWonderLabs SwitchBot API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    url="https://github.com/slee124565",
    author=__author__,
    author_email=__email__,
    license="MIT",
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=install_requires,
    python_requires='>=3.7',
    entry_points={
        "console_scripts": [
            "switchbot=switchbot.entrypoints.cli:switchbotcli",
        ],
    },
)
