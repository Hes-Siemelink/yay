import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="yay",
    version="0.2",
    author="Hes Siemelink",
    author_email="author@example.com",
    description="YAML script",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Hes-Siemelink/yay",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
