import sys
import os

from setuptools import find_packages
from setuptools import setup
from pdai import __VERSION__

if sys.version_info < (3, 9, 0):
    raise OSError(f"QA AI requires Python >=3.9, but yours is {sys.version}")

PKG_ROOT = os.path.abspath(os.path.dirname(__file__))


def load_requirements() -> list:
    """Load requirements from file, parse them as a Python list!"""

    with open(os.path.join(PKG_ROOT, "requirements.txt"), encoding="utf-8") as f:
        all_reqs = f.read().split("\n")
    install_requires = [x.strip() for x in all_reqs if "git+" not in x]

    return install_requires


setup(
    name="qa-ai",
    version=__VERSION__,
    packages=find_packages(exclude=["contrib", "test-docs"]),
    install_requires=load_requirements(),
    url="",
    license="Apache License 2.0",
    author="alexbogatu",
    author_email="alex.bogatu@manchester.ac.uk",
    description="QA AI Tool",
)
