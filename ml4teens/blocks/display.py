# -*- coding: utf-8 -*-

import os;

import IPython;

from IPython.display import update_display, display;

#import ipywidgets as widgets;

import PIL;
from PIL       import ImageDraw, ImageFont;
from PIL.Image import Image;

#from io import BytesIO;

from ..core import Block;

class Display(Block):

      #-------------------------------------------------------------------------
      # width
      # height
      # feed = False
      def __init__(self, *args, **kwargs):
          super().__init__(*args, **kwargs);
          self._handle=None;
          
          
      #-------------------------------------------------------------------------
      def _redim(self, imagen, width=None, height=None):

          if width is None and height is None: return imagen;
          
          (w, h) = imagen.width, imagen.height;
          
          if width is None:
             r = height / float(h);
             dimensiones = (int(w * r), height);
          else:
             r = width / float(w);
             dimensiones = (width, int(h * r));
             
          imagen = imagen.resize(dimensiones);
                
          return imagen;
          
      #-------------------------------------------------------------------------
      def _rotate(self, imagen, n):
      
          if n is None or type(n) not in (int, float):
             return imagen;
             
          else:
             return imagen.rotate(n);
             
      #-------------------------------------------------------------------------
      @classmethod
      def get_textsize(cls, text, font):
          # https://stackoverflow.com/a/46220683/9263761
          ascent, descent = font.getmetrics();
          text_width = font.getmask(text).getbbox()[2];
          text_height = font.getmask(text).getbbox()[3] + descent;
          return (text_width, text_height);

      #-------------------------------------------------------------------------
      @Block.slot("image", {Image})
      def slot_image(self, slot, data):

          if data:
             width =self.params.width;
             height=self.params.height;
             imagen=self._redim(data,width,height);
             imagen=self._rotate(imagen, self.params.rotate);
             
             title = None;
             if type(self.params.title) is str and len(self.params.title)>0:
                title  = self.params.title;
                bgcolor= self.params.bgcolor or "white";
                
                cwd = os.path.dirname(__file__);
                fwd = os.path.join(cwd, '../fonts');
                fuente = ImageFont.truetype(os.path.join(fwd, self.params.fontname or "Roboto-Bold.ttf"), self.params.fontsize or 12);
                ancho_texto, alto_texto = Display.get_textsize(title, fuente);
                espacio_texto=5+alto_texto+5;
                
                img = PIL.Image.new('RGB', (imagen.width, imagen.height + espacio_texto), bgcolor);
                img.paste(imagen, (0, espacio_texto));
                
                dibujo = ImageDraw.Draw(img);
                x_texto = (img.width - ancho_texto) / 2;
                y_texto = (espacio_texto - alto_texto) / 2;
                dibujo.text((x_texto, y_texto), title, fill="black", font=fuente);
                imagen=img;
                
             caption = None;
             if type(self.params.caption) is str and len(self.params.caption)>0:
                caption = self.params.caption;
                bgcolor= self.params.bgcolor or "white";
                
                cwd = os.path.dirname(__file__);
                fwd = os.path.join(cwd, '../fonts');
                fuente = ImageFont.truetype(os.path.join(fwd, self.params.fontname or "Roboto-Bold.ttf"), self.params.fontsize or 12);
                ancho_texto, alto_texto = Display.get_textsize(caption, fuente);
                espacio_texto=5+alto_texto+5;
                
                img = PIL.Image.new('RGB', (imagen.width, imagen.height + espacio_texto), bgcolor);
                img.paste(imagen, (0, 0));
                
                dibujo = ImageDraw.Draw(img);
                x_texto = (img.width - ancho_texto) / 2;
                y_texto = imagen.height + (espacio_texto - alto_texto) / 2;
                dibujo.text((x_texto, y_texto), caption, fill="black", font=fuente);
                imagen=img;
             
             if self.params.border:
                n=self.params.borderSize  or self.params.border_size  or 2;
                c=self.params.borderColor or self.params.border_color or "black";
                n=min(2,n);
                draw = ImageDraw.Draw(imagen);
                draw.line([(0, n//2-1),            (img.width, n//2-1)],            fill=c, width=n);
                draw.line([(0, img.height-n//2-1), (img.width, img.height-n//2-1)], fill=c, width=n);
                draw.line([(n//2-1, 0),            (n//2-1, img.height)],           fill=c, width=n);
                draw.line([(img.width-n//2-1, 0),  (img.width-n//2-1, img.height)], fill=c, width=n);
             
             if not self.params.feed:
                if self._handle is None:
                   self._handle=display(imagen, display_id=self._id);
                else:
                   self._handle.update(imagen);
             else:
                display(imagen);
                   
          self.signal_image(data);
          
          return True;
          
      #-------------------------------------------------------------------------
      @Block.signal("image", Image)
      def signal_image(self, data):
          return data;

