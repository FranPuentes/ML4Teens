Module ml4teens.blocks.img.faceRecognition
==========================================

Classes
-------

`FaceRecognition(**kwargs)`
:   Dada una imagen de referencia (slot "reference"), con una o más caras que pueden ser detectadas, aprende a reconocer dichas caras en las sucesivas imágenes que se le entreguen (slot "image").
    
    Se le puede entregar al constructor un objeto Image (param "reference") para tener una referencia desde el principio.
    
    Emite dos señales:
    
    1) Un diccionario con las caras reconocidas (signal "recognized").
    2) La imagen de entrada (slot "image") con las caras reconocidas (slot/param "reference").
    
    El formato del diccionario con las facciones reconocidas es el mismo que el de la identificacioón de caras (FaceBoxing) + la etiqueta de la cara reconocida.

    ### Ancestors (in MRO)

    * ml4teens.core.block.Block
    * abc.ABC

    ### Static methods

    `boxes(model, imagen, minconf=0.0)`
    :

    `download(source: str)`
    :

    `embedding(processor, model, data, lm)`
    :

    `normalize(image, landmarks)`
    :

    `similarity(emb1, emb2)`
    :

    ### Methods

    `encodings(self, imagen, minconf=0.0)`
    :

    `signal_image(self, data='533643831eb34c8ccdbfcd91d1a4a98dc3106e0d6d97446682cc91cfb4efcb2e')`
    :

    `signal_recognized(self, data='38f944f664c3accd86d60bf29fc455aefc89455de1173f015d064e042e498bd8')`
    :

    `signal_reference(self, data='781429126dcfc31759b0359feeb623b1efe6355d94dcd84a8111ca7bbf5d8547')`
    :

    `slot_image(self, _slot, data)`
    :

    `slot_reference(self, _slot, data)`
    :