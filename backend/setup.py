from setuptools import setup, find_packages

# Read requirements from requirements.txt
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="learning_path_backend",
    version="0.1.0",
    packages=find_packages(),
    install_requires=requirements,
    python_requires='>=3.8',
    author="Your Name",
    author_email="your.email@example.com",
    description="Backend for Personalized Learning Path Application",
    url="https://github.com/nabeelsyed11/personalized-learning-path",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'learning-path=app.main:main',
        ],
    },
)
