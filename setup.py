from setuptools import setup, find_packages


setup(
    name='laura',
    version='0.1-dev',
    packages=find_packages(),
    install_requires=[
        'beautifulsoup4',
        'FredIRC',
        'requests'
    ],
    entry_points={
        'console_scripts': [
            'laura = laura:main',
        ],
    },
    author='killruana',
    author_email='killruana@gmail.com',
    description='My bot',
    license='WTFPL',
    url='https://github.com/killruana/laura',
)
