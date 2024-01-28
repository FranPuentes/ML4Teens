import os;
import requests;
import numpy as np;
import PIL;

from tempfile import NamedTemporaryFile;

from PIL.Image import Image;

# https://github.com/ageitgey/face_recognition

import face_recognition as fr;

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
      # Constructor
      #-------------------------------------------------------------------------
      def __init__(self, **kwargs):
          super().__init__(**kwargs);

          self._encodings = None;

          if self.params.reference is not None:

             if   isinstance(self.params.reference,str):
                  try:
                    fuente, istemp = FaceRecognition.download(self.params.reference);
                    image = fr.load_image_file(fuente);
                    self._encodings = fr.face_encodings(image);
                  finally:
                    if istemp: os.remove(fuente);

             elif isinstance(self.params.reference,Image):
                  data_array=np.array(self.params.reference.convert("RGB"));
                  self._encodings = fr.face_encodings(data_array);

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
                 image = fr.load_image_file(fuente);
                 self._encodings = fr.face_encodings(image);
                 if self.signal_reference():
                    image=PIL.Image.fromarray(np.uint8(image));
                    self.signal_reference(image);
               finally:
                 if istemp: os.remove(fuente);

          elif isinstance(data,Image):
               data_array=np.array(data.convert("RGB"));
               self._encodings = fr.face_encodings(data_array);
               if self.signal_reference():
                  image=PIL.Image.fromarray(data_array);
                  self.signal_reference(image);

      #-------------------------------------------------------------------------
      @Block.slot("image",{Image,str})
      def slot_image(self, slot, data):

          if data is None: return;

          if self._encodings is not None:

             assert isinstance(data,(Image,str));

             if isinstance(data,str):
                try:
                  fuente, istemp = FaceRecognition.download(data);
                  data_array=fr.load_image_file(fuente, mode="RGB");
                  data=PIL.Image.fromarray(data_array);
                finally:
                  if istemp: os.remove(fuente);

             else:
                data_array=np.array(data.convert("RGB"));
                data=PIL.Image.fromarray(data_array);

             face_locations = fr.face_locations(data_array);
             face_encodings = fr.face_encodings(data_array, face_locations);
             matches=[];
             draw=PIL.ImageDraw.Draw(data);
             for idx, face_encoding in enumerate(face_encodings):
                 _match = fr.compare_faces(self._encodings, face_encoding);
                 y1,x2,y2,x1 = face_locations[idx];
                 if any(_match): # _match es un array de True/False
                    draw.rectangle([x1,y1,x2,y2], fill=None, outline=(255,0,0), width=5);
                 else:
                    draw.rectangle([x1,y1,x2,y2], fill=None, outline=(128,128,128), width=2);
                 matches += _match;
             self.signal_recognized(any(matches)); # True/False

          self.signal_image(data);

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

