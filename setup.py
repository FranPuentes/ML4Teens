from setuptools import setup, find_packages

setup(
    name='ml4teens',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        # Aquí puedes listar las dependencias de tu paquete, si las hay
    ],
    # metadata para publicar en PyPI
    author='Francisco Puentes',
    author_email='fran@puentescalvo.com',
    description='Machine Learning para Adolescentes (o más) ...',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/FranPuentes/ML4Teens',
)
