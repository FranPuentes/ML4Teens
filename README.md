# ML4Teens

**Machine Learning for *Teens* *** (Aprendizaje Automático para *adolescentes*)

Librería Python (ml4teens) para permitir crear *arquitecturas basadas en bloques" que lleven a cabo un proceso de ML.

Cada bloque hace algo concreto, posiblemente *matizado* por los parámetros del usuario.
Cada uno de ellos genera *signal*s y posee *slot*s.

Un objeto (*singleton*) se encarga de unos signals con slots (con control de tipos).

El código que sigue, muestra un ejemplo de lo que puede hacer el paquete.

```
import ml4teens as ml;

context   = ml.core.Context.instance.reset();

vídeo    = ml.blocks.VideoSource(fuente="https://cdn.pixabay.com/vimeo/188704568/parque-6096.mp4?width=640&hash=112e5fd94cb9090c07f4472a41d182d344db647b");
yolo     = ml.blocks.Yolo();
pantalla = ml.blocks.Screen(width=640);
terminal = ml.blocks.Terminal();

vídeo["información"] >> terminal["stdin"];
vídeo["dimensiones"] >> terminal["stdin"];

(vídeo["frame"] >> yolo["frame"])["frame"] >> pantalla["frame"];

context.run(vídeo);

```

+ Carga la librería.
+ Define los objetos: vídeo, yolo, terminal y pantalla. Cada uno de ellos es un bloque.
+ Establece las conexiones entre *signal*s y *slot*s, mediente el operador **>>**
+ Ejecuta el objeto 'vídeo', ya que es el punto de entrada.

>[!NOTE]
>El resultado es todavía muy primitivo, pero es funcional.

>[!WARNING]
>Este ejemplo va lento en Colab, mejor ejecútalo en un jupyter local.

