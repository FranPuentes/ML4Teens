#!/bin/env python3

########################################################################################
import json;
import ml4teens as ml;

with open("./ml4teens/autodoc.json", mode="r+", encoding="utf-8") as fd:
     autodoc = ml.tools.autodoc.autodoc();
     fd.seek(0);     
     json.dump(autodoc, fd);
     current_position = fd.tell();
     fd.truncate(current_position);
