import json
import os

class TarkovData:
    def __init__(self, data_path):
        with open(data_path, 'r', encoding='utf-8') as f:
            self.raw_data = json.load(f)
        
        self.items = {item['id']: item for item in self.raw_data['items']}
        self.crafts = self.raw_data['crafts']
        self.price_cache = {}

    def get_price(self, item_id):
        if item_id in self.price_cache:
            return self.price_cache[item_id]
        
        item = self.items.get(item_id)
        if not item:
            return 0
        
        # Priority: lastLowPrice (Flea) -> Best Trader Sell -> basePrice
        # User requested "last low price".
        flea_price = item.get('lastLowPrice')
        base_price = item.get('basePrice', 0)
        
        # Sanity Check: If Flea price is absurdly high (likely RMT or outlier), ignore it.
        # Threshold: 20x base price (generous for rare items, but catches 500k grenades)
        # Exception: If base_price is very low (e.g. < 1000), 20x might be valid.
        # Better check: Compare to Trader Price if available.
        
        final_price = 0
        
        if flea_price and flea_price > 0:
            # If flea price is > 1,000,000 and base is < 50,000, it's suspicious.
            if base_price > 0 and flea_price > (base_price * 20) and flea_price > 100000:
                 # Fallback
                 final_price = 0 # Will trigger next check
            else:
                final_price = flea_price
        
        if final_price == 0:
            sell_for = item.get('sellFor')
            if sell_for:
                final_price = max([s['price'] for s in sell_for])
            else:
                final_price = base_price
        
        self.price_cache[item_id] = final_price
        return final_price

    def get_item_name(self, item_id):
        item = self.items.get(item_id)
        return item['name'] if item else "Unknown"

class CraftAnalyzer:
    def __init__(self, data: TarkovData):
        self.data = data

    def analyze_crafts(self):
        results = []
        for craft in self.data.crafts:
            station = craft['station']['name']
            duration = craft['duration'] # seconds
            
            # Calculate Revenue
            revenue = 0
            reward_name = ""
            for reward in craft['rewardItems']:
                price = self.data.get_price(reward['item']['id'])
                revenue += price * reward['count']
                reward_name = reward['item']['name'] # Just take the first one for name

            # Calculate Cost
            cost = 0
            components = []
            for req in craft['requiredItems']:
                price = self.data.get_price(req['item']['id'])
                total_req_cost = price * req['count']
                cost += total_req_cost
                components.append({
                    'name': req['item']['name'],
                    'count': req['count'],
                    'price': price,
                    'total': total_req_cost
                })

            profit = revenue - cost
            profit_per_hour = 0
            if duration > 0:
                profit_per_hour = profit / (duration / 3600)

            results.append({
                'id': craft['id'],
                'station': station,
                'level': craft['level'],
                'duration': duration,
                'reward_name': reward_name,
                'revenue': revenue,
                'cost': cost,
                'profit': profit,
                'profit_per_hour': profit_per_hour,
                'components': components
            })
        
        # Sort by profit per hour
        results.sort(key=lambda x: x['profit_per_hour'], reverse=True)
        return results

class Scheduler:
    def __init__(self, analyzed_crafts):
        self.crafts = analyzed_crafts

    def suggest_queue(self, available_hours, station_filter=None):
        # Simple greedy scheduler
        # 1. Filter by station if needed
        # 2. Find best profit/hr crafts that fit in the time window
        # 3. For the last slot, find the best TOTAL profit craft that starts before time runs out (or fits the "overnight" logic)
        
        available_seconds = available_hours * 3600
        queue = []
        current_time = 0
        
        # Separate candidates
        candidates = [c for c in self.crafts if c['profit'] > 0]
        if station_filter:
            candidates = [c for c in candidates if c['station'] == station_filter]
            
        # Sort by profit/hr
        candidates.sort(key=lambda x: x['profit_per_hour'], reverse=True)
        
        if not candidates:
            return []

        # Fill time with short, high-profit crafts
        # In reality, you can repeat the same craft, but you have to collect it.
        # We will assume the user wants to spam the best craft until they go offline.
        
        best_craft = candidates[0]
        
        while current_time + best_craft['duration'] < available_seconds:
            queue.append(best_craft)
            current_time += best_craft['duration']
            
        # Final craft: "Overnight" or just filling the rest?
        # If we have time left, or even if we are at the end, we want the last craft to be long and high profit.
        # We want a craft that maximizes profit, regardless of duration (since it runs while offline).
        
        # Find best total profit craft
        candidates.sort(key=lambda x: x['profit'], reverse=True)
        best_long_craft = candidates[0]
        
        queue.append(best_long_craft)
        
        return queue

if __name__ == "__main__":
    # Test run
    data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'tarkov_data.json')
    data = TarkovData(data_path)
    analyzer = CraftAnalyzer(data)
    results = analyzer.analyze_crafts()
    
    print(f"Top craft: {results[0]['reward_name']} - {results[0]['profit_per_hour']:.2f} RUB/hr")
    
    scheduler = Scheduler(results)
    queue = scheduler.suggest_queue(4, "Workbench")
    print("Suggested Workbench Queue (4h):")
    for q in queue:
        print(f"- {q['reward_name']} ({q['duration']/60:.0f}m)")
