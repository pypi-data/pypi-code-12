from distutils.core import setup


setup(
    name="FromXLS2CSV",    # Nombre de la app (CamelCase)
    version="1",          # Version
    author="Miriam Olid", # Nombre del Autor
    author_email="molidg@gmail.com", # E-mail del autor
    packages=["fromxls2csv"],    # Paquetes a incluir
    license="GPL v3.0",     # Licencia
    description="Conversor de archivos XLS a CSV",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: Spanish",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 2 :: Only",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ]
)
