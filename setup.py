import setuptools


setuptools.setup(
    name='gatewatch',
    version='1.0',
    long_description=__doc__,
    packages=['gatewatch'],
    include_package_data=True,
    zip_safe=False,
    test_suite='tests',
    install_requires=[
        'Flask',
        'requests',
        'celery',
        'redis',
        'dogpile.cache'])
