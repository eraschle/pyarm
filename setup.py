from setuptools import find_namespace_packages, setup

setup(
    name="pyarm",
    package_dir={"": "src"},
    packages=find_namespace_packages(where="src"),
    package_data={
        "pyarm": ["py.typed"],
    },
    python_requires=">=3.8",
    entry_points={
        "pyarm.plugins": [
            # Hier koennten kernintegrierte Plugins registriert werden
        ],
    },
)
