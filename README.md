# ML4Teens

**Machine Learning for Teens** (Aprendizaje Automático para *adolescentes*)

Librería Python (ml4teens) para permitir crear *arquitecturas basadas en bloques" que lleven a cabo un proceso de ML.

Cada bloque hace algo concreto, posiblemente *matizado* por los parámetros del usuario.
Cada uno de ellos genera *signal*s y posee *slot*s.

Un objeto (*singleton*) se encarga de emparejar los signals con slots (con control de tipos).

El código que sigue, muestra un ejemplo de lo que puede hacer el paquete.

```python
import ml4teens as ml;

context   = ml.core.Context.instance.reset();

vídeo    = ml.blocks.VideoSource(fuente="https://cdn.pixabay.com/vimeo/188704568/parque-6096.mp4?width=640&hash=112e5fd94cb9090c07f4472a41d182d344db647b");
objid    = ml.blocks.ObjectID();
pantalla = ml.blocks.Screen(width=640);
terminal = ml.blocks.Terminal();

vídeo["información"] >> terminal["stdin"];
vídeo["dimensiones"] >> terminal["stdin"];

(vídeo["frame"] >> objid["frame"])["frame"] >> pantalla["frame"];

context.run(vídeo);

```

+ Carga la librería.
+ Define los objetos: vídeo, objid, terminal y pantalla. Cada uno de ellos es un bloque.
+ Establece las conexiones entre *signal*s y *slot*s, mediente el operador **>>**
+ Ejecuta el objeto 'vídeo', dado que es el punto de entrada.

Por otro lado, hacer un bloque es sencillo, uno básico que -por ejemplo- convierte una imagen a tono de grises es:

```python
import cv2 as cv;
import numpy as np;

from ml4teens.core import Block;

class SingleChannel(Block):

      def __init__(self, **kwargs):
          super().__init__(**kwargs);

      @Block.slot("frame", {np.ndarray}, required=True)
      def slot_frame(self, slot, data):
          frame = cv.cvtColor(data, cv.COLOR_BGR2GRAY);
          self.signal_frame(frame);
          self.reset("frame");

      @Block.signal("frame", np.ndarray)
      def signal_frame(self, data):
          return data;

      def run(self, **kwarg):
          raise RuntimeError("No tiene sentido invocar el método 'run' de un objeto de clase 'SingleChannel'.");
```

Este bloque (de tipo *passthru*), puede recibir imágenes en forma de tensor numpy por medio del slot llamado *frame* y reenvía dicho tensor por medio de una señal, igualmente llamada *frame*.

Observar:
* El constructor de la clase puede recibir parámetros de usuario. En este ejemplo no hace uso de ninguno de ellos.
* El slot se define mediante un decorador (@Block.slot).
* La señal (*signal*) se define igualmente mediante un decorador.
* El slot, una vez hecha la conversión, pasa el tensor a la señal, invocando al método *signal_frame*.
* Los métodos decorados por @Block.signal no tienen que hacer nada, salvo devolver el dato que -finalmente- se ha de enviar.
* El método *run* en este caso no es significativo.

>[!NOTE]
>El resultado es todavía muy primitivo, pero es funcional.

>[!WARNING]
>Este ejemplo va lento en Colab, mejor ejecútalo en un jupyter local.

>[!CAUTION]
>El submódulo core todavía no está en estado *estable*, por lo que puede sufrir cambios en un futuro. Igualmente el submódulo *blocks*.


