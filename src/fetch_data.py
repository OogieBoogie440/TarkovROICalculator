import requests
import json
import os
import time

# --- Configuration ---
# Try to get key from Environment (for GitHub Actions), otherwise use local key
TARKOV_MARKET_API_KEY = os.environ.get("TARKOV_MARKET_API_KEY", "DTe5CfPQ8PUGXoUr")
TARKOV_DEV_URL = 'https://api.tarkov.dev/graphql'
TARKOV_MARKET_URL = 'https://api.tarkov-market.app/api/v1/items/all' # Endpoint to get ALL items at once if possible, or we might need to loop.
# Note: Tarkov-Market /items/all is usually the endpoint for bulk data.

def fetch_recipes_from_tarkov_dev():
    """Fetches crafting recipes from Tarkov.dev (since Tarkov-Market doesn't have them)."""
    query = """
    {
        crafts {
            id
            station {
                name
            }
            level
            duration
            rewardItems {
                item {
                    id
                    name
                }
                count
            }
            requiredItems {
                item {
                    id
                    name
                }
                count
            }
        }
        barters {
            id
            trader {
                name
            }
            level
            requiredItems {
                item {
                    id
                    name
                }
                count
            }
            rewardItems {
                item {
                    id
                    name
                }
                count
            }
        }
    }
    """
    headers = {"Content-Type": "application/json"}
    print("Fetching recipes from tarkov.dev...")
    response = requests.post(TARKOV_DEV_URL, headers=headers, json={'query': query})
    if response.status_code == 200:
        return response.json()['data']
    else:
        raise Exception(f"Tarkov.dev query failed: {response.status_code}")

def fetch_prices_from_tarkov_market():
    """Fetches price data from Tarkov-Market.com using the provided API key."""
    headers = {
        "x-api-key": TARKOV_MARKET_API_KEY
    }
    
    print("Fetching prices from tarkov-market.com...")
    # The /items/all endpoint is efficient for getting everything.
    response = requests.get(TARKOV_MARKET_URL, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Tarkov-Market query failed: {response.status_code} - {response.text}")

def merge_data(recipes, market_data):
    """
    Merges the recipes (from dev) with the prices (from market).
    We need to map them by Item Name or ID.
    Tarkov-Market uses 'bsgId' or 'uid' which usually matches Tarkov.dev 'id'.
    """
    print("Merging data...")
    
    # Create a price lookup map from Tarkov-Market data
    # Key: bsgId (which matches tarkov.dev ID), Value: Price Data
    price_map = {}
    for item in market_data:
        # Tarkov-Market returns a list of item objects
        # We care about 'price' (avg price) or 'avg24hPrice' or 'traderPrice'
        # Let's inspect the structure in logic, but here we just store it.
        # Usually 'bsgId' is the common ID.
        item_id = item.get('bsgId')
        if item_id:
            price_map[item_id] = {
                'price': item.get('price'), # Current price
                'avg24hPrice': item.get('avg24hPrice'),
                'traderPrice': item.get('traderPrice'),
                'name': item.get('name'),
                'updated': item.get('updated')
            }
            
    # We need to reconstruct the 'items' list structure that our logic.py expects
    # logic.py expects: items { id, name, lastLowPrice, basePrice, sellFor... }
    
    formatted_items = []
    
    # We iterate through the price_map to build the items list
    for item_id, data in price_map.items():
        formatted_items.append({
            'id': item_id,
            'name': data['name'],
            'lastLowPrice': data['price'], # Mapping 'price' (current) to 'lastLowPrice' for our logic
            'basePrice': data['traderPrice'], # Using trader price as base
            'sellFor': [] # We can leave this empty or populate if needed, logic.py falls back to basePrice
        })
        
    return {
        'items': formatted_items,
        'crafts': recipes['crafts'],
        'barters': recipes['barters']
    }

def fetch_data():
    try:
        raw_data = fetch_recipes_from_tarkov_dev()
        market_data = fetch_prices_from_tarkov_market()
        
        final_data = merge_data(raw_data, market_data)
        
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        output_file = os.path.join(data_dir, 'tarkov_data.json')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, indent=4)
            
        print(f"Data successfully merged and saved to {output_file}")
        
    except Exception as e:
        print(f"Error fetching data: {e}")

if __name__ == "__main__":
    fetch_data()
