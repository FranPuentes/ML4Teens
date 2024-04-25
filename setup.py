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
                       "ipywidgets==7.7.1",
                       "pandas>=1.3.4",
                       #"transformers>=4.37",
                       "transformers",
                       "torch==2.2.2",   # <------------ si algo falla pasa a 2.2.1
                       "mediapipe>=0.10.9",
                       "jupyter_ui_poll",
                       "openai",
                       #"gdown",
                       "matplotlib>=3.0",
                       "seaborn",
                       "cohere",
                       "tiktoken",
                       #"gradio==3.47.1",
                       "gradio==4.27",
                       #"imgbeddings==0.1.0",
                       "PyYAML",
                       "librosa",
                       "webrtcvad",
                       "sounddevice",
                       "openai-whisper",
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
