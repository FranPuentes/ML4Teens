from setuptools import setup, find_packages

setup(
    name='ml4teens',
    version='0.1.18',
    packages=find_packages(),
    install_requires=[ "ipython", 
                       "opencv-python", 
                       "numpy",
                       "requests", 
                       "ultralytics", 
                       "Pillow", 
                       "ipycanvas==0.11",
                       "ipyevents",
                       "pandas>=1.3.4"
                     ],
    # metadata para publicar en PyPI
    author='Francisco Puentes',
    author_email='fran@puentescalvo.com',
    description='Machine Learning para Adolescentes',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/FranPuentes/ML4Teens',
)
