from PIL.Image import Image;
from PIL       import ImageOps, ImageChops, ImageMath, ImageFilter;

from ...core import Block;

class ImageOp(Block):

      #-------------------------------------------------------------------------
      # op:str 
      # autoredim: uno de {left,right,min,avg,max}
      # expression:str
      # kwargs:dict
      def __init__(self, **kwargs):
          super().__init__(**kwargs);

          self._op         = self.params.op;
          self._autoredim  = self.params.autoredim or "average";
          self._expression = self.params.expression;
          self._left       = None;
          self._right      = None;
          self._last       = None;
          self._kwargs     = kwargs;
          
          if self._op is None: raise RuntimeError("Los objetos de la clase ImageOp necesitan el parámetro 'op' con la operación a realizar");
          
          def delparam(key):
              if key in self._kwargs: del self._kwargs[key];

          delparam("op");
          delparam("autoredim");
          delparam("expression");          

          self._op = (" ".join([t.strip() for t in self._op.split()])).lower();

      #-------------------------------------------------------------------------
      def _redim(self, l,r):
          if l.size != r.size:
          
             if self._autoredim==None or self._autoredim.lower() in ["l","left"]:
                l = l.resize(r.size);
                return (l,r);
                
             if self._autoredim.lower() in ["r","right"]:
                r = r.resize(l.size);
                return (l,r);
                
             if self._autoredim.lower() in ["mn","min"]:
                width =min(l.width,  r.width );
                height=min(l.height, r.height);
                l=l.resize( (width, height) );
                r=r.resize( (width, height) );
                return (l,r);
                
             if self._autoredim.lower() in ["mx","max"]:
                width =max(l.width,  r.width );
                height=max(l.height, r.height);
                l=l.resize( (width, height) );
                r=r.resize( (width, height) );
                return (l,r);
                
             if self._autoredim.lower() in ["a","avg","average"]:
                width =(l.width +r.width )//2;
                height=(l.height+r.height)//2;
                l=l.resize( (width, height) );
                r=r.resize( (width, height) );
                return (l,r);
                
          return (l,r);

      #-------------------------------------------------------------------------
      def _op2(self, left, right, op, params):
          
          left, right = self._redim(left, right);
          
          imagen=None;          

          if   op in ["diff"]:
               imagen = ImageChops.difference(left, right);

          elif op in ["and","&&"]:
               left =left. convert("1");
               right=right.convert("1");
               imagen = ImageChops.logical_and(left, right);

          elif op in ["or","||"]:
               left =left. convert("1");
               right=right.convert("1");
               imagen = ImageChops.logical_or(left, right);

          elif op in ["xor","^^","^"]:
               left =left. convert("1");
               right=right.convert("1");
               imagen = ImageChops.logical_xor(left, right);

          elif op in ["add","+"]:
               imagen = ImageChops.add(left, right, **params);

          elif op in ["add mod","+ %"]:
               imagen = ImageChops.add_modulo(left, right);

          elif op in ["subtract","-"]:
               imagen = ImageChops.subtract(left, right, **params);

          elif op in ["subtract mod","- %"]:
               imagen = ImageChops.subtract_modulo(left, right);

          elif op in ["multiply","*"]:
               imagen = ImageChops.multiply(left, right);

          elif op in ["blend"]:
               imagen = ImageChops.blend(left, right, **params);

          elif op in ["darker"]:
               imagen = ImageChops.darker(left, right);

          elif op in ["lighter"]:
               imagen = ImageChops.lighter(left, right);

          elif op in ["soft light"]:
               imagen = ImageChops.soft_light(left, right);

          elif op in ["hard light"]:
               imagen = ImageChops.hard_light(left, right);

          elif op in ["overlay"]:
               imagen = ImageChops.overlay(left, right);

          elif op in ["screen"]:
               imagen = ImageChops.screen(left, right);

          elif op=="eval" and self._expression is not None:
               left =left. convert("L");
               right=right.convert("L");
               imagen = ImageMath.eval(self._expression, left=left, right=right, l=left, r=right);

          return imagen;

      #-------------------------------------------------------------------------
      # UNARIAS
      #-------------------------------------------------------------------------
      @Block.slot("image", {Image})
      def slot_image(self, slot, data):

          imagen=None;

          if len(self._op.split())>=2 and self._op.split()[-1] in ["seq","acc"]:
             
             tp=self._op.split()[-1];
             
             if self._last==None:
                self._last=data;

             op=" ".join(self._op.split()[:-1]);
             left =self._last;
             right=data;
             imagen=self._op2(left,right,op,self._kwargs);
             if tp=="seq": self._last=data;
             if tp=="acc": self._last=imagen;
               
          elif self._op=="invert":
               imagen = ImageOps.invert(data);

          elif self._op=="constant":
               imagen = ImageChops.constant(data, **self._kwargs);

          elif self._op=="offset":
               imagen = ImageChops.offset(data, **self._kwargs);

          elif self._op=="autocontrast":
               imagen = ImageOps.autocontrast(data, **self._kwargs);

          elif self._op=="colorize":
               imagen = ImageOps.colorize(data, **self._kwargs);

          elif self._op=="crop":
               imagen = ImageOps.crop(data, **self._kwargs);

          elif self._op=="scale":
               imagen = ImageOps.scale(data, **self._kwargs);

          elif self._op=="deform":
               imagen = ImageOps.deform(data, **self._kwargs);

          elif self._op=="equalize":
               imagen = ImageOps.equalize(data, **self._kwargs);

          elif self._op=="expand":
               imagen = ImageOps.expand(data, **self._kwargs);

          elif self._op=="flip":
               imagen = ImageOps.flip(data);

          elif self._op=="mirror":
               imagen = ImageOps.mirror(data);

          elif self._op=="posterize":
               imagen = ImageOps.posterize(data);

          elif self._op=="solarize":
               imagen = ImageOps.solarize(data);

          elif self._op=="grayscale":
               imagen = ImageOps.grayscale(data);

          elif self._op=="contain":
               imagen = ImageOps.contain(data, **self._kwargs);

          elif self._op=="cover":
               imagen = ImageOps.cover(data, **self._kwargs);

          elif self._op=="fit":
               imagen = ImageOps.fit(data, **self._kwargs);

          elif self._op=="pad":
               imagen = ImageOps.pad(data, **self._kwargs);

          elif self._op=="filter blur":
               imagen = data.filter(ImageFilter.BLUR);
          elif self._op=="filter contour":
               imagen = data.filter(ImageFilter.CONTOUR);
          elif self._op=="filter detail":
               imagen = data.filter(ImageFilter.DETAIL);
          elif self._op=="filter edge enhance":
               imagen = data.filter(ImageFilter.EDGE_ENHANCE);
          elif self._op=="filter edge enhance more":
               imagen = data.filter(ImageFilter.EDGE_ENHANCE_MORE);
          elif self._op=="filter emboss":
               imagen = data.filter(ImageFilter.EMBOSS);
          elif self._op=="filter find edges":
               imagen = data.filter(ImageFilter.FIND_EDGES);
          elif self._op=="filter sharpen":
               imagen = data.filter(ImageFilter.SHARPEN);
          elif self._op=="filter smooth":
               imagen = data.filter(ImageFilter.SMOOTH);
          elif self._op=="filter smooth more":
               imagen = data.filter(ImageFilter.SMOOTH_MORE);

          elif self._op=="filter box blur":
               filter=ImageFilter.BoxBlur(**self._kwargs);
               imagen = data.filter(filter);
          elif self._op=="filter gaussian blur":
               filter=ImageFilter.GaussianBlur(**self._kwargs);
               imagen = data.filter(filter);
          elif self._op=="filter unsharp mask":
               filter=ImageFilter.UnsharpMask(**self._kwargs);
               imagen = data.filter(filter);
          elif self._op=="filter kernel":
               filter=ImageFilter.Kernel(**self._kwargs);
               imagen = data.filter(filter);
          elif self._op=="filter min":
               filter=ImageFilter.MinFilter(**self._kwargs);
               imagen = data.filter(filter);
          elif self._op=="filter median":
               filter=ImageFilter.MedianFilter(**self._kwargs);
               imagen = data.filter(filter);
          elif self._op=="filter max":
               filter=ImageFilter.MaxFilter(**self._kwargs);
               imagen = data.filter(filter);
          elif self._op=="filter mode":
               filter=ImageFilter.ModeFilter(**self._kwargs);
               imagen = data.filter(filter);

          elif self._op=="eval" and self._expression is not None:
               data=data.convert("L");
               imagen = ImageMath.eval(self._expression, image=data);             

          self.signal_image(imagen);
          #self.signal_left (imagen);
          #self.signal_right(imagen);
        
      #-------------------------------------------------------------------------
      # BINARIAS
      #-------------------------------------------------------------------------
      def _binary(self):
          right=self._right;
          left =self._left;
          if left and right:
             imagen=self._op2(left, right, self._op, self._kwargs);
             return imagen;
          return None;      

      #-------------------------------------------------------------------------
      @Block.slot("left", {Image})
      def slot_left(self, slot, data):
          self._left=data;
          imagen=self._binary();
          self.signal_image(imagen);
          self.signal_left(imagen);

      #-------------------------------------------------------------------------
      @Block.slot("right", {Image})
      def slot_right(self, slot, data):
          self._right=data;
          imagen=self._binary();
          self.signal_image(imagen);
          self.signal_right(imagen);

      #-------------------------------------------------------------------------
      # SIGNALS & RUN
      #-------------------------------------------------------------------------
      @Block.signal("image", Image)
      def signal_image(self, data):
          return data;

      #-------------------------------------------------------------------------
      @Block.signal("left", Image)
      def signal_left(self, data):
          return data;

      #-------------------------------------------------------------------------
      @Block.signal("right", Image)
      def signal_right(self, data):
          return data;
