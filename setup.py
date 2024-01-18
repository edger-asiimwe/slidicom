from setuptools import setup, find_packages

with open("requirements.txt", 'r') as f:
    requirements = f.read().splitlines()

setup(
    name='slidicom',
    version='0.1',
    packages=find_packages(),
    url='https://github.com/edger-asiimwe/slidicom',
    author='Asiimwe Edgar',
    author_email='edgerasiimwe@gmail.com',
    description='A Python package for slidicom',
    license="MIT",
    install_requires=requirements,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
