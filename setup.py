from setuptools import setup, find_packages

setup(name='chianti-pearl',
      description='A module that can parse Korean movie theater data, including CGV, Lotte Cinema, and Megabox.',
      version='1.0.1',
      url='https://github.com/chiantishiina/pearl',
      author='Chianti Shiina',
      author_email='chianti.shiina@gmail.com',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Programming Language :: Python :: 3'
      ],
      packages=find_packages(exclude=['contrib', 'docs', 'tests']),
      install_requires=[
          'colorama'
      ]
      )
