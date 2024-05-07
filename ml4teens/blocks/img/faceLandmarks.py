# -*- coding: utf-8 -*-

import os;
import numpy as np;
import PIL;

from PIL.Image import Image;

import matplotlib.pyplot as plt;
from io import BytesIO;

from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2

import mediapipe as mp

from ...core import Block;

#===============================================================================
class FaceLandmarks(Block):

      #-------------------------------------------------------------------------
      def __init__(self, **kwargs):
          super().__init__(**kwargs);

          # /home/fran/CODE/ML4Teens/package/notebooks/models/face_landmarker.task

          cwd = os.path.dirname(__file__);
          mwd = os.path.join(cwd, '../../models');
          fwd = os.path.join(cwd, '../../fonts');
          
          from mediapipe.tasks        import python;
          from mediapipe.tasks.python import vision;

          VisionRunningMode = vision.RunningMode;

          self.running_mode = VisionRunningMode.IMAGE;
          self.running_mode = VisionRunningMode.IMAGE if self.params.image else self.running_mode;
          self.running_mode = VisionRunningMode.VIDEO if (self.params.frame or self.params.video) else self.running_mode;

          options={ "num_faces": self.params.faces or 1,
                    "running_mode": self.running_mode,
                    "output_face_blendshapes":True,
                    "output_facial_transformation_matrixes":True,
                  };

          base_options = python.BaseOptions(model_asset_path=os.path.join(mwd,'face_landmarker.task'));
          self._model  = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(base_options=base_options,**options));
          self._ms=0;

      #-------------------------------------------------------------------------
      @classmethod
      def names(cls, idx=None):
          
          if idx is None: return 52;
          
          if idx== 0: return "_neutral";
          if idx== 1: return "browDownLeft";
          if idx== 2: return "browDownRight";
          if idx== 3: return "browInnerUp";
          if idx== 4: return "browOuterUpLeft";
          if idx== 5: return "browOuterUpRight";
          if idx== 6: return "cheekPuff";
          if idx== 7: return "cheekSquintLeft";
          if idx== 8: return "cheekSquintRight";
          if idx== 9: return "eyeBlinkLeft";
          if idx==10: return "eyeBlinkRight";
          if idx==11: return "eyeLookDownLeft";
          if idx==12: return "eyeLookDownRight";
          if idx==13: return "eyeLookInLeft";
          if idx==14: return "eyeLookInRight";
          if idx==15: return "eyeLookOutLeft";
          if idx==16: return "eyeLookOutRight";
          if idx==17: return "eyeLookUpLeft";
          if idx==18: return "eyeLookUpRight";
          if idx==19: return "eyeSquintLeft";
          if idx==20: return "eyeSquintRight";
          if idx==21: return "eyeWideLeft";
          if idx==22: return "eyeWideRight";
          if idx==23: return "jawForward";
          if idx==24: return "jawLeft";
          if idx==25: return "jawOpen";
          if idx==26: return "jawRight";
          if idx==27: return "mouthClose";
          if idx==28: return "mouthDimpleLeft";
          if idx==29: return "mouthDimpleRight";
          if idx==30: return "mouthFrownLeft";
          if idx==31: return "mouthFrownRight";
          if idx==32: return "mouthFunnel";
          if idx==33: return "mouthLeft";
          if idx==34: return "mouthLowerDownLeft";
          if idx==35: return "mouthLowerDownRight";
          if idx==36: return "mouthPressLeft";
          if idx==37: return "mouthPressRight";
          if idx==38: return "mouthPucker";
          if idx==39: return "mouthRight";
          if idx==40: return "mouthRollLower";
          if idx==41: return "mouthRollUpper";
          if idx==42: return "mouthShrugLower";
          if idx==43: return "mouthShrugUpper";
          if idx==44: return "mouthSmileLeft";
          if idx==45: return "mouthSmileRight";
          if idx==46: return "mouthStretchLeft";
          if idx==47: return "mouthStretchRight";
          if idx==48: return "mouthUpperUpLeft";
          if idx==49: return "mouthUpperUpRight";
          if idx==50: return "noseSneerLeft";
          if idx==51: return "noseSneerRight";
          raise KeyError(f"El índice {idx} no se corresponde con ningún face::landmark.");
          
      """
      traducciones = {
      "_neutral": "neutral",
      "browDownLeft": "ceño fruncido izquierdo",
      "browDownRight": "ceño fruncido derecho",
      "browInnerUp": "ceño elevado interior",
      "browOuterUpLeft": "ceño elevado exterior izquierdo",
      "browOuterUpRight": "ceño elevado exterior derecho",
      "cheekPuff": "inflar mejillas",
      "cheekSquintLeft": "entrecerrar mejilla izquierda",
      "cheekSquintRight": "entrecerrar mejilla derecha",
      "eyeBlinkLeft": "parpadeo izquierdo",
      "eyeBlinkRight": "parpadeo derecho",
      "eyeLookDownLeft": "mirada abajo izquierda",
      "eyeLookDownRight": "mirada abajo derecha",
      "eyeLookInLeft": "mirada hacia dentro izquierda",
      "eyeLookInRight": "mirada hacia dentro derecha",
      "eyeLookOutLeft": "mirada hacia fuera izquierda",
      "eyeLookOutRight": "mirada hacia fuera derecha",
      "eyeLookUpLeft": "mirada arriba izquierda",
      "eyeLookUpRight": "mirada arriba derecha",
      "eyeSquintLeft": "ojo entrecerrado izquierdo",
      "eyeSquintRight": "ojo entrecerrado derecho",
      "eyeWideLeft": "ojo muy abierto izquierdo",
      "eyeWideRight": "ojo muy abierto derecho",
      "jawForward": "mandíbula hacia adelante",
      "jawLeft": "mandíbula izquierda",
      "jawOpen": "mandíbula abierta",
      "jawRight": "mandíbula derecha",
      "mouthClose": "boca cerrada",
      "mouthDimpleLeft": "hoyuelo izquierdo",
      "mouthDimpleRight": "hoyuelo derecho",
      "mouthFrownLeft": "ceño boca izquierda",
      "mouthFrownRight": "ceño boca derecha",
      "mouthFunnel": "boca embudo",
      "mouthLeft": "boca izquierda",
      "mouthLowerDownLeft": "boca abajo izquierda",
      "mouthLowerDownRight": "boca abajo derecha",
      "mouthPressLeft": "presión boca izquierda",
      "mouthPressRight": "presión boca derecha",
      "mouthPucker": "boca fruncida",
      "mouthRight": "boca derecha",
      "mouthRollLower": "enrollar inferior de boca",
      "mouthRollUpper": "enrollar superior de boca",
      "mouthShrugLower": "encoger inferior de boca",
      "mouthShrugUpper": "encoger superior de boca",
      "mouthSmileLeft": "sonrisa izquierda",
      "mouthSmileRight": "sonrisa derecha",
      "mouthStretchLeft": "estiramiento boca izquierda",
      "mouthStretchRight": "estiramiento boca derecha",
      "mouthUpperUpLeft": "parte superior boca arriba izquierda",
      "mouthUpperUpRight": "parte superior boca arriba derecha",
      "noseSneerLeft": "arrugar nariz izquierda",
      "noseSneerRight": "arrugar nariz derecha"
      }
      """
      
      #-------------------------------------------------------------------------
      @classmethod
      def draw_landmarks_on_image(cls, rgb_image, detection_result, params):
          face_landmarks_list = detection_result.face_landmarks
          annotated_image = np.copy(rgb_image)
        
          # Loop through the detected faces to visualize.
          for idx in range(len(face_landmarks_list)):
            face_landmarks = face_landmarks_list[idx]
        
            # Draw the face landmarks.
            face_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
            face_landmarks_proto.landmark.extend([ landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in face_landmarks ])
        
            if bool(params.drawAll) is True or bool(params.tesselation) is True:
               solutions.drawing_utils.draw_landmarks(image=annotated_image, 
                                                      landmark_list=face_landmarks_proto, 
                                                      connections=mp.solutions.face_mesh.FACEMESH_TESSELATION, 
                                                      landmark_drawing_spec=None, 
                                                      connection_drawing_spec=mp.solutions.drawing_styles.get_default_face_mesh_tesselation_style())
            if bool(params.drawAll) is True or bool(params.contours) is True:
               solutions.drawing_utils.draw_landmarks(image=annotated_image, 
                                                      landmark_list=face_landmarks_proto, 
                                                      connections=mp.solutions.face_mesh.FACEMESH_CONTOURS,    
                                                      landmark_drawing_spec=None, 
                                                      connection_drawing_spec=mp.solutions.drawing_styles.get_default_face_mesh_contours_style())               
            if bool(params.drawAll) is True or bool(params.irises) is True:
               solutions.drawing_utils.draw_landmarks(image=annotated_image, 
                                                      landmark_list=face_landmarks_proto, 
                                                      connections=mp.solutions.face_mesh.FACEMESH_IRISES,      
                                                      landmark_drawing_spec=None, 
                                                      connection_drawing_spec=mp.solutions.drawing_styles.get_default_face_mesh_iris_connections_style())
        
          return annotated_image    
          
      #-------------------------------------------------------------------------
      @classmethod
      def plot_features(cls, features):
        names  = [item["name" ] for item in features];
        scores = [item["score"] for item in features];
        
        ranks = range(len(names));

        with BytesIO() as buff:
             fig, ax = plt.subplots(figsize=(10, 10));
             bar = ax.barh(ranks, scores, label=[str(x) for x in ranks]);
             ax.set_yticks(ranks, names);
             ax.invert_yaxis();

             for score, patch in zip(scores, bar.patches):
                 plt.text(patch.get_x() + patch.get_width(), patch.get_y(), f"{score:.2f}", va="top");

             ax.set_xlabel('Score');
             ax.set_title("Features");
             plt.tight_layout();

             plt.savefig(buff, format='png');
             buff.seek(0);
             image = PIL.Image.open(buff)
             image.load();

             buff.close();
             plt.close();

        return image;
          
      #-------------------------------------------------------------------------
      # SLOTS
      #-------------------------------------------------------------------------
      @Block.slot("image", {Image})
      def slot_image(self, slot, data):

          from mediapipe.tasks        import python;
          from mediapipe.tasks.python import vision;

          VisionRunningMode = vision.RunningMode;
          
          if data:
             ms=self.params.ms or 33;
             image = data.convert('RGB');  
             image = mp.Image(image_format=mp.ImageFormat.SRGB, data=np.asarray(image));
             if self.running_mode==VisionRunningMode.IMAGE: results = self._model.detect(image);
             if self.running_mode==VisionRunningMode.VIDEO: results = self._model.detect_for_video(image,self._ms);
             self._ms+=ms;
                    
             #image = data.convert('RGB');  
             #image = mp.Image(image_format=mp.ImageFormat.SRGB, data=np.asarray(image));
             #results = self._model.detect(image);

             if self.signal_image():
                image = image.numpy_view();
                if bool(self.params.bb) is True:
                   image = np.zeros_like(image);
                if self.params.alpha is not None:
                   alpha=self.params.alpha;
                   alpha=max(alpha,0.0);
                   alpha=min(alpha,1.0);
                   color_fondo = np.array([0, 0, 0]);
                   color_fondo = np.tile(color_fondo, (image.shape[0], image.shape[1], 1));
                   image = image.astype(float) * alpha + color_fondo.astype(float) * (1 - alpha);
                   image = np.clip(image, 0, 255).astype(np.uint8);
                   
                salida = FaceLandmarks.draw_landmarks_on_image(image, results, self.params);
                self.signal_image(PIL.Image.fromarray(salida));

             if self.signal_landmarks():
                rt=[];
                for idx in range(len(results.face_landmarks)):
                    landmarks   = results.face_landmarks[idx];
                    blendshapes = results.face_blendshapes[idx];
                    matrix      = results.facial_transformation_matrixes[idx];
                    face={"kind":f"face::{0}", "trust":0.0, "matrix":matrix, "xyz":[]};
                    for lm in landmarks:
                        face["xyz"].append((lm.x, lm.y, lm.z));
                    rt.append(face);
                    
                self.signal_landmarks(rt);

             if self.signal_features():
                rt=[];
                for idx in range(len(results.face_landmarks)):
                    blendshapes = results.face_blendshapes[idx];
                    face = [ {"index":bs.index, "score":bs.score, "name":bs.category_name} for bs in blendshapes ];
                    rt.append(face);
                    
                self.signal_features(rt);
                
             if self.signal_plot():
                if len(results.face_landmarks) > 0:
                   for idx in range(len(results.face_landmarks)):
                       blendshapes = results.face_blendshapes[idx];
                       face = [ {"index":bs.index, "score":bs.score, "name":bs.category_name} for bs in blendshapes ];
                       image = FaceLandmarks.plot_features(face);
                       self.signal_plot(image);
                else:
                   if self.params.emptyPlot:
                      face=[{"index":n, "score":0.0, "name":FaceLandmarks.names(n)} for n in range(52)];
                      image = FaceLandmarks.plot_features(face);
                      self.signal_plot(image);
                
     #-------------------------------------------------------------------------
      # SIGNALS
      #-------------------------------------------------------------------------
      @Block.signal("image", Image)
      def signal_image(self, data):
          return data;

      @Block.signal("plot", Image)
      def signal_plot(self, data):
          return data;

      #-------------------------------------------------------------------------
      @Block.signal("landmarks", list)
      def signal_landmarks(self, data):
          return data;

      #-------------------------------------------------------------------------
      @Block.signal("features", list)
      def signal_features(self, data):
          return data;
