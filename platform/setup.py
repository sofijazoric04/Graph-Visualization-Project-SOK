from setuptools import setup, find_packages

setup(
    name="graph-platform",
    version="0.1.0",
    description="Platforma (Core) za vizualizaciju grafova - pretraga, filtriranje, workspace i komunikacija sa plugin-ovima",
    packages=find_packages(exclude=["tests", "tests.*"]),
    python_requires=">=3.10",
    install_requires=[
        # ovde treba da stoji za graph_visualizer "verzija" koja nam treba
        # tj treba u graph_visualizer da se stavi setup.py pa onda ovo da se popuni
    ],
    zip_safe=False,
)