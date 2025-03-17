import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

import argparse
import json
import requests
from io import BytesIO
from pokemontcgsdk import RestClient
from pokemontcgsdk import Card as TCGCard
from pokemontcgsdk import Set as TCGSet
from PIL import Image
from dotenv import load_dotenv

# Add the parent directory to sys.path
from utils.file_utils import sanitize_filename

load_dotenv()
RestClient.configure(os.getenv("POKEMON_TCG_API_KEY"))

data_dir = os.path.join(PROJECT_ROOT, "pokemon_tcg_data")

def save_all_sets(force=False):
    all_sets = TCGSet.all()
    for set in all_sets:
        save_set_data(set, force)

def save_set_data(set: TCGSet, force=False):
    set_folder = os.path.join(data_dir, set.id)

    if os.path.exists(set_folder) and not force:
        print(f"Skipping set with ID {set.id} ({set.name}) as it already exists at {set_folder}")
        return

    os.makedirs(set_folder, exist_ok=True)

    save_data = {
        "id": set.id,
        "name": set.name,
        "series": set.series,
        "printed_total": set.printedTotal,
        "total": set.total,
        "release_date": set.releaseDate
    }

    with open(os.path.join(set_folder, f'{set.id}.json'), 'w') as file:
        json.dump(save_data, file, indent=2)
    
    print(f"Saved {set.name} with ID: {set.id} successfully")

def save_all_cards(force=False):
    card_dict = {}

    page = 1
    while True:
        cards = TCGCard.where(page=page, pageSize=100)
        print(card_dict)

        print(f"Will save the next {len(cards)} cards.") 
        for card in cards:
            if card.set.id not in card_dict:
                card_dict[card.set.id] = []
            
            card_dict[card.set.id].append(card.id)
            save_card_data(card, force)

        # If the number of cards returned is less than the page_size, stop.
        if len(cards) < 100:
            print("Finished saving all card data.")
            break
        
        page += 1

    card_dict_path = os.path.join(data_dir, "card_dict.json")
    with open(card_dict_path, 'w') as file:
        json.dump(card_dict, file, indent=2)


def save_card_data(card: TCGCard, force=False):
    set_folder = os.path.join(data_dir, card.set.id)

    # Save the images
    _save_card_sprite(card, set_folder, force)

    save_data = {
        "id": card.id,
        "name": card.name,
        "number": card.number,
        "artist": card.artist,
        "rarity": card.rarity,
        "flavor_text": card.flavorText,
        "set" : card.set.id #sets are stored separately     
    }

    file_name = sanitize_filename(f"{card.id}.json")
    file_path = os.path.join(set_folder, file_name) 

    if os.path.exists(file_path) and not force:
        print(f"Skipping Card with ID {card.id} ({card.name}) as it already exists at {file_path}")
        return

    with open(file_path, 'w') as file:
        json.dump(save_data, file, indent=2)
    
    print(f"Saved {card.name} with ID: {card.id} successfully")

def _save_card_sprite(card: TCGCard, card_folder: str, force=False):
    image_url = card.images.small
    try:
        # Download the sprite image
        response = requests.get(image_url)
        response.raise_for_status()  # Raise an exception if there's an error

        # Save the image in the appropriate file
        image_name = sanitize_filename(f'{card.id}.png')
        image_path = os.path.join(card_folder, image_name)

        if os.path.exists(image_path) and not force:
            print(f"Skipping Card Image with ID {card.id} ({card.name}) as it already exists at {image_path}")
            return

        try:
            img = Image.open(BytesIO(response.content))
            img.save(image_path)
        except Exception as e:
            print(f"Error saving {card.name} for Card ID {card.id} Image Url: {image_url} Error: {e}")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading {card.name} for Card ID {card.id}: {e}")
    

def main():
    parser = argparse.ArgumentParser(description="Download Pokémon Card data.")
    parser.add_argument("--force", action="store_true", help="Force the download of the Pokémon Card data.")

    # Create directories for storing data
    # Ensure the main directory exists
    os.makedirs(data_dir, exist_ok=True)

    args = parser.parse_args()
    
    save_all_sets(args.force)
    save_all_cards(args.force)  # Fetch and process all Pokémon

if __name__ == "__main__":
    main()


