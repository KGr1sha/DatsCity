from setuptools import setup
from Cython.Build import cythonize

setup(
    name="bomba app",
    ext_modules=cythonize("fast.py")
)
