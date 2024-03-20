import os;
import zipfile;
import tempfile;
import textwrap;
import random;
import shutil;
import yaml;
import json;

from itertools import accumulate;

from ultralytics import YOLO;

#TODO https://docs.ultralytics.com/es/usage/callbacks/#returning-additional-information-with-prediction

# TODO: formato .zip de Label Studio!

from ...tools import searchFilename, searchPattern;

from ...core import Block;

class YoloTrain(Block):

      #--------------------------------------------------------------------------
      def __init__(self, **kwargs):
          super().__init__(**kwargs);
          self._from_url=None;
          
      #--------------------------------------------------------------------------
      def param(self, conf, key, default=None):
          if key in self.params: return self.params[key];
          if key in conf:        return conf[key];
          return default;

      #--------------------------------------------------------------------------
      def _adapt(self, source):
      
          #print("--->",os.path.join(source,"notes.json"))
          #print("--->",os.path.join(source,"images")    )
          #print("--->",os.path.join(source,"labels")    )
          #print("--->",os.path.join(source,"data")      )
          
          if os.path.isdir(os.path.join(source,"images")) and os.path.isdir(os.path.join(source,"labels")) and not os.path.exists(os.path.join(source,"data")):
             
             #LabelStudio
             
             images=os.path.join(source,"images");
             labels=os.path.join(source,"labels");
             data  =os.path.join(source,"data"  );
             
             os.makedirs(data);
             
             for filename in os.listdir(images):
                 filepath=os.path.join(images,filename);
                 if os.path.isfile(filepath): shutil.move(filepath, data);
                 
             for filename in os.listdir(labels):
                 filepath=os.path.join(labels,filename);
                 if os.path.isfile(filepath): shutil.move(filepath, data);
             
             if os.path.exists(os.path.join(source,"notes.json")):
                labels=[];
                notes=os.path.join(source,"notes.json");
                with open(notes, 'r', encoding='utf-8') as fd:
                     notes = json.load(fd);
                     for category in notes["categories"]:
                         id=category["id"];
                         assert id==len(labels), "La numeración de las etiquetas no es correlativa";
                         labels.append(category["name"]);
                
                conf={};
                conf["names"]=labels;
                yaml_file = os.path.join(source,'dataset.yaml');
                with open(yaml_file, 'wt') as fd:
                     yaml.dump(conf, fd);
      
      #--------------------------------------------------------------------------
      def _train(self, conf):
          
          current = os.getcwd();
          try:
            source=conf["path"];
            os.chdir(source);
            
            yaml_file = os.path.join(conf["tmp"],'dataset.yaml');
            with open(yaml_file, 'wt') as fd:
                 yaml.dump(conf, fd);
            
            os.environ["YOLO_VERBOSE"]="false";
            model = YOLO(task="detect", model=self.param(conf,"model","yolov8n.pt"), verbose=False);
            try:
              epochs=self.param(conf,"epochs", 10);
              imgsz =self.param(conf,"imgsz", 640);
              batch =self.param(conf,"batch",  -1);
              model.train(verbose=False, imgsz=imgsz, batch=batch, epochs=epochs, data=yaml_file, project=conf["run"], name=".", exist_ok=True, plots=True);
            finally:
              del model;  
          finally:
            os.chdir(current);

      #--------------------------------------------------------------------------
      def _split(self, conf):
      
          current = os.getcwd();
          try:
            source=conf["path"];
            os.chdir(source);
          
            data     =conf["data" ];
            tmp_train=conf["train"];
            tmp_val  =conf["val"  ];
            tmp_test =conf["test" ];
            f        =self.param(conf,"split",(80,15,5));

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
          finally:
            os.chdir(current);

      #--------------------------------------------------------------------------
      def _yaml(self, source):
      
          yaml_filename=os.path.join(source,"dataset.yaml");
          
          if os.path.isfile(yaml_filename):
             with open(yaml_filename, 'r') as fd:
                  conf = yaml.safe_load(fd);
                  conf["yaml" ]=yaml_filename;
                  conf["path" ]=source;
                  conf["data" ]="./data";
                  conf["run"  ]="./run";
                  conf["tmp"  ]="./tmp";
                  conf["train"]="./tmp/train";
                  conf["val"  ]="./tmp/val";
                  conf["test" ]="./tmp/test";
                  return conf;
                  
          else:             
             conf={};             
             conf["yaml" ]=None;
             conf["path" ]=source;
             conf["data" ]=os.path.join(source,"data");
             conf["run"  ]=os.path.join(source,"run");
             conf["tmp"  ]=os.path.join(source,"tmp");
             conf["train"]=os.path.join(source,"tmp","train");
             conf["val"  ]=os.path.join(source,"tmp","val");
             conf["test" ]=os.path.join(source,"tmp","test");
             return conf;

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

             #print("-->", source, flush=True);
             
             assert os.path.exists(source) and os.path.isdir(source), f"'{source}' no existe o no es un directorio!";

             source_data=os.path.join(source,"data");
             source_run =os.path.join(source,"run");
             source_tmp =os.path.join(source,"tmp");

             self._adapt(source);
                    
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

             conf = self._yaml(source);
             self._split(conf);
             self._train(conf);
             
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
