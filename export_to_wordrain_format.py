

import numpy as np
import matplotlib.pyplot as plt
import json
import matplotlib.markers as markers
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator, MaxNLocator, FixedLocator)
from matplotlib import cm
import math
import matplotlib.colors as colors
import os
import matplotlib.dates as mdates
from math import modf
import sys
import datetime
import matplotlib
from collections import Counter


###
# Start
#####

def create_wordrain_dir(model_file, outputdir, new_dir_name, top_nr_documents = None):

    new_dir = os.path.join(outputdir, new_dir_name)
    
    if os.path.exists(new_dir):
        print(new_dir, "Already exists")
        exit()
    
    os.mkdir(new_dir)
    
    
    with open(model_file, 'r') as f:
        data = f.read()
        obj = json.loads(data)


    documents_for_topic = {}
    
    for el in obj["topic_model_output"]["documents"]:
        base_name = el["base_name"]
        document_text = el["text"]
        
        document_topics = []
        for t in el["document_topics"]:

            
            if t["topic_index"] not in documents_for_topic:
                documents_for_topic[t["topic_index"]] = []
            documents_for_topic[t["topic_index"]].append((t["topic_confidence"], document_text))
        
    for index in sorted(documents_for_topic.keys()):
        dir_to_store = os.path.join(new_dir, str(index))
        os.mkdir(dir_to_store)
        for nr, (conf, text) in enumerate(documents_for_topic[index]):
            file_name = os.path.join(dir_to_store, str(nr) + ".txt")
            with open(file_name, "w") as out:
                out.write(text)
    


create_wordrain_dir("/Users/marsk757/journalpolls/code_and_data/t2tdata/data_folder/polls/topics2themes_exports_folder_created_by_system/65a4e258f52ff00acae28c0f_model.json", "/Users/marsk757/journalpolls/code_and_data/wordrain_output", "test")
