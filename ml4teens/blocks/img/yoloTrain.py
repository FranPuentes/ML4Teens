import os;
import zipfile;
import tempfile;
import textwrap;
import random;
import shutil;

from itertools import accumulate;

from ultralytics import YOLO;

#TODO https://docs.ultralytics.com/es/usage/callbacks/#returning-additional-information-with-prediction

from ...tools import searchFilename, searchPattern;

from ...core import Block;

class YoloTrain(Block):

      #--------------------------------------------------------------------------
      def __init__(self, **kwargs):
          super().__init__(**kwargs);
          self._from_url=None;

      #--------------------------------------------------------------------------
      def _train(self, source, basemodel, **kwargs):
          current = os.getcwd();
          try:
            os.chdir(source);
            os.environ["YOLO_VERBOSE"]="false";
            yaml_file = os.path.join(source,"tmp",'dataset.yaml');
            model = YOLO(task="detect", model=basemodel, verbose=False);
            try:
              model.train(verbose=False, imgsz=640, batch=-1, epochs=5, data=yaml_file, project=os.path.join(source,"run"), name=".", exist_ok=True, plots=True, **kwargs);
            finally:
              del model;  
          finally:
            os.chdir(current);

      #--------------------------------------------------------------------------
      def _split(self, data, tmp_train, tmp_val, tmp_test, f=(80,15,5)):

          assert len(f)==3 and (sum(f)==100 or sum(f)==1.0) and all((n>0 for n in f));

          if sum(f)==100: f=[n/100.0 for n in f];
          else:           f=lista(f);
          f.insert(0,0);
          f=list(accumulate(f));

          img_exts  = (".jpg",".jpeg",".png",".gif");
          img_names = [archivo for archivo in os.listdir(data) if archivo.lower().endswith(img_exts)]
          txt_names = [];
          for img_name in img_names:
              name=os.path.splitext(img_name)[0];
              txt_name=f"{name}.txt";
              assert os.path.exists(os.path.join(data,txt_name)) and os.path.isfile(os.path.join(data,txt_name)), f"No existe el fichero {txt_name}";
              txt_names.append(txt_name);

          f=[int(len(txt_names)*n) for n in f];
          assert len(f)==4 and f[0]==0 and f[3]==len(txt_names);

          indexes=list(range(0,len(txt_names)));
          random.shuffle(indexes);
          indexes_train=indexes[    :f[1]];
          indexes_val  =indexes[f[1]:f[2]];
          indexes_test =indexes[f[2]:    ];
          assert len(indexes_train)+len(indexes_val)+len(indexes_test) == len(txt_names);

          for index in indexes_train:
              sfn = os.path.join(data,     txt_names[index]);
              tfn = os.path.join(tmp_train,txt_names[index]);
              shutil.copyfile(sfn, tfn);
              sfn = os.path.join(data,     img_names[index]);
              tfn = os.path.join(tmp_train,img_names[index]);
              shutil.copyfile(sfn, tfn);

          for index in indexes_val:
              sfn = os.path.join(data,    txt_names[index]);
              tfn = os.path.join(tmp_val, txt_names[index]);
              shutil.copyfile(sfn, tfn);
              sfn = os.path.join(data,    img_names[index]);
              tfn = os.path.join(tmp_val, img_names[index]);
              shutil.copyfile(sfn, tfn);

          for index in indexes_test:
              sfn = os.path.join(data,    txt_names[index]);
              tfn = os.path.join(tmp_test,txt_names[index]);
              shutil.copyfile(sfn, tfn);
              sfn = os.path.join(data,    img_names[index]);
              tfn = os.path.join(tmp_test,img_names[index]);
              shutil.copyfile(sfn, tfn);

      #--------------------------------------------------------------------------
      def _yaml(self, tmp, labels):
          content=f"""
          path: {tmp}
          train: train
          val: val

          names:""";

          yaml_filename=os.path.join(tmp,"dataset.yaml");
          with open(yaml_filename,"wt", encoding='utf-8') as fd:
               print(textwrap.dedent(content), file=fd);
               for idx,label in enumerate(labels):
                   print(f"  {idx}: {label}", file=fd);

      #--------------------------------------------------------------------------
      @Block.slot("dataset", {str})
      def slot_dataset(self, slot, source):
          if source:
             
             source=os.path.abspath(source);

             if os.path.exists(source) and os.path.isfile(source):
                with zipfile.ZipFile(source, 'r') as azip:
                     if self.params.useTempDir:
                        a_dir = tempfile.mkdtemp();
                     else:
                        path  = os.path.dirname(source);                        
                        a_dir = path;
                     azip.extractall(a_dir);
                     base = os.path.basename(source);
                     name, _ = os.path.splitext(base);
                     source = os.path.join(a_dir,name);
                    
             assert os.path.exists(source) and os.path.isdir(source), f"'{source}' no existe o no es un directorio!";

             source_data=os.path.join(source,"data");
             source_run =os.path.join(source,"run");
             source_tmp =os.path.join(source,"tmp");

             assert os.path.exists(source_data), "No existe el subdirectorio con los datos!";

             if not os.path.exists(source_run):
                os.makedirs(source_run);

             if not os.path.exists(source_tmp):
                os.makedirs(source_tmp);
                source_tmp_train = os.path.join(source_tmp,"train");
                source_tmp_val   = os.path.join(source_tmp,"val");
                source_tmp_test  = os.path.join(source_tmp,"test");
                os.makedirs(source_tmp_train);
                os.makedirs(source_tmp_val  );
                os.makedirs(source_tmp_test );
             else:
                source_tmp_train = os.path.join(source_tmp,"train");
                source_tmp_val   = os.path.join(source_tmp,"val");
                source_tmp_test  = os.path.join(source_tmp,"test");

             self._yaml (source_tmp, self.params.labels or ["Nop","Yep"]);
             self._split(source_data, source_tmp_train, source_tmp_val, source_tmp_test);
             self._train(source, self.params.model or "yolov8n.pt");
             
             files={ "model":            searchFilename(source_run, "best.pt"),
                     "args":             searchFilename(source_run, "args.yaml"),
                     "confusion matrix": searchFilename(source_run, "confusion_matrix.png"),
                     "F1 curve":         searchFilename(source_run, "F1_curve.png"),
                     "P curve":          searchFilename(source_run, "P_curve.png"),
                     "R curve":          searchFilename(source_run, "R_curve.png"),
                     "PR curve":         searchFilename(source_run, "PR_curve.png"),
                     "results":          searchFilename(source_run, "results.csv"),
                     "batchs":           { "train":searchPattern(source_run,"train_batch*.jpg"), "val":searchPattern(source_run,"val_batch*.jpg") },
                     "data":             { "train":source_tmp_train, "val":source_tmp_val, "test":source_tmp_test },
                   };

             self.signal_files(files);

      #--------------------------------------------------------------------------
      @Block.signal("files", dict)
      def signal_files(self, data):
          return data;

      #--------------------------------------------------------------------------
      @Block.slot("close", {object})
      def slot_close(self, slot, data):
          if self._from_url is not None:
             del self._from_url;
