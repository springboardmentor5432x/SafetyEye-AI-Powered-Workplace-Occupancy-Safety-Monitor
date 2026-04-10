import os
import csv
import glob

best_map = -1
best_model = None

with open('best_model.txt', 'w') as out_f:
    out_f.write("Analyzing all training results...\n")
    for f in glob.glob('runs/detect/*/results.csv'):
        try:
            with open(f, 'r') as file:
                reader = csv.reader(file)
                header = next(reader)
                headers = [h.strip() for h in header]
                
                map_idx = 6
                for i, h in enumerate(headers):
                    if 'map50' in h.lower() and '95' not in h.lower():
                        map_idx = i
                        break
                
                maps = []
                for row in reader:
                    if len(row) > map_idx and row[map_idx].strip():
                        try:
                            maps.append(float(row[map_idx]))
                        except:
                            pass
                
                if maps:
                    max_map = max(maps)
                    folder = os.path.dirname(f)
                    weights_path = os.path.join(folder, 'weights', 'best.pt')
                    
                    if os.path.exists(weights_path):
                        out_f.write(f"{folder}: Max mAP50 = {max_map:.4f} (Found best.pt)\n")
                        if max_map > best_map:
                            best_map = max_map
                            best_model = weights_path.replace("\\", "/")
                    else:
                        out_f.write(f"{folder}: Max mAP50 = {max_map:.4f} (WARNING: No best.pt found!)\n")
                        
        except Exception as e:
            out_f.write(f"Error reading {f}: {e}\n")

    if best_model:
        out_f.write(f"\nWINNER|{best_model}|{best_map:.4f}")
    else:
        out_f.write("\nWINNER|NONE|0")
