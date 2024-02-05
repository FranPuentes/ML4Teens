import os, numpy as np;
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
class HandGestures(Block):

      #-------------------------------------------------------------------------
      def __init__(self, **kwargs):
          super().__init__(**kwargs);

          cwd = os.path.dirname(__file__);
          mwd = os.path.join(cwd, '../../models');
          fwd = os.path.join(cwd, '../../fonts');

          base_options = python.BaseOptions(model_asset_path=os.path.join(mwd,'gesture_recognizer.task'));
          options = vision.GestureRecognizerOptions(base_options=base_options, num_hands=2);
          self._model = vision.GestureRecognizer.create_from_options(options);
          self._queue = [];

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
          
          self._queue = [];
          
          if data:
             image = data.convert('RGB');  
             image = mp.Image(image_format=mp.ImageFormat.SRGB, data=np.asarray(image));
             results = self._model.recognize(image);
             
             topg = results.gestures[0][0];
             self.signal_gesture( (topg.score, topg.category_name) );
             
             if self.signal_landmarks():
                rt=[];
                
                for idx in range(len(results.hand_landmarks)):
                    hand_landmarks = results.hand_landmarks[idx];
                    handedness = results.handedness[idx];
                     
                    hand={"kind":f"hand::{handedness[0].category_name}", "trust":handedness[0].score, "xy":[], "z":[], "visibility":[], "presence":[], "names":[] };
                     
                    for l, lm in enumerate(hand_landmarks):
                        hand["xy"        ].append((lm.x, lm.y));
                        hand["z"         ].append(lm.z);
                        hand["visibility"].append(lm.visibility);
                        hand["presence"  ].append(lm.presence);
                        hand["names"     ].append(self.names(l));
                        
                    rt.append(hand);
                    
                self._queue += rt;
                self.signal_landmarks(rt);
             
             if self.signal_landmark():
                try:
                  landmark=self._queue.pop(0);
                  self.signal_landmark(landmark);
                  
                except IndexError:
                  self.signal_end(True);
                
             if self.signal_image():
                salida = HandGestures.draw_landmarks_on_image(image.numpy_view(), results);
                self.signal_image(PIL.Image.fromarray(salida));

      #-------------------------------------------------------------------------
      @Block.slot("next", {object})
      def slot_next(self, slot, data):
          try:
            landmark=self._queue.pop(0);
            self.signal_landmark(landmark);
          except IndexError:
            self.signal_end(True);

      #-------------------------------------------------------------------------
      # SIGNALS
      #-------------------------------------------------------------------------
      @Block.signal("image", Image)
      def signal_image(self, data):
          return data;

      #-------------------------------------------------------------------------
      @Block.signal("gesture", tuple)
      def signal_gesture(self, data):
          return data;

      #-------------------------------------------------------------------------
      @Block.signal("landmark", list)
      def signal_landmark(self, data):
          return data;

      #-------------------------------------------------------------------------
      @Block.signal("landmarks", list)
      def signal_landmarks(self, data):
          return data;

      #-------------------------------------------------------------------------
      @Block.signal("end", list)
      def signal_end(self, data):
          return data;
