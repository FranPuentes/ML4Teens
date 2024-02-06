import numpy as np;
import seaborn as sns;
import matplotlib.pyplot as plt;
import PIL;

from io import BytesIO;
from PIL.Image import Image;

from mpl_toolkits.axes_grid1.inset_locator import inset_axes

from ...core import Block;

class Histogram(Block):

      def __init__(self, **kwargs):
          super().__init__(**kwargs);

      #-------------------------------------------------------------------------
      # SLOTS
      #-------------------------------------------------------------------------
      @Block.slot("image",{Image})
      def slot_image(self, slot, data):
          if data:
             image = np.array(data);
             
             if len(image.shape) == 2:
                plt.figure(figsize=self.params.figsize or (10, 4));
                sns.histplot(image.ravel(), bins=256, kde=False, color='gray');
                plt.title('Histograma');
                plt.xlabel('Intensidad del Pixel');
                plt.ylabel('Frecuencia');

                plt.constrained_layout();
                
             elif len(image.shape) == 3:
                fig, axs = plt.subplots(nrows=3, ncols=1, figsize=self.params.figsize or (10, 12), constrained_layout=True);
                nombres_canales = ['Rojo', 'Verde', 'Azul'];
                colores = ['red', 'green', 'blue'];
                for i, color in enumerate(colores):
                    sns.histplot(image[:, :, i].ravel(), bins=256, kde=False, ax=axs[i], color=color);
                    axs[i].set_title(f'Histograma del Canal {nombres_canales[i]}');
                    axs[i].set_xlabel('Intensidad de Pixel');
                    axs[i].set_ylabel('Frecuencia');
                    
                    if bool(self.params.thumbnail) is True or any([self.params.alpha, self.params.width, self.params.height]):
                       ax_inset = inset_axes(axs[i], width=self.params.width or "50%", height=self.params.height or "50%", loc='upper left');
                       canal_imagen = image[:, :, i];
                       ax_inset.imshow(canal_imagen, cmap="gray", alpha=self.params.alpha);
                       ax_inset.axis('off');

             try:
               buf = BytesIO();
               plt.savefig(buf, format='png');
               buf.seek(0);

               histograma = PIL.Image.open(buf);
               histograma.load();
               
               self.signal_histogram(histograma);
               
             finally:
               buf.close();
               plt.close();             

      #-------------------------------------------------------------------------
      # SIGNALS
      #-------------------------------------------------------------------------
      @Block.signal("histogram",Image)
      def signal_histogram(self, data):
          return data;

