#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="edlab-pdfmanager",
    version="0.1.0",
    description="Ferramenta para manipulação de arquivos PDF: juntar, remover texto, cortar margens, extrair páginas e muito mais",
    author="EdLab",
    author_email="contato@edlab.com",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "PyPDF2>=3.0.0",
        "pymupdf>=1.22.0",
        "pdf2image>=1.16.0",
        "reportlab>=3.6.0",
        "pdfminer.six>=20211012",
        "pdf2docx>=0.5.6",
        "Pillow>=10.0.0",
        "numpy>=1.23.0",
        "opencv-python>=4.7.0",
        "tqdm>=4.65.0",
    ],
    entry_points={
        "console_scripts": [
            "edlab-pdfmanager=edlab_pdfmanager.cli:main",
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
        "Topic :: Utilities",
    ],
)