import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

requires = [
    'pyramid',
    'pyramid_debugtoolbar',
    'pyramid_simpleform',
    'formencode',
    'waitress',
    'bcrypt',
    'sqlalchemy >= 0.9.3dev',
    'alembic >= 0.6.3',
    'psycopg2',
    'decorator'
    ]

setup(name='atmcraft',
      version='1.0',
      description='ATM-like simulation',
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='mike bayer',
      author_email='mike_mp@zzzcomputing.com',
      url='',
      keywords='web pyramid pylons',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=["nose", "mock"],
      test_suite="atmcraft",
      entry_points = {
        'console_scripts': ['clientcfg = atmcraft.model.client:console'],
        'paste.app_factory': ['main = atmcraft.application:main']
      }

      )