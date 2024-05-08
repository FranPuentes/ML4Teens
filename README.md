# ML4Teens

**Machine Learning for Teens** (Aprendizaje Automático para *adolescentes*)

Paquete Python (*ml4teens* en pip) que permite crear *arquitecturas basadas en bloques* que lleven a cabo un proceso de ML.

Cada bloque hace algo concreto, en modo *caja negra*; cada uno de ellos genera *signal*s y posee *slot*s en donde recibir las señales.

Un objeto (*singleton*) se encarga de emparejar los signals con slots (con control de tipos) y lanzar la red.

>[!NOTE]
>El submódulo *blocks*/*img* **está en estado estable**.
>
>El submódulo *blocks*/*nlp* **está en estado incompleto** pero usable.
>
>El submódulo *blocks*/*ds* **está en estado incompleto** pero usable.
>
>El submódulo *core* está en estado estable.
>
>La documentación está incompleta.

El código que sigue, muestra un ejemplo -básico- de lo que puede hacer el paquete (en la rama 'main').


```python
import ml4teens as ml;

from ml4teens.tools import prettyPrintException;

with ml.core.Context() as context:
     try:
       imagen   = ml.blocks.img.ImageSource();
       img2text = ml.blocks.img.ImageToText(caption="A photo of an");
       terminal = ml.blocks.Terminal();
       salida   = ml.blocks.Display(width=300);

       imagen  ("image") >> img2text("image" );
       imagen  ("image") >> salida  ("image" );
       img2text("text" ) >> terminal("stdout");

       source="https://img.freepik.com/foto-gratis/mujer-tiro-completo-bicicleta-al-aire-libre_23-2149413735.jpg";

       context.emit(target=imagen, slot_name="source", data=source);
       context.wait();

     except Exception as e:
       prettyPrintException(e);

```

Por otro lado, hacer un bloque es sencillo, uno básico que -por ejemplo- que se queda con sólo un canal de una imagen:

```python
from PIL.Image import Image;
from PIL.Image import fromarray;

from ml4teens.core import Block;

class SingleChannel(Block):

      #-------------------------------------------------------------------------
      # channel
      def __init__(self, **kwargs):
          super().__init__(**kwargs);
          assert isinstance(self.params.channel, int), "El parámetro 'channel' debe ser el número del canal (0, ...)";

      #------------------------------------------------------------------------- slots
      @Block.slot("image", {Image})
      def slot_image(self, slot, data):
          c=len(data.getbands());
          n=self.params.channel;
          assert n in range(0,c), f"El canal {n} no puede ser extraído de una imagen de {c} canales (recuerda: empieza a contar en 0)";
          imagen=data.getchannel(n);
          self.signal_image(imagen);

      #------------------------------------------------------------------------- signals
      @Block.signal("image", Image)
      def signal_image(self, data):
          return data;
```

Este bloque recibe imágenes (una a una) en el **slot** llamado *image* y reenvía el canal indicado de dicha imagen por medio de una señal,
igualmente llamada *image*.

