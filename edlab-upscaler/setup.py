from setuptools import setup, find_packages

setup(
    name="upscaler",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "torch>=2.6.0",
        "torchvision>=0.21.0",
        "numpy>=2.1.3",
        "Pillow>=11.1.0"
    ],
    entry_points={
        'console_scripts': [
            'upscaler=upscaler.upscaler:main',
        ],
    },
    python_requires=">=3.12",
    author="Jorge Sallum",
    author_email="jorge@hedra.com.br",
    description="Uma ferramenta de linha de comando para aumento de resolução de imagens usando Real-ESRGAN",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown"
)
