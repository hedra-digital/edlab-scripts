from setuptools import setup, find_packages

setup(
    name="voicing",
    version="0.1.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "azure-cognitiveservices-speech",
        "edge-tts",
        "gtts",
        "tqdm"
    ],
    entry_points={
        'console_scripts': [
            'voicing=voicing.voicing:main',
        ],
    },
    python_requires=">=3.8",
    author="Jorge Sallum",
    author_email="jorge@hedra.com.br",
    description="Uma ferramenta de linha de comando para síntese de voz",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown"
)