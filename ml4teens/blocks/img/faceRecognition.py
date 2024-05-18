# -*- coding: utf-8 -*-

import os;
import requests;
import numpy as np;
import PIL;
#import cv2;

#from transformers import AutoImageProcessor, ViTModel;
#import torch;

#from ultralytics import YOLO;

from tempfile import NamedTemporaryFile;

from PIL.Image import Image;

import face_recognition;

#from IPython.display import display as IDisplay;

from ...core import Context;
from ...core import Block;

class FaceRecognition(Block):
      """
      Dada una imagen de referencia (slot "reference"), con una o más caras que pueden ser detectadas, aprende a reconocer dichas caras en las sucesivas imágenes que se le entreguen (slot "image").

      Se le puede entregar al constructor un objeto Image (param "reference") para tener una referencia desde el principio.

      Emite dos señales:

      1) Un diccionario con las caras reconocidas (signal "recognized").
      2) La imagen de entrada (slot "image") con las caras reconocidas (slot/param "reference").

      El formato del diccionario con las facciones reconocidas es el mismo que el de la identificacioón de caras (FaceBoxing) + la etiqueta de la cara reconocida.
      """

      #-------------------------------------------------------------------------
      @staticmethod
      def download(source:str):
          if source.startswith("http"):
             with requests.get(source, stream=True) as r:
                  r.raise_for_status();
                  with NamedTemporaryFile(delete=False) as f:
                       for chunk in r.iter_content(chunk_size=65536//8):
                           f.write(chunk);
                       fuente = f.name;
                       istemp = True;
          else:
             fuente = source;
             istemp = False;

          return (fuente, istemp);

      #-------------------------------------------------------------------------
      @staticmethod
      def boxes(model, imagen, minconf=0.0):
          results = model(imagen, stream=False, verbose=False);
          rt=[];
          for r in results:
              boxes=[{ "trust": float(c), 
                       "xyxy" : [int(_) for _ in k],
                       "xy":    [[int(_) for _ in l]  for l in p], }
                     for c,k,p in zip(r.boxes.conf, r.boxes.xyxy, r.keypoints.xy) if float(c)>=minconf];
              rt += boxes;
          return rt;             
          
      #-------------------------------------------------------------------------
      def encodings(self, imagen, minconf=0.0):
          rt=[];
          boxes = FaceRecognition.boxes(self._facem, imagen, minconf=minconf);
          for box in boxes:
              conf           = box["trust"];
              x1, y1, x2, y2 = box["xyxy" ];
              l1,l2,l3,l4,l5 = box["xy"   ];
              face = imagen.crop( (x1,y1,x2,y2) );
              data=np.array(face);
              l1=(l1[0]-x1, l1[1]-y1);
              l2=(l2[0]-x1, l2[1]-y1);
              l3=(l3[0]-x1, l3[1]-y1);
              l4=(l4[0]-x1, l4[1]-y1);
              l5=(l5[0]-x1, l5[1]-y1);
              embedding = FaceRecognition.embedding(self._processor, self._model, data, (l1,l2,l3,l4,l5));
              rt.append( ( (x1,y1,x2,y2), face, embedding) );
          return rt;
    
      #-------------------------------------------------------------------------
      # Constructor
      #-------------------------------------------------------------------------
      def __init__(self, **kwargs):
          super().__init__(**kwargs);
          self._encodings = None;
          """
          cwd = os.path.dirname(__file__);
          mwd = os.path.join(cwd, '../../models');
          fwd = os.path.join(cwd, '../../fonts');
          
          self._font = PIL.ImageFont.truetype(os.path.join(fwd, self.params.fontname or "Roboto-Bold.ttf"), self.params.fontsize or 14);
          
          self._facem = YOLO(os.path.join(mwd, "yolov8n-faces.pt"));          
          self._processor = AutoImageProcessor.from_pretrained("google/vit-base-patch16-224-in21k");
          self._model     = ViTModel.from_pretrained("google/vit-base-patch16-224-in21k")        
          """
          
          if self.params.reference is not None:

             if   isinstance(self.params.reference,str):
                  try:
                    fuente, istemp = FaceRecognition.download(self.params.reference);
                    imagen = PIL.Image.open(fuente);
                    if imagen.mode != 'RGB':
                       imagen = imagen.convert('RGB');
                    self._encodings = face_recognition.face_encodings(np.array(imagen)); #, num_jitters=self.params.jitters or 1, model=self.params.model or "small");
                  finally:
                    if istemp: os.remove(fuente);

             elif isinstance(self.params.reference,Image):
                  imagen = self.params.reference;
                  if imagen.mode != 'RGB':
                     imagen = imagen.convert('RGB');
                  self._encodings = face_recognition.face_encodings(np.array(imagen)); #, num_jitters=self.params.jitters or 1, model=self.params.model or "small");

             else:
                  raise "El parámetro 'reference' debe ser el path de una imagen o un objeto Image";
          
      #-------------------------------------------------------------------------
      # SLOTS
      #-------------------------------------------------------------------------
      @Block.slot("reference",{Image,str})
      def slot_reference(self, slot, data:(Image|str)):

          if data is None: return;

          assert isinstance(data,(Image,str));

          if   isinstance(data,str):
               try:
                 fuente, istemp = FaceRecognition.download(data);
                 imagen = PIL.Image.open(fuente);
                 if imagen.mode != 'RGB':
                    imagen = imagen.convert('RGB');
                 self._encodings = face_recognition.face_encodings(np.array(imagen)); #, num_jitters=self.params.jitters or 1, model=self.params.model or "small");
                 self.signal_reference(imagen);
               finally:
                 if istemp: os.remove(fuente);

          elif isinstance(data,Image):
               imagen = data;
               if imagen.mode != 'RGB':
                  imagen = imagen.convert('RGB');
               self._encodings = face_recognition.face_encodings(np.array(imagen)); #, num_jitters=self.params.jitters or 1, model=self.params.model or "small");
               self.signal_reference(imagen);

      #-------------------------------------------------------------------------
      @Block.slot("image",{Image,str})
      def slot_image(self, slot, data):

          if self._encodings is not None:

             if data is None: return;
             
             if isinstance(data,str):
                try:
                  fuente, istemp = FaceRecognition.download(data);
                  data = PIL.Image.open(fuente);
                finally:
                  if istemp: os.remove(fuente);
             
             imagen=data.copy();
             if imagen.mode != 'RGB':
                imagen = imagen.convert('RGB');

             face_encodings = face_recognition.face_encodings(np.array(imagen)); #, num_jitters=self.params.jitters or 1, model=self.params.model or "small");
             face_locations = face_recognition.face_locations(np.array(imagen)); #, number_of_times_to_upsample=self.params.upsample or 1, model="cnn" if Context().gpu else "hog");
             
             matches=0; 
             draw=PIL.ImageDraw.Draw(imagen);
             for s_enc in self._encodings:                 
                 for loc, t_enc in zip(face_locations, face_encodings):
                     results = face_recognition.compare_faces([s_enc], t_enc); #, tolerance=self.params.tolerance or 0.6);
                     if results[0] != True: continue;
                     y1,x2,y2,x1 = loc;
                     draw.rectangle([x1,y1,x2,y2], fill=None, outline=(255,0,0), width=5);
                     matches+=1;

             self.signal_recognized(bool(matches>0));
             self.signal_image(imagen);

      #-------------------------------------------------------------------------
      # SIGNALS
      #-------------------------------------------------------------------------
      @Block.signal("reference",Image)
      def signal_reference(self, data:Image):
          return data;

     #-------------------------------------------------------------------------
      @Block.signal("recognized",bool)
      def signal_recognized(self, data:bool):
          return data;

      #-------------------------------------------------------------------------
      @Block.signal("image",Image)
      def signal_image(self, data:Image):
          return data;
