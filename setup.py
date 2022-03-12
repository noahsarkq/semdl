from setuptools import setup, find_packages

VERSION = "1"
DESCRIPTION = "SemDownloader"
LONG_DESC = open("./README.md", "r").read()
KEYWORDS = "Semdl"
CLASSIFIERS = [
    "Programming Language :: Python :: 3",
    "Operating System :: OS Independent",
]
setup(
    name="semdl",
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESC,
    long_description_content_type="text/markdown",
    classifiers=CLASSIFIERS,
    keywords=KEYWORDS,
    packages=find_packages(),
    py_modules=["semdl"],
    entry_points={"console_scripts": [
        "semdl=semdl:main",
    ]},
    install_requires=["aiofiles", "yt-dlp"],
    zip_safe=True,
)
