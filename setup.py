from setuptools import setup, find_packages

PACKAGE="ml4teens";

def read_version():
    with open(f"{PACKAGE}/version.py", "rt") as fd:
         locals = {};
         exec(fd.read(), None, locals);
         return locals["__version__"];

setup(
    name=PACKAGE,
    version=read_version(),
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
                       #"netifaces", Da problemas en windows (necesita c++ para ser compilado)
                       #"transformers>=4.37",
                       "transformers",
                       "torch==2.2.2",   # <------------ si algo falla pasa a 2.2.1
                       "torchaudio",
                       "mediapipe>=0.10.9",
                       "jupyter_ui_poll",
                       "openai",
                       #"gdown",
                       "matplotlib>=3.0",
                       "seaborn",
                       "cohere",
                       "tiktoken",
                       #"gradio==3.47.1",
                       "gradio",
                       #"imgbeddings==0.1.0",
                       "PyYAML",
                       "librosa",
                       #"webrtcvad",
                       "sounddevice",
                       "accelerate",
                       "ffmpeg",
                       "nsnet2-denoiser",
                       "pyaudio",
                       "scipy==1.12.0", # <-------------- hay un error en la 1.13.0
                       "imageio",
                       "plotly",
                       #"tensorflow",
                       "keras",
                       #"face_recognition",
                       "scikit-image",
                     ],
    include_package_data=True,
    
    # metadata para publicar en PyPI
    author='Francisco Puentes',
    author_email='fran@puentescalvo.com',
    description='Machine Learning para Adolescentes (Machine Learning for Teens)',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/FranPuentes/ML4Teens',
   )
