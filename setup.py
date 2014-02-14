import setuptools


setuptools.setup(
    name='openstackhud',
    version='1.0',
    long_description=__doc__,
    packages=['openstackhud'],
    include_package_data=True,
    zip_safe=False,
    test_suite='tests',
    install_requires=[
        'Flask',
        'dogpile.cache'])
