from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="supertask",
    version="1.0.0",
    author="SuperTask Team",
    description="跨平台智能任务管理系统 - 基于Kivy框架",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Framework :: Kivy",
    ],
    python_requires=">=3.7",
    install_requires=[
        "kivy>=2.3.0",
        "requests>=2.31.0",
        "python-dateutil>=2.8.2",
    ],
    entry_points={
        "console_scripts": [
            "supertask=main:SuperTaskAppMain.run",
        ],
    },
)
