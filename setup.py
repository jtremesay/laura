from setuptools import setup, find_packages

setup(
    name='laura',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
        'python-telegram-bot',
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
    url='https://git.slaanesh.org/killruana/laura',
)
