from setuptools import setup, find_packages

setup(
    name="metronome",
    version="1.0",
    description="Custom metrics for SONiC",
    license="MIT",
    author="Said van de Klundert",
    author_email="saidvandeklundert@gmail.com",
    url="https://github.com/saidvandeklundert/metronome",
    maintainer="Said van de Klundert",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "metronome = metronome.metronome:main",
        ]
    },
    install_requires=[
        # NOTE: This package also requires swsscommon, but it is not currently installed as a wheel
        'enum39; python_version < "3.9"',
        "sonic-py-common",
    ],
    setup_requires=["wheel"],
    tests_require=[
        "pytest",
        "pytest-cov",
    ],
    classifiers=[
        "Development Status :: 1 - Beta",
        "Environment :: No Input/Output (Daemon)",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.9",
        "Topic :: System :: Hardware",
    ],
    keywords="sonic SONiC CUSTOM metrics",
)
