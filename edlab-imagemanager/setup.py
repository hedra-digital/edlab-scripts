#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="edlab-imagemanager",
    version="0.1.0",
    description="Ferramenta para processamento de imagens com adição de bordas e centralização em fundo quadrado",
    author="EdLab",
    author_email="contato@edlab.com",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "Pillow>=9.0.0",
    ],
    entry_points={
        "console_scripts": [
            "edlab-imagemanager=edlab_imagemanager.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Graphics",
    ],
)