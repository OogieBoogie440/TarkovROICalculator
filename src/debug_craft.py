import json
import os
from logic import TarkovData

def debug_craft(craft_name_fragment):
    data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'tarkov_data.json')
    data = TarkovData(data_path)
    
    print(f"Searching for craft: {craft_name_fragment}")
    
    found = False
    for craft in data.crafts:
        reward_name = craft['rewardItems'][0]['item']['name']
        if craft_name_fragment.lower() in reward_name.lower():
            found = True
            print(f"\n--- Craft Found: {reward_name} ---")
            print(f"Station: {craft['station']['name']} (Lvl {craft['level']})")
            print(f"Duration: {craft['duration']}s")
            
            print("\nREVENUE:")
            total_revenue = 0
            for reward in craft['rewardItems']:
                r_item = reward['item']
                count = reward['count']
                
                # Debug values
                raw_item = data.items.get(r_item['id'])
                print(f"  [DEBUG] {r_item['name']} - Base: {raw_item.get('basePrice')} | Flea: {raw_item.get('lastLowPrice')}")
                
                price = data.get_price(r_item['id'])
                total = price * count
                print(f"  - {count}x {r_item['name']} @ {price} = {total}")
                total_revenue += total
            print(f"  Total Revenue: {total_revenue}")
            
            print("\nCOST:")
            total_cost = 0
            for req in craft['requiredItems']:
                q_item = req['item']
                count = req['count']
                price = data.get_price(q_item['id'])
                total = price * count
                print(f"  - {count}x {q_item['name']} @ {price} = {total}")
                total_cost += total
            print(f"  Total Cost: {total_cost}")
            
            profit = total_revenue - total_cost
            print(f"\nPROFIT: {profit}")
            if craft['duration'] > 0:
                pph = profit / (craft['duration'] / 3600)
                print(f"PROFIT/HR: {pph}")

    if not found:
        print("Craft not found.")

if __name__ == "__main__":
    debug_craft("VOG-25 Khattabka")
