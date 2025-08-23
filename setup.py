from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="living-synthesizer",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A weather-controlled synthesizer system using RTL-SDR",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/newcubes/Living_Synthesizer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Multimedia :: Sound/Audio :: MIDI",
        "Topic :: Scientific/Engineering :: Atmospheric Science",
    ],
    python_requires=">=3.7",
    install_requires=[
        "numpy",
        "rtmidi",
    ],
    extras_require={
        "dev": [
            "pytest",
            "black",
            "flake8",
        ],
    },
    entry_points={
        "console_scripts": [
            "living-synthesizer=src.monitor:main",
        ],
    },
)
