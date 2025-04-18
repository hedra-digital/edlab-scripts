from setuptools import setup, find_packages

setup(
    name="edlab-filemanager",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "colorama",
        "pathlib",
    ],
    entry_points={
        "console_scripts": [
            "edlab-filemanager=edlab_filemanager.cli:main",
        ],
    },
    python_requires=">=3.8",
    author="Your Name",
    author_email="your.email@example.com",
    description="File manager for renaming files based on a table or aligning numerical place values",
    long_description="A tool for renaming files based on a table or aligning numerical place values",
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/edlab-filemanager",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)