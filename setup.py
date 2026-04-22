from setuptools import find_packages, setup

MAIN_REQUIREMENTS = [
    "airbyte-cdk>=7.13.0,<8.0.0",
    "requests>=2.31.0",
]

setup(
    name="source-zendesk-custom",
    version="0.1.0",
    description="Airbyte source for Zendesk Support (tickets, users, comments, organizations, tags)",
    author="Tripti Sharma",
    packages=find_packages(),
    install_requires=MAIN_REQUIREMENTS,
)
