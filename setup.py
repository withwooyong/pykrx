import re

from setuptools import find_packages, setup  # type: ignore[import-untyped]

# __version__을 파일에서 직접 읽기 (import 없이)
with open("pykrx/__init__.py", encoding="utf-8") as f:
    version_match = re.search(r"^__version__\s*=\s*['\"]([^'\"]*)['\"]", f.read(), re.MULTILINE)
    __version__ = version_match.group(1) if version_match else "1.0.51"

with open("README.md", encoding="UTF-8") as fh:
    long_description = fh.read()

setup(
    name="pykrx",
    version=__version__,
    description="KRX data scraping",
    url="https://github.com/sharebook-kr/pykrx/",
    author="Brayden Jo, Jonghun Yoo",
    author_email=("brayden.jo@outlook.com, jonghun.yoo@outlook.com, pystock@outlook.com"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "requests",
        "pandas",
        "numpy",
        "xlrd",
        "deprecated",
        "multipledispatch",
        "matplotlib",
    ],
    license="MIT",
    packages=find_packages(include=["pykrx", "pykrx.*", "pykrx.stock.*"]),
    package_data={
        "pykrx": ["*.ttf"],
    },
    python_requires=">=3",
    zip_safe=False,
)
