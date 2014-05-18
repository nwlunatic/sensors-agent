from setuptools import find_packages, setup

setup(
    name='sensors_agent',
    version='0.1',
    description='Service for serving lm-sensors and hddtemp temperature',
    long_description='',
    author='Igor Pavlov',
    author_email='nwlunatic@yandex.ru',
    packages=find_packages(),
    install_requires=[
        "pysensors",
    ],
    scripts=['bin/sensors_agent'],
)