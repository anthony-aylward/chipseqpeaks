import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='chipseqpeaks',
    version='1.1.0',
    author='Anthony Aylward, Joshua Chiou',
    author_email='aaylward@eng.ucsd.edu',
    description='Easy management of ChIP-seq peak calling',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/anthony-aylward/chipseqpeaks.git',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    install_requires=[],
    entry_points={
        'console_scripts': ['chipseqpeaks-call=chipseqpeaks.call_peaks:main',]
    },
    include_package_data=True
)
