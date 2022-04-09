import os
import json
import csv
import glob

def fill_zero(str):
    while len(str) < 4:
        str = "0" + str
    return str

def convert_to_csv(json_topic_names, json_model, json_themes, file_name_text_dict):
    
    document_theme_dict = {}
    for theme_el in json_themes:
        for document_id in theme_el['document_ids']:
            if document_id not in document_theme_dict:
                document_theme_dict[document_id] = []
            document_theme_dict[document_id].append(theme_el)
            
    topic_names_sorted = sorted(json_topic_names, key=lambda k: 'topic_id')
    header_list = []
    
    header_list.append("Keywords")
    header_list.append("Text")
    header_list.append("Your theme")
    header_list.append("Most common theme")
    header_list.append("2nd most common theme")
    header_list.append("3rd most common theme")
    header_list.append("Rest of themes")
    index_start_topics = len(header_list)
    
    id_index_dict = {}
    for nr, el in enumerate(topic_names_sorted):
        header_list.append(el['topic_name'].strip())
        id_index_dict[int(el['topic_id'])] = nr
    
    index_end_topics = len(header_list)
    header_list.append("Filename")
    
    outputfile = open('test_output.txt', 'w')
    to_write = "\t".join(header_list) + "\n"
    outputfile.write(to_write)
        
    included_file_names = set()
    for document in json_model["topic_model_output"]["documents"]:
        
        row_list = [""]*len(header_list)
        
        #themes
        if str(document['id']) in document_theme_dict:
            themes_sorted = sorted(document_theme_dict[str(document['id'])], key=lambda x: len((x['document_ids'])), reverse = True)
            row_list[3] = fill_zero(str(len(themes_sorted[0]['document_ids']))) + " occ: " +  themes_sorted[0]['theme_name']
            if len(themes_sorted) > 1:
                row_list[4] = fill_zero(str(len(themes_sorted[1]['document_ids']))) + " occ: " + themes_sorted[1]['theme_name']
            if len(themes_sorted) > 2:
                row_list[5] = fill_zero(str(len(themes_sorted[2]['document_ids']))) + " occ: " + themes_sorted[2]['theme_name']
            if len(themes_sorted) > 3:
                row_list[6] = " / ".join([fill_zero(str(len(t['document_ids']))) + " occ: " + t['theme_name'] for t in themes_sorted[3:]])
        #key words and topics
        key_words = []
        for document_topic in document["document_topics"]:
            key_words.extend(document_topic['terms_found_in_text'])
            id_index = id_index_dict[document_topic['topic_index']]
            row_list[index_start_topics + id_index] = str(round(document_topic['topic_confidence'], 2)).replace(".",",") # Swedish Excel
        
        key_words = list(set(key_words))
        repr_terms = []
        for key_word in key_words:
            terms_to_pick_as_rep = []
            splitted_key_word = sorted(key_word.split("__"), key=len)
            terms_to_pick_as_rep.append(splitted_key_word[0])
            for splitted in splitted_key_word[1:]:
                add_splitted = True
                for existing_reps in terms_to_pick_as_rep[:]:
                    if (len(existing_reps) > 1 and existing_reps in splitted) or (len(existing_reps) > 3 and existing_reps[:-2] in splitted): # Adapted to only to suffixing lang.
                        add_splitted = False # Don't add a longer form of a word
                if add_splitted or "_" in splitted:
                    terms_to_pick_as_rep.append(splitted)
                 
            repr_terms.append("/".join(terms_to_pick_as_rep))
        
        row_list[0] = ", ".join(repr_terms)
        
        #text
        row_list[1] = document['text'].replace("\t", " ").replace("\n", " ").strip()
        
        #name of text
        row_list[index_end_topics] = document['base_name'].replace(".txt", "")
        
        to_write_row = "\t".join(row_list) + "\n"
        outputfile.write(to_write_row)
        
        included_file_names.add(document['base_name'])
    
    not_covered = set(file_name_text_dict.keys()) - included_file_names
    for file_name in list(not_covered):
        row_list = [""]*len(header_list)
        row_list[index_end_topics] = file_name.replace(".txt", "")
        row_list[1] = file_name_text_dict[file_name].replace("\t", " ").replace("\n", " ").strip()
        to_write_row = "\t".join(row_list) + "\n"
        outputfile.write(to_write_row)
        
    outputfile.close()
        
if __name__ == '__main__':
    #folder = "/Users/marsk757/topic2themes/topics2themes/data_folder/språk-tilltal-delat/topics2themes_exports_folder_created_by_system"
    #model_nr = "61d9bbb060423d19911efd8a"
    #model_nr = "61dcc03a8002335ed70e493f"
    #model_nr = "61df484b2ca8753abecb663a"
    
    folder = "/Users/marsk757/topic2themes/topics2themes/data_folder/cycling/topics2themes_exports_folder_created_by_system"
    model_nr = "61ea6c0301c7c1346b1ff9f4"
    files_folder = "/Users/marsk757/topic2themes/topics2themes/data_folder/cycling/cycling/"
    
    file_names = glob.glob(os.path.join(files_folder, "*.txt"))
    file_name_text_dict = {}
    for file_name in file_names:
        with open(file_name) as f:
            file_name_text_dict[os.path.basename(file_name)] = f.read()
    
    topic_names = open(os.path.join(folder, model_nr + "_topic_name.json"), "r")
    
    model = open(os.path.join(folder, model_nr + "_model.json"), "r")
    
    themes = open(os.path.join(folder, model_nr + "_theme.json"), "r")
    
    json_topic_names = json.loads(topic_names.read())
    json_model = json.loads(model.read())
    json_themes = json.loads(themes.read())
    
    topic_names.close()
    model.close()
    themes.close()
    convert_to_csv(json_topic_names, json_model, json_themes, file_name_text_dict)