#!/bin/env python3

########################################################################################
import json;
import ml4teens as ml;

with open("./ml4teens/autodoc.json",mode="wt", encoding="utf-8") as fd:
     autodoc = ml.tools.autodoc.autodoc();
     json.dump(autodoc, fd);
     