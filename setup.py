from setuptools import setup


setup(
    name='pynsodm',
    zip_safe=True,
    version='0.3.2',
    description='Smart ODM for NoSQL (RethinkDB, Redis, etc.)',
    url='https://github.com/agratoth/pynsodm',
    maintainer='Anton Berdnikov',
    maintainer_email='agratoth@yandex.ru',
    packages=[
      'pynsodm',
      'pynsodm.exceptions',
      'pynsodm.fields',
      'pynsodm.handlers',
      'pynsodm.json_ext',
      'pynsodm.rethinkdb_ext',
      'pynsodm.valids',
    ],
    package_dir={'pynsodm': 'pynsodm'},
    install_requires=[
      'rethinkdb>=2.4.8',
      'validators>=0.18.2',
      'python-dotenv>=0.15.0',
      'pytz>=2021.1'],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Database",
        "Topic :: Database :: Front-Ends",
    ],
    python_requires='>=3.8',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
)
