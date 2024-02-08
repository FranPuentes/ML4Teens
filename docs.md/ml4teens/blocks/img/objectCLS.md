Module ml4teens.blocks.img.objectCLS
====================================

Classes
-------

`ObjectCLS(**kwargs)`
:   Recibe una imagen (slot 'frame' o 'image') en forma de PIL.Image, y emite la misma imagen, pero con los elementos identificados.
    URL: https://docs.ultralytics.com/modes/predict
    
    Parámetos del objeto:
    'conf':    object confidence threshold for detection (float, 0.25)
    'iou':     intersection over union (IoU) threshold for NMS (float, 0.7)
    'device':  device to run on, i.e. cuda device=0/1/2/3 or device=cpu (None|str)
    'max_det': maximum number of detections per image (int, 300)
    'classes': filter results by class, i.e. classes=0, or classes=[0,2,3] (int|list[int])
    
    SLOTS:
    image <- PIL.Image
    
    SIGNALS:
    image -> PIL.Image
    boxes -> object
    
    Constructor: puede recibir varios parámetros opcionales.

    ### Ancestors (in MRO)

    * ml4teens.core.block.Block
    * abc.ABC

    ### Methods

    `signal_class(self, data='e535854415f48ba04738b38ad37e3b732e9d30c92095b0b36f1831ba526bc37b')`
    :

    `signal_classes(self, data='be67e6c09466911441cf6e45b32aa66d6e2c9ee5f6ce7f09ee8ab09286939178')`
    :

    `signal_end(self, data='8e3f3c49018246dc5791183bd99bd777e9e5183a05bafdf94aa5d8696f5edfcf')`
    :

    `signal_image(self, data='fcebd9e54d181bc47f8ac03ce0379c33b8a95f0fb732490a9af22ab58e1ef9b1')`
    :

    `slot_image(self, _slot, data)`
    :

    `slot_next(self, _slot, data)`
    :