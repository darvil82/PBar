import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PBar2",
    version="1.9.0",
    author="David Losantos (DarviL82)",
    author_email="davidlosantos89@gmail.com",
    description="Display customizable progress bars on the terminal easily.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DarviL82/PBar",
    project_urls={
        "Bug Tracker": "https://github.com/DarviL82/PBar/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.9",
)