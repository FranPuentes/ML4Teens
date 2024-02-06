import os;
import requests;
import numpy as np;
import PIL;
import cv2;

from transformers import AutoImageProcessor, ViTModel;
import torch;

from ultralytics import YOLO;

from tempfile import NamedTemporaryFile;

from PIL.Image import Image;

#from IPython.display import display as IDisplay;

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
      def similarity(emb1, emb2):
          assert isinstance(emb1, torch.Tensor);
          assert isinstance(emb2, torch.Tensor);
          emb1 = emb1.numpy().flatten();
          emb2 = emb2.numpy().flatten();
          norm1 = emb1 / np.linalg.norm(emb1);
          norm2 = emb2 / np.linalg.norm(emb2);
          return np.dot(norm1, norm2);

      #-------------------------------------------------------------------------
      @staticmethod
      def normalize(image, landmarks):
          # Definir las coordenadas objetivo para los landmarks en la imagen normalizada
          desired_eye_x = 0.25; # Porcentaje del ancho de la imagen para los ojos
          desired_eye_y = 0.4   # Porcentaje del alto de la imagen para los ojos

          desired_nose_x = 0.5  # Mitad de la imagen para la nariz
          desired_nose_y = 0.6  # Porcentaje del alto de la imagen para la nariz

          desired_mouth_x = 0.5  # Mitad de la imagen para la boca
          desired_mouth_y = 0.85; # Porcentaje del alto de la imagen para la boca
            
          img_h, img_w = image.shape[:2]
          desired_width, desired_height = img_w, img_h
            
          # Coordenadas objetivo basadas en las dimensiones deseadas
          desired_left_eye = (int(desired_width * desired_eye_x), int(desired_height * desired_eye_y))
          desired_right_eye = (int(desired_width * (1 - desired_eye_x)), int(desired_height * desired_eye_y))
          desired_nose = (int(desired_width * desired_nose_x), int(desired_height * desired_nose_y))
          desired_left_mouth = (int(desired_width * (desired_mouth_x - 0.1)), int(desired_height * desired_mouth_y))
          desired_right_mouth = (int(desired_width * (desired_mouth_x + 0.1)), int(desired_height * desired_mouth_y))
            
          # Calcular la matriz de transformación para alinear los landmarks a las coordenadas objetivo
          src_pts = np.float32([landmarks[0], landmarks[1], landmarks[2], landmarks[3], landmarks[4]])
          dst_pts = np.float32([desired_left_eye, desired_right_eye, desired_nose, desired_left_mouth, desired_right_mouth])
           
          # Calcular la matriz de transformación usando todos los 5 puntos para obtener más precisión
          transform_matrix, _ = cv2.findHomography(src_pts, dst_pts)
            
          # Aplicar la transformación para normalizar la subimagen
          normalized_image = cv2.warpPerspective(image, transform_matrix, (desired_width, desired_height))

          resized_image = cv2.resize(normalized_image, (128,128), interpolation=cv2.INTER_AREA);
          return resized_image;
          
      #-------------------------------------------------------------------------
      @staticmethod
      def embedding(processor, model, data, lm):
          data=FaceRecognition.normalize(data, lm);
          #IDisplay(PIL.Image.fromarray(data));
          inputs = processor(data, return_tensors="pt");
          with torch.no_grad():
               outputs = model(**inputs);
               return outputs.last_hidden_state[0];
              
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

          cwd = os.path.dirname(__file__);
          mwd = os.path.join(cwd, '../../models');
          fwd = os.path.join(cwd, '../../fonts');
          
          self._font = PIL.ImageFont.truetype(os.path.join(fwd, self.params.fontname or "Roboto-Bold.ttf"), self.params.fontsize or 14);
          
          self._facem = YOLO(os.path.join(mwd, "yolov8n-faces.pt"));          
          self._processor = AutoImageProcessor.from_pretrained("google/vit-base-patch16-224-in21k");
          self._model     = ViTModel.from_pretrained("google/vit-base-patch16-224-in21k");
        
          self._encodings = None;

          if self.params.reference is not None:

             if   isinstance(self.params.reference,str):
                  try:
                    fuente, istemp = FaceRecognition.download(self.params.reference);
                    imagen = PIL.Image.open(fuente);
                    self._encodings = self.encodings(imagen);
                  finally:
                    if istemp: os.remove(fuente);

             elif isinstance(self.params.reference,Image):
                  imagen = self.params.reference;
                  self._encodings = self.encodings(imagen);

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
                 self._encodings = self.encodings(imagen);
                 if self.signal_reference():
                    self.signal_reference(imagen);
               finally:
                 if istemp: os.remove(fuente);

          elif isinstance(data,Image):
               imagen = self.params.reference; #.convert("RGB");
               self._encodings = self.encodings(imagen);
               if self.signal_reference():
                  self.signal_reference(imagen);

      #-------------------------------------------------------------------------
      @Block.slot("image",{Image,str})
      def slot_image(self, slot, data):

          def softmax(x):
              e_x = np.exp(x - np.max(x));
              return e_x / e_x.sum(axis=0);
              #import torch.nn.functional as F
              #scores = torch.tensor(x)
              #softmax_scores = F.softmax(scores, dim=0)
              #return softmax_scores.numpy();


          if self._encodings is not None:

             if isinstance(data,str):
                try:
                  fuente, istemp = FaceRecognition.download(data);
                  data = PIL.Image.open(fuente);
                finally:
                  if istemp: os.remove(fuente);

             else:
                data = data or self.params.reference;

             if data is None: return;

             imagen = data.copy();

             matches=[]; 
             draw=PIL.ImageDraw.Draw(imagen);
             face_encodings = self.encodings(imagen);
             
             for s_enc in self._encodings:
                  
                 encx=[];
                 encs=[];
                 for t_enc in face_encodings:
                     simm=FaceRecognition.similarity(s_enc[2], t_enc[2]);
                     if simm < 0.45: continue;
                     encs.append( [simm, t_enc] );
                     encx.append(  simm         );
                     
                 if encs:    
                    smax=softmax(encx);
                    for i, enc in enumerate(encs):
                        enc[0]=smax[i];                 
                    best=max(encs, key=lambda e: e[0]);
    
                    x1,y1,x2,y2 = best[1][0];
                    conf        = best[0];
                    draw.rectangle([x1,y1,x2,y2], fill=None, outline=(255,0,0), width=5);
                    texto=f"{round(100*float(conf),1)}%";
                    alto_texto = (self.params.fontsize or 14);
                    draw.text((x1+5+2, y1+5), texto, fill=self.params.fontcolor or "yellow", font=self._font);
                    matches.append(True);
                 else:    
                    matches.append(False);

             self.signal_recognized(any(matches));             
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
