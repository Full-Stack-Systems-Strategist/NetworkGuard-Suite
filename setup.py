from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="NetworkGuard-Suite",
    version="1.0.0",
    author="Full-Stack-Systems-Strategist",
    description="A comprehensive network security toolkit for ARP spoofing detection and port hardening",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Full-Stack-Systems-Strategist/NetworkGuard-Suite",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Information Technology",
        "Topic :: Security",
        "Topic :: System :: Networking",
        "Topic :: System :: Systems Administration",
    ],
    python_requires=">=3.8",
    install_requires=[
        "scapy>=2.4.5",
    ],
    entry_points={
        "console_scripts": [
            "networkguard=Network_Guard:main",
            "port-hardener=Python_script_to_identify_and_close_open:main",
        ],
    },
)