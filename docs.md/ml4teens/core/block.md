Module ml4teens.core.block
==========================

Classes
-------

`Block(**kwargs)`
:   La clase Block, ancestro de todos los bloques y núcleo fundamental del sistema, junto con la clase Context.

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * ml4teens.blocks.display.Display
    * ml4teens.blocks.drain.Drain
    * ml4teens.blocks.forEach.ForEach
    * ml4teens.blocks.ifElse.IfElse
    * ml4teens.blocks.img.convertImage.ConvertImage
    * ml4teens.blocks.img.depthEstimation.DepthEstimation
    * ml4teens.blocks.img.distance.Distance
    * ml4teens.blocks.img.embedding.Embedding
    * ml4teens.blocks.img.faceBoxing.FaceBoxing
    * ml4teens.blocks.img.faceLandmarks.FaceLandmarks
    * ml4teens.blocks.img.faceRecognition.FaceRecognition
    * ml4teens.blocks.img.handGestures.HandGestures
    * ml4teens.blocks.img.handLandmarks.HandLandmarks
    * ml4teens.blocks.img.histogram.Histogram
    * ml4teens.blocks.img.imageOp.ImageOp
    * ml4teens.blocks.img.imageSource.ImageSource
    * ml4teens.blocks.img.imageToText.ImageToText
    * ml4teens.blocks.img.mergeChannels.MergeChannels
    * ml4teens.blocks.img.objectCLS.ObjectCLS
    * ml4teens.blocks.img.objectID.ObjectID
    * ml4teens.blocks.img.poseEstimation.PoseEstimation
    * ml4teens.blocks.img.resizeImage.ResizeImage
    * ml4teens.blocks.img.segmentAll.SegmentAll
    * ml4teens.blocks.img.segmentation.Segmentation
    * ml4teens.blocks.img.similarity.Similarity
    * ml4teens.blocks.img.singleChannel.SingleChannel
    * ml4teens.blocks.img.splitChannels.SplitChannels
    * ml4teens.blocks.img.threshold.Threshold
    * ml4teens.blocks.img.trimImage.TrimImage
    * ml4teens.blocks.img.video2file.Video2File
    * ml4teens.blocks.img.videoSource.VideoSource
    * ml4teens.blocks.terminal.Terminal
    * ml4teens.blocks.timer.Timer
    * ml4teens.blocks.txt.inputText.InputText
    * ml4teens.blocks.txt.oaiChat.OAIChat
    * ml4teens.blocks.value.Value

    ### Static methods

    `signal(name, typedecl)`
    :

    `slot(name, typedecl, default=None)`
    :

    `waitUntil(finish)`
    :

    ### Instance variables

    `params`
    :

    `signals`
    :

    `slots`
    :

    ### Methods

    `checkSignalUsage(self, name)`
    :   Comprueba si el evento (*signal*) está asociado a un *slot*.
        Es equivalente a invocar el método (decorado) correspondente al evento, pero con *data=None*.          
        
        :param name: Nombre del evento (*signal*)
        :type  name: str
        :return:     True si la señal está asocida a un *slot*, False en caso contrario.
        :rtype:      bool

    `run(self, sname, data, mods)`
    :

`StackedDicts(**kwargs)`
:   

    ### Methods

    `begin(self)`
    :

    `commit(self)`
    :

    `get(self, key, default=None)`
    :

    `items(self)`
    :

    `keys(self)`
    :

    `pop(self, *args, **kwargs)`
    :

    `rollback(self)`
    :

    `update(self, *args, **kwargs)`
    :

    `values(self)`
    :