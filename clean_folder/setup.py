from setuptools import setup, find_packages

setup(
    name='clean_folder',
    version='0.0.15',
    author='Basil Egupov',
    packages=find_packages(),
    entry_points={
        'console_scripts': ['clean-folder=clean_folder.clean:main']
    }
)
