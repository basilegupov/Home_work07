from setuptools import setup, find_packages

setup(
    name='clean_folder',
    version='0.0.20',
    author='Basil Yegupov',
    packages=find_packages(),
    entry_points={
        'console_scripts': ['clean-folder=clean_folder.clean:main']
    }
)
