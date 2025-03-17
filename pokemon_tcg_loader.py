import json
import os
import random
from schemas.pokemon_card_schema import PokemonCardSchema
from schemas.pokemon_card_set_schema import PokemonCardSetSchema
from utils.file_utils import sanitize_filename
from PIL import Image

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(PROJECT_ROOT, "pokemon_tcg_data")

pokemon_tcg_data = None

class PokemonTCGLoader:
    @staticmethod
    def load_data():
        global pokemon_tcg_data
        
        # Only load JSON data once
        if pokemon_tcg_data is None:
            json_file_path = os.path.join(data_dir, "card_dict.json")  # Adjust path as needed
            with open(json_file_path, 'r') as file:
                pokemon_tcg_data = json.load(file)
        
        return pokemon_tcg_data
        
    @staticmethod
    def get_random_card() -> PokemonCardSchema:
        random_set_id = random.choice(list(pokemon_tcg_data.keys()))
        random_card_id = random.choice(pokemon_tcg_data[random_set_id])
        return PokemonTCGLoader.load_card_data(random_card_id)

    @staticmethod
    def load_set_data(pokemon_tcg_set_id):
        file_name = sanitize_filename(f'{pokemon_tcg_set_id}.json')

        set_folder = os.path.join(data_dir, pokemon_tcg_set_id)
        set_file = os.path.join(set_folder, file_name)

        with open(set_file, 'r') as file:
            set_data = json.load(file)
            return PokemonCardSetSchema.model_validate(set_data)

        return None

    @staticmethod
    def load_card_data(pokemon_tcg_card_id):
        set_id = pokemon_tcg_card_id.split("-")[0]
        file_name = sanitize_filename(f'{pokemon_tcg_card_id}.json')

        card_file_path = os.path.join(data_dir, set_id)
        card_file_path = os.path.join(card_file_path, file_name)

        with open(card_file_path, 'r') as file:
            card_data = json.load(file)
            from schemas.pokemon_card_schema import PokemonCardSchema
            return PokemonCardSchema.model_validate(card_data)

        return None

    @staticmethod
    def load_card_image(pokemon_tcg_card_id):
        set_id = pokemon_tcg_card_id.split("-")[0]

        set_folder = sanitize_filename(set_id)
        file_name = sanitize_filename(f'{pokemon_tcg_card_id}.png')

        image_file_path = os.path.join(data_dir, set_folder)
        image_file_path = os.path.join(image_file_path, file_name)

        return Image.open(image_file_path).convert('RGBA')
