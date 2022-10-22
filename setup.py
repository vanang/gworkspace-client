from setuptools import setup, find_packages

setup(
    name='gworkspace_client',
    version='0.0.1',
    packages=['gworkspace_client'],
    package_dir={'gworkspace_client': 'gworkspace_client'},
    url='https://github.com/vanang/core-gsuite-client',
    license='MIT-2.0',
    author='taek900',
    author_email='vanang7@gmail.com',
    description='A set of wrapper classes for Google Workspace API',
    install_requires=[
        'google-api-core==2.7.1',
        'google-api-python-client==2.40.0',
        'google-auth==2.6.0',
        'google-auth-httplib2==0.1.0',
        'google-auth-oauthlib==0.5.0',
        'googleapis-common-protos==1.55.0',
        'pandas',
    ],
    python_requires='>=3.8'

)
