from setuptools import setup, find_packages

setup(
    name="petriEBN",
    version="0.1.0",
    author="Elizabeth Andreas, Eli Quist, and Tomáš Gedeon",
    author_email="eli.quist@student.montana.edu",
    description="Representing expanded boolean networks as Petri nets to compute Morse Graphs of ODE models",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/quistew/petriEBN",
    packages=find_packages(),
    install_requires=[
       "DSGRN",
        
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
