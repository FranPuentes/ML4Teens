from setuptools import setup, find_packages

setup(
    name='ml4teens',
    version='0.1.25',
    packages=find_packages(),
    install_requires=[ "ipython>=3.8", 
                       "opencv-python", 
                       "numpy",
                       "requests", 
                       "ultralytics", 
                       "Pillow", 
                       "ipycanvas==0.11",
                       "ipyevents",
                       "ipywidgets",
                       "pandas>=1.3.4",
                       "transformers",
                       "torch",
                       "face_recognition",
                       "jupyter_ui_poll",
                     ],
    # metadata para publicar en PyPI
    author='Francisco Puentes',
    author_email='fran@puentescalvo.com',
    description='Machine Learning para Adolescentes',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/FranPuentes/ML4Teens',
)
