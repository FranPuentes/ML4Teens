import os, math, numpy as np;
import PIL;

import cv2;

from PIL.Image import Image;

from mediapipe import solutions;
from mediapipe.framework.formats import landmark_pb2;

import mediapipe as mp;
from mediapipe.tasks import python;
from mediapipe.tasks.python import vision;

from ...core import Block;

#===============================================================================
class HandFeatures(Block):

      #-------------------------------------------------------------------------
      def __init__(self, **kwargs):
          super().__init__(**kwargs);

          cwd = os.path.dirname(__file__);
          mwd = os.path.join(cwd, '../../models');
          fwd = os.path.join(cwd, '../../fonts');
          
          base_options = python.BaseOptions(model_asset_path=os.path.join(mwd,'hand_landmarker.task'));
          options = vision.HandLandmarkerOptions(base_options=base_options, num_hands=2);
          self._model = vision.HandLandmarker.create_from_options(options);

      #-------------------------------------------------------------------------
      def draw_landmarks_on_image(rgb_image, results):

          MARGIN = 10;  # pixels
          FONT_SIZE = 1;
          FONT_THICKNESS = 1;
          HANDEDNESS_TEXT_COLOR = (88, 205, 54); # vibrant green

          hand_landmarks_list = results.hand_landmarks;
          handedness_list = results.handedness;
          annotated_image = np.copy(rgb_image);

          # Loop through the detected hands to visualize.
          for idx in range(len(hand_landmarks_list)):
              hand_landmarks = hand_landmarks_list[idx];
              handedness = handedness_list[idx];
    
              # Draw the hand landmarks.
              hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList();
              hand_landmarks_proto.landmark.extend([ landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in hand_landmarks ]);
              solutions.drawing_utils.draw_landmarks( annotated_image, hand_landmarks_proto, solutions.hands.HAND_CONNECTIONS, solutions.drawing_styles.get_default_hand_landmarks_style(), solutions.drawing_styles.get_default_hand_connections_style());
    
              # Get the top left corner of the detected hand's bounding box.
              height, width, _ = annotated_image.shape;
              x_coordinates = [landmark.x for landmark in hand_landmarks];
              y_coordinates = [landmark.y for landmark in hand_landmarks];
              text_x = int(min(x_coordinates) * width);
              text_y = int(min(y_coordinates) * height) - MARGIN;
    
              # Draw handedness (left or right hand) on the image.
              cv2.putText(annotated_image, f"{handedness[0].category_name}", (text_x, text_y), cv2.FONT_HERSHEY_DUPLEX, FONT_SIZE, HANDEDNESS_TEXT_COLOR, FONT_THICKNESS, cv2.LINE_AA);

          return annotated_image
          
      @classmethod    
      def normalize_names(cls, *args):
          rt="";
          for arg in args:
              rt += "".join([s.capitalize() for s in arg.split()]);
          return rt;    
      
      @classmethod    
      def names(cls, idx):
          if idx== 0: return "wrist";
          if idx== 1: return "thumb cmc";
          if idx== 2: return "thumb mcp";
          if idx== 3: return "thumb pip";
          if idx== 4: return "thumb tip";
          if idx== 5: return "index finger mcp";
          if idx== 6: return "index finger pip";
          if idx== 7: return "index finger dip";
          if idx== 8: return "index finger tip";
          if idx== 9: return "middle finger mcp";
          if idx==10: return "middle finger pip";
          if idx==11: return "middle finger dip";
          if idx==12: return "middle finger tip";
          if idx==13: return "ring finger mcp";
          if idx==14: return "ring finger pip";
          if idx==15: return "ring finger dip";
          if idx==16: return "ring finger tip";
          if idx==17: return "pinky mcp";
          if idx==18: return "pinky pip";
          if idx==19: return "pinky dip";
          if idx==20: return "pinky tip";
          raise KeyError(f"No existe el índice {idx} en la lista de HandLandmarks");

      #-------------------------------------------------------------------------
      # SLOTS
      #-------------------------------------------------------------------------
      @Block.slot("image", {Image})
      def slot_image(self, slot, data):
          
          if data:
             image = data.convert('RGB');  
             image = mp.Image(image_format=mp.ImageFormat.SRGB, data=np.asarray(image));
             results = self._model.detect(image);
              
             rt=[]; 
             for idx in range(len(results.hand_landmarks)):
                 landmarks = results.hand_landmarks[idx];
                 prefix    = results.handedness[idx][0].category_name;
                 
                 wrist = None;
                 for idx, lm in enumerate(landmarks):
                     name=HandFeatures.normalize_names(prefix,self.names(idx));
                     if wrist is None:
                        wrist=[lm.x, lm.y, lm.z];
                        rt.append({"index":idx, "score":0.0, "name":name});
                     else:
                        score= math.sqrt((wrist[0]-lm.x)**2 + (wrist[1]-lm.y)**2 + (wrist[2]-lm.z)**2);
                        rt.append({"index":idx, "score":score, "name":name});
                    
             self.signal_features(rt);
              
             if self.signal_image():
                salida = HandFeatures.draw_landmarks_on_image(image.numpy_view(), results)
                self.signal_image(PIL.Image.fromarray(salida));

      #-------------------------------------------------------------------------
      # SIGNALS
      #-------------------------------------------------------------------------
      @Block.signal("image", Image)
      def signal_image(self, data):
          return data;

      #-------------------------------------------------------------------------
      @Block.signal("features", list)
      def signal_features(self, data):
          return data;

