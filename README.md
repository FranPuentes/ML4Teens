# ML4Teens

**Machine Learning for Teens** (Aprendizaje Automático para *adolescentes*)

Librería Python (ml4teens) para permitir crear *arquitecturas basadas en bloques* que lleven a cabo un proceso de ML.

Cada bloque hace algo concreto, posiblemente *matizado* por los parámetros del usuario.

Cada uno de ellos genera *signal*s y posee *slot*s.

Un objeto (*singleton*) se encarga de emparejar los signals con slots (con control de tipos).

>[!WARNING]
>Actualmente la rama publicada en Pypi (pip) es **main**, pero la buena es **develop**.
>Cuando sea estable, **main** será la publicada.

>[!NOTE]
>En breve crearé la rama 'stable' desde 'develop'.

>[!CAUTION]
>El submódulo core todavía **no está en estado *estable* **, por lo que puede sufrir cambios en un futuro. Igualmente el submódulo *blocks*.

El código que sigue, muestra un ejemplo de lo que puede hacer el paquete (en 'develop').

```python
import ml4teens as ml;

context   = ml.core.Context.instance.reset();

imagen   = ml.blocks.ImageSource();
img2text = ml.blocks.ImageToText(caption="A photo of an");
terminal = ml.blocks.Terminal();
salida   = ml.blocks.Display(width=300);

imagen  ["image"] >> img2text["image" ];
imagen  ["image"] >> salida  ["image" ];
img2text["text" ] >> terminal["stdout"];

source="https://img.freepik.com/foto-gratis/mujer-tiro-completo-bicicleta-al-aire-libre_23-2149413735.jpg?w=1380&t=st=1704297833~exp=1704298433~hmac=433c68f72fc841cbb094d598521f8b72dad100a383f59b39de5f490cce7c7b99";

context.emit(target=imagen, sname="source", data=source);
context.wait();
```

Por otro lado, hacer un bloque es sencillo, uno básico que -por ejemplo- se queda con un canal de una imagen:

```python
import cv2 as cv;

from PIL.Image import Image;
from PIL.Image import fromarray;

from ml4teens.core import Block;

class SingleChannel(Block):

      #-------------------------------------------------------------------------
      # channel
      def __init__(self, **kwargs):
          super().__init__(**kwargs);
          assert type(self._channel)==int, "El parámetro 'channel' debe ser el número del canal (0, ...)";

      #-------------------------------------------------------------------------
      @Block.slot("image", {Image})
      def slot_image(self, slot, data):
          c=len(data.getbands());
          n=self._channel;
          assert n in range(0,c), f"El canal {n} no puede ser extraído de una imagen de {c} canales (recuerda: empieza a contar en 0)";
          imagen=data.getchannel(n);
          self.signal_image(imagen);
          self.reset("image");

      #-------------------------------------------------------------------------
      @Block.signal("image", Image)
      def signal_image(self, data):
          return data;
```

Este bloque (de tipo *passthru*), puede recibir imágenes en forma de imagen
PIL por medio del **slot** llamado *image* y reenvía el canal indicado de
dicha imagen por medio de una señal, igualmente llamada *image*.

Observar:
* El constructor de la clase puede recibir parámetros de usuario.
* El slot se define mediante un decorador (@Block.slot).
* La señal (*signal*) se define igualmente mediante un decorador (@Block.signal).
* El slot, una vez hecha la conversión, pasa la imagen a la señal, invocando al método *signal_image*.
* Los métodos decorados por @Block.signal no tienen que hacer nada, salvo devolver el dato que -finalmente- se ha de enviar.


