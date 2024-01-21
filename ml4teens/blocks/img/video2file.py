import sys, os, copy;
import time;
import cv2 as cv;
import numpy as np;
import PIL;
import requests;

from PIL.Image import Image;

from tempfile import NamedTemporaryFile;

from ...core import Block;

class Video2File(Block):

      #-------------------------------------------------------------------------
      # filename:str
      # fps:int
      def __init__(self, **kwargs):
          super().__init__(**kwargs);          
          self._source = None;
          self._target = self.params.target or "./video2file.avi";
          self._fd     = None;
          self._frames = 0;
          self._encoder= "XVID";
          self._fps    = self.params.fps or 33;
          self._delay  = (1000*1/self.params.fps) if self.params.fps is not None else self._fps;
                               
      #-------------------------------------------------------------------------
      # SLOTS
      #-------------------------------------------------------------------------
      @Block.slot("info", {dict})
      def slot_info(self, slot, data):
          self._source  = data.get("source",  self._source );
          self._frames  = data.get("frames",  self._frames );
          self._encoder = data.get("encoder", self._encoder);
          self._delay   = data.get("delay",   self._delay  );
          self._fps     = data.get("fps",     self._fps    );
          
          fourcc = self._encoder;
          fourcc = f"{fourcc & 0xff:c}{(fourcc >> 8) & 0xff:c}{(fourcc >> 16) & 0xff:c}{(fourcc >> 24) & 0xff:c}"
          self._encoder = fourcc;

      @Block.slot("target", {str})
      def slot_target(self, slot, data):
          pass;
            
      @Block.slot("begin", {int})
      def slot_begin(self, slot, data):
          assert self._frames is None or data == self._frames, f"No se corresponden frames (info) con frames (begin)";
          assert self._target is not None;
          self._frames=data;
          # abrir el fichero          
            
      #-------------------------------------------------------------------------
      @Block.slot("frame", {Image})
      def slot_frame(self, slot, data):
          # escribir en el fichero
          pass;
                    
      @Block.slot("end", {bool})
      def slot_end(self, slot, data):
          # cerrar el fichero
          pass;
            
      #-------------------------------------------------------------------------
      # SIGNALS
      #-------------------------------------------------------------------------
      @Block.signal("filename", str)
      def signal_filename(self, data:str):
          return data;

