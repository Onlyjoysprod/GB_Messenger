from setuptools import setup, find_packages

setup(name='onlyjoys_messenenger_server',
      version='0.4.3',
      description='onlyjoys_messenenger_server',
      author='Roman Polevoy',
      author_email='kujaku@yandex.ru',
      packages=find_packages(),
      install_requires=['PyQT5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex']
      )