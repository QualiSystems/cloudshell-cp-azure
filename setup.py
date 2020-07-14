import os

from setuptools import find_packages, setup

with open(os.path.join("version.txt")) as version_file:
    version_from_file = version_file.read().strip()

with open("requirements.txt") as f_required:
    required = f_required.read().splitlines()

with open("test_requirements.txt") as f_tests:
    required_for_tests = f_tests.read().splitlines()

setup(
    name="cloudshell-cp-azure",
    url="http://www.qualisystems.com/",
    author="Quali",
    author_email="info@quali.com",
    packages=find_packages(),
    install_requires=required,
    tests_require=required_for_tests,
    test_suite="nose.collector",
    version=version_from_file,
    description="",
    include_package_data=True,
)
