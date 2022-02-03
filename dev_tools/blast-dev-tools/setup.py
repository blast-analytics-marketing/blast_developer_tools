from setuptools import setup, find_packages

requirements = [
    "pandas",
    "pytz",
    "toml",
]

setup(
    name="blast-dev-tools",
    version="1.0.3",
    description="Reusable Developer Tools Library",
    author="Emile Averill",
    author_email="emile.averill@blastam.com",
    python_requires=">=3.9,<4.0",
    packages=find_packages(),
    install_requires=requirements,
)
