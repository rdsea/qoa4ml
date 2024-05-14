from setuptools import find_packages, setup

setup(
    name="qoa4ml",
    version=open("VERSION").read(),
    description="Quality of Analysis for Machine Learning",
    long_description=open("README.md").read() + "\n\n" + open("CHANGELOG.txt").read(),
    long_description_content_type="text/markdown",
    url="https://rdsea.github.io/",
    author="AaltoSEA",
    email="tri.m.nguyen@aalto.fi",
    keyword="Monitoring Machine Learning",
    install_requires=[line.strip() for line in open("requirements.txt").readlines()],
    extras_require={
        "ml": [line.strip() for line in open("ml_requirements.txt").readlines()],
        "dev": [line.strip() for line in open("dev_requirements.txt").readlines()],
    },
    packages=find_packages(),
    license="Apache License 2.0",
)
