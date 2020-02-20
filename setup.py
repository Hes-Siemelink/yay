import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="yay",
    version="0.9-SNAPSHOT",
    author="Hes Siemelink",
    author_email="author@example.com",
    description="YAML script",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Hes-Siemelink/yay",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'pytest',
        'pyyaml',
        'requests',
        'jsonpath-ng',
        'PyInquirer',
        'flask',
        'python-arango'
    ],
    entry_points = {
        'console_scripts': [
            'yay = yay.__main__:main',
        ],
    },)
