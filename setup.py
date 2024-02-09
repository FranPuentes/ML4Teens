from setuptools import setup, find_packages

setup(
    name='ml4teens',
    version='0.1.34',
    packages=find_packages(),
    install_requires=[ "ipython",
                       "opencv-python>=4.9",
                       "numpy",
                       "requests", 
                       "ultralytics", 
                       "Pillow", 
                       "ipycanvas==0.11",
                       "ipyevents",
                       "ipywidgets",
                       "pandas>=1.3.4",
                       #"transformers>=4.37",
                       "torch==2.1.0",
                       "mediapipe>=0.10.9",
                       "jupyter_ui_poll",
                       "openai",
                       #"gdown",
                       "matplotlib>=3.0",
                       "seaborn",
                       "cohere",
                       "tiktoken",
                       #"imgbeddings==0.1.0",
                     ],
    include_package_data=True,
    
    # metadata para publicar en PyPI
    author='Francisco Puentes',
    author_email='fran@puentescalvo.com',
    description='Machine Learning para Adolescentes',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/FranPuentes/ML4Teens',
)
