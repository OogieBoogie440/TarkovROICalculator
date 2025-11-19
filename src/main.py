import json
import os
from fetch_data import fetch_data
from logic import TarkovData, CraftAnalyzer, Scheduler

def main():
    # 1. Fetch latest data (optional, can comment out to use cache)
    # fetch_data() 
    
    # 2. Load Data
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, 'data', 'tarkov_data.json')
    
    if not os.path.exists(data_path):
        print("Data file not found, fetching...")
        fetch_data()
    
    tarkov_data = TarkovData(data_path)
    
    # 3. Analyze
    analyzer = CraftAnalyzer(tarkov_data)
    crafts = analyzer.analyze_crafts()
    
    # 4. Schedule (Example scenarios)
    scheduler = Scheduler(crafts)
    stations = set(c['station'] for c in crafts)
    
    schedules = {}
    for station in stations:
        schedules[station] = {
            '2h': scheduler.suggest_queue(2, station),
            '4h': scheduler.suggest_queue(4, station),
            '8h': scheduler.suggest_queue(8, station)
        }

    # 5. Export for Dashboard
    dashboard_data = {
        'crafts': crafts,
        'schedules': schedules,
        'timestamp': 'Just now' # You could add real timestamp
    }
    
    js_output = os.path.join(base_dir, 'data.js')
    os.makedirs(os.path.dirname(js_output), exist_ok=True)
    
    with open(js_output, 'w', encoding='utf-8') as f:
        f.write(f"window.dashboardData = {json.dumps(dashboard_data, indent=4)};")
        
    print(f"Dashboard data written to {js_output}")

if __name__ == "__main__":
    main()
