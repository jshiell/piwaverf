import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="piwaverf",
    version="0.0.1",
    author="James Shiell",
    author_email="j+piwaverf@infernus.org",
    description="Tools for using a Raspberry Pi as a LightwaveRF hub",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jshiell/piwaverf",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=[
        "pigpio",
        "pyyaml"
    ]
)
