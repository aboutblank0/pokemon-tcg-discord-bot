import os
import sys
import json

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

data_dir = os.path.join(PROJECT_ROOT, "pokemon_tcg_data")

def generate_dict():
    card_dict = {}

    # Loop through each directory in data_dir
    for root, dirs, files in os.walk(data_dir):
        # If the current directory is at the top level (just subdirectories)
        if root == data_dir:
            for dir_name in dirs:
                card_dict[dir_name] = []

                # Now look through files in this directory
                dir_path = os.path.join(root, dir_name)
                for file_name in os.listdir(dir_path):
                    if "-" in file_name and file_name.endswith('.json'):
                        card_dict[dir_name].append(file_name[:-5])
    
    #Remove empty keys
    for key in tuple(card_dict):
        if card_dict[key] == []:
            card_dict.pop(key)

    #Write the file
    card_dict_path = os.path.join(data_dir, "card_dict.json")
    with open(card_dict_path, 'w') as file:
        json.dump(card_dict, file, indent=2)

if __name__ == "__main__":
    generate_dict()