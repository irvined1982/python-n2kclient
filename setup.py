from setuptools import setup

setup(
    name='n2kclient',
    version='0.1',
    description='NMEA 2000 Client - makes it easier to send NMEA 2000 messages from python using socketcan',
    url='https://github.com/irvined1982/python-n2kclient',
    author='David Irvine',
    author_email='irvined@gmail.com',
    license='Apache-2.0',
    packages=['n2kclient'],
    scripts=['scripts/ds18b20_to_n2kbus'],
    zip_safe=False
)
