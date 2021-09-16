import os, sys, pathlib
try:
    from src import staticmetrics
except:
    pass
from setuptools import find_packages, setup, Command

here = os.path.abspath(os.path.dirname(__file__))
py_version = sys.version_info[:2]
NAME = 'staticmetrics'
AUTHOR = 'Myles Frantz',
DESCRIPTION = 'A useful tool for determing metrics from python projects and files.'
GH_NAME = "franceme"
URL = f"https://github.com/{GH_NAME}/{NAME}"
long_description = pathlib.Path(f"{here}/README.md").read_text(encoding='utf-8')
REQUIRES_PYTHON = '>=3.8.0'
VERSION = "0.0.1"
RELEASE = "?"
entry_point = f"src.{NAME}"


setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    keywords = ['static analysis', 'metrics'],
    command_options={
    },
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(
        exclude=["tests", "*.tests", "*.tests.*", "tests.*"]
    ),
    entry_points={
        'console_scripts': [f"mycli=src.{NAME}:main"],
    },
    install_requires=[
        "setuptools==51.1.2",
        "radon==4.3.2",
        "openpyxl==3.0.8",
        "pandas==1.1.0"
    ],
    include_package_data=True,
    license='Apache 2.0',
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        # 'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
    ],
    test_suite='tests.test_suites',
)
# endregion
