# -*- coding: utf-8 -*-

import io;
import numpy     as np;
import ml4teens  as ml;
import soundfile as sf;
import time;
import librosa;
from pydub import AudioSegment;

from openai import OpenAI

from ...core  import Block;
from ...core  import Context;
from ...tools import tools;

class TTS(Block):
      """
      Texto a audio usando el servicio de OpenAI.

      Params
      ------
      + voice: Uno de ["alloy", "echo", "fable", "onyx", "nova", "shimmer"].
      + speed: de 0.24 a 4, por defecto es 1.
      + split: por defecto False; si True debe hacer un split tratar cada uno independientemente.

      Slots
      -----
      + text: texto a convertir a audio.

      Signals
      -------
      + segment: audio en PCM.
      """
      
      def __init__(self, **kwargs):
          params, self._rest = tools.splitDict(["token","proxy","voice","speed","split","retries","timeout"], **kwargs);
          super().__init__(**params);
          context=Context();
          self._client =OpenAI(api_key     = self.params.token or context["OPENAI_TOKEN"],
                               max_retries = self.params.retries or 5,
                               timeout     = self.params.timeout or 10.0,
                               base_url    = self.params.proxy or context["OPENAI_PROXY"]);

      def _generate(self, text, delay=0):
          from openai import OpenAI;
          response = self._client.audio.speech.create(input=text, model="tts-1", voice=self.params.voice or "nova", response_format="pcm", speed=self.params.speed or 1);
          buffer = io.BytesIO();
          for chunk in response.iter_bytes(chunk_size=4096):
              buffer.write(chunk);
          buffer.seek(0);
          data = np.frombuffer(buffer.read(), dtype='<i2');
          data = librosa.resample(data.astype(float), orig_sr=24000, target_sr=self.context.default.AudioSampleRate);
          data=np.clip(data, -2**15, 2**15-1).astype(np.int16);
          if delay>0:
             zeros = np.zeros(int(self.context.default.AudioSampleRate*delay), dtype=np.int16);
             data=np.concatenate((zeros,data));
          self.signal_segment(data);

      @Block.slot("text",{str})
      def slot_text(self, slot, data):
          if data:

             if self.params.split is None or not bool(self.params.split):
                self._generate(str(data));

             else:
                for c, text in enumerate([t.strip() for t in str(data).split('\n')]):
                    if text:
                       if c>0 and isinstance(self.params.split,(int,float,str)): delay=float(self.params.split);
                       else:                                                     delay=0;
                       self._generate(text, delay);

             return True;

          return False;

      @Block.signal("segment", np.ndarray)
      def signal_segment(self, data):
          return data;

###########################################################################################################
class STT(Block):
      """
      De audio a texto usando el servicio de OpenAI.

      Params
      ------
      + language: idioma en el que está escrito el texto.
      + prompt: contexto que ayudará al modelo a dar significado al texto.

      Slots
      -----
      + segment: audio a convertir a texto.

      Signals
      -------
      + text: texto reconocido
      """
      
      def __init__(self, **kwargs):
          params, self._rest = tools.splitDict(["token", "retries", "timeout", "proxy", "language", "prompt", "temperature"], **kwargs);
          super().__init__(**params);
          context=Context();
          self._client =OpenAI(api_key     = self.params.token or context["OPENAI_TOKEN"],
                               max_retries = self.params.retries or 5,
                               timeout     = self.params.timeout or 10.0,
                               base_url    = self.params.proxy or context["OPENAI_PROXY"]);

      @Block.slot("segment",{np.ndarray})
      def slot_segment(self, slot, data):
          if data is not None:
             sound = AudioSegment(data=data.tobytes(), sample_width=data.dtype.itemsize, frame_rate=self.context.default.AudioSampleRate, channels=1);
             buffer = io.BytesIO();
             sound.export(buffer, format="mp3", );
             buffer.seek(0);
             buffer.name="ml4teens.mp3";
             transcription = self._client.audio.transcriptions.create(model="whisper-1",
                                                                      file=buffer,
                                                                      language=self.params.language or "es",
                                                                      prompt=self.params.prompt or None,
                                                                      temperature=self.params.temperature or 0,
                                                                      response_format="text",
                                                                     );
             self.signal_text(transcription);

      @Block.signal("text", str)
      def signal_text(self, data):
          return data;

################################################################################

import openai;
import json;

from openai import OpenAI;

from ...core import Context;
from ...core import Block;

################################################################################
class Chat(Block):
      """
      Recibe una 'question' y responde con un 'answer'.
      Acumula la iteracción hasta que recibe un nuevo "context".
      """

      class QUERY:

            def __init__(self, client, messages:list):
                self.client=client;
                self.prompt=messages;
                self.aoigen=None;
                self.reason=None;

            def __iter__(self):
                return self;

            def __next__(self):
                if self.reason=="stop":   raise StopIteration();
                if self.reason=="length": raise StopIteration();
                if self.aoigen==None:
                   try:
                     self.aoigen=self.client.chat.completions.create(model="gpt-3.5-turbo", messages=self.prompt, stream=True);
                       
                   except openai.APIConnectionError as e:
                     raise e;
                       
                   except openai.RateLimitError as e:
                     raise e;
                       
                   except openai.APIStatusError as e:
                     raise e;
                       
                   except Exception as e:
                     raise StopIteration();

                for chunk in self.aoigen:
                    return (chunk.choices[0].delta.content or "");

      #-------------------------------------------------------------------------
      # Constructor
      #-------------------------------------------------------------------------
      def __init__(self, **kwargs):
          super().__init__(**kwargs);
          context=Context.instance;
          self._client =OpenAI(api_key=self.params.token or context["OPENAI_TOKEN"],
                               max_retries=self.params.max_retries or 2,
                               timeout=self.params.timeout or 10.0,
                               base_url=self.params.proxy or context["OPENAI_PROXY"]);
          self._context=self.params.context or "";
          self._history=[];

      #-------------------------------------------------------------------------
      # SLOTS
      #-------------------------------------------------------------------------
      @Block.slot("context",{str})
      def slot_context(self, slot, data):
          self._context=data or self.params.context or self._context;
          self._history=[];

      #-------------------------------------------------------------------------
      @Block.slot("question",{object})
      def slot_question(self, slot, data):
         
          if data is not None and isinstance(data,(str,)):
             if len(self._history)==0:  self._history.append("");
             self._history.append(data);
             messages=[];
    
             for i,h in enumerate(self._history):
                 if    i==0   : messages.append({"role":"system",    "content":h});
                 elif (i%2)==1: messages.append({"role":"user",      "content":h});
                 elif (i%2)==0: messages.append({"role":"assistant", "content":h});
    
             try:
               """
               response="";
               for token in self.QUERY(self._client, messages):
                   if token is not None: response += token;
                   else:                 break;
               """
               response = self._client.chat.completions.create(messages=messages, model=self.params.model or "gpt-3.5-turbo");
               if isinstance(response, str):
                  response=json.loads(response);               
               response = response.choices[0].message.content;
    
             except Exception as e:
               print(e, flush=True);  
               if not response:
                  response="Me temo que se ha producido un error. Vuelve a intentarlo otra vez por favor.";
    
             finally:
               self._history.append(response);
               self.signal_answer  (response);

      #-------------------------------------------------------------------------
      # SIGNALS
      #-------------------------------------------------------------------------
      @Block.signal("answer",str)
      def signal_answer(self, data):
          return data;

