Module ml4teens.blocks.img.objectID
===================================

Classes
-------

`ObjectID(**kwargs)`
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

    `classes(self)`
    :

    `signal_boxes(self, data='fc82f14308e3aa3bc0dcb4df080c31b467fdf4fc38eaf3e0736787fdfea48647')`
    :

    `signal_image(self, data='457054a8025b58df7d6b79eaf312bfe13de6655ac75b7487f782f3cfedd7bad4')`
    :

    `slot_image(self, _slot, data)`
    :