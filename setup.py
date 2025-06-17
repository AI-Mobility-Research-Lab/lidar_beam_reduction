from setuptools import setup, find_packages

# Read the README file for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="lidar_beam_reduction",
    version="1.0.0",
    description="Tools for reducing the number of beams in LiDAR point clouds",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="AI & Mobility Research Lab",
    author_email="cnpcshangbin@gmail.com",
    url="https://yiqiao-li.github.io",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "scipy",
        "scikit-learn",
        "matplotlib",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
            "flake8",
        ],
        "ply": [
            "plyfile",
        ],
    },
    entry_points={
        "console_scripts": [
            "reduce_beams=lidar_beam_reduction.command_line:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    keywords="lidar pointcloud beam reduction 3d",
) 