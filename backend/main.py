from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import cv2
import torch
import torch.nn as nn
import numpy as np
import os
import base64
from scipy.ndimage import binary_dilation
import heapq

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODEL ARCHITECTURES ---
class ResidualBlock(nn.Module):
    def __init__(self, c):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(c, c, 3, 1, 1), nn.BatchNorm2d(c), nn.PReLU(),
            nn.Conv2d(c, c, 3, 1, 1), nn.BatchNorm2d(c)
        )
    def forward(self, x): return x + self.conv(x)

class SRResNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.head = nn.Sequential(nn.Conv2d(3, 64, 9, 1, 4), nn.PReLU())
        self.body = nn.Sequential(*[ResidualBlock(64) for _ in range(5)])
        self.tail = nn.Sequential(
            nn.Conv2d(64, 256, 3, 1, 1), nn.PixelShuffle(2), nn.PReLU(),
            nn.Conv2d(64, 256, 3, 1, 1), nn.PixelShuffle(2), nn.PReLU(),
            nn.Conv2d(64, 3, 9, 1, 4)
        )
    def forward(self, x):
        x = self.head(x)
        res = self.body(x)
        return self.tail(x + res)

class SimpleUNet(nn.Module):
    def __init__(self, n_class):
        super().__init__()
        self.enc1 = self.conv(3, 64)
        self.enc2 = self.conv(64, 128)
        self.pool = nn.MaxPool2d(2)
        self.bottleneck = self.conv(128, 256)
        self.up1 = nn.ConvTranspose2d(256, 128, 2, 2)
        self.dec1 = self.conv(256, 128)
        self.up2 = nn.ConvTranspose2d(128, 64, 2, 2)
        self.dec2 = self.conv(128, 64)
        self.head = nn.Conv2d(64, n_class, 1)
    def conv(self, i, o):
        return nn.Sequential(nn.Conv2d(i, o, 3, padding=1), nn.ReLU(inplace=True), nn.Conv2d(o, o, 3, padding=1), nn.ReLU(inplace=True))
    def forward(self, x):
        e1 = self.enc1(x)
        e2 = self.enc2(self.pool(e1))
        b = self.bottleneck(self.pool(e2))
        d1 = self.dec1(torch.cat([self.up1(b), e2], dim=1))
        d2 = self.dec2(torch.cat([self.up2(d1), e1], dim=1))
        return self.head(d2)

# --- LOAD ---
device = torch.device('cpu')
sr_model = SRResNet()
if os.path.exists("lunar_sr_model_V2.pth"):
    try: sr_model.load_state_dict(torch.load("lunar_sr_model_V2.pth", map_location=device)); sr_model.eval(); print("✅ SR ONLINE")
    except: sr_model = None
else: sr_model = None

unet_model = SimpleUNet(n_class=3)
if os.path.exists("lunar_unet_model.pth"):
    try: unet_model.load_state_dict(torch.load("lunar_unet_model.pth", map_location=device)); unet_model.eval(); print("✅ U-NET ONLINE")
    except: pass

# --- LOGIC ---
def heuristic(a, b): return np.sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2)

def advanced_astar(cost_map, start, goal):
    neighbors = [(0,1),(0,-1),(1,0),(-1,0), (1,1),(1,-1),(-1,1),(-1,-1)]
    gscore = {start: 0}
    fscore = {start: heuristic(start, goal)}
    oheap = []
    heapq.heappush(oheap, (fscore[start], start))
    came_from = {}
    
    while oheap:
        current = heapq.heappop(oheap)[1]
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            return path[::-1]

        for i, j in neighbors:
            neighbor = current[0] + i, current[1] + j
            if not (0 <= neighbor[0] < cost_map.shape[0] and 0 <= neighbor[1] < cost_map.shape[1]): continue
            
            # Physics Cost
            total_cost = cost_map[neighbor[0]][neighbor[1]]
            if total_cost > 0.8: continue 
            
            move_cost = 1 + (total_cost * 100) 
            tentative_g_score = gscore[current] + move_cost
            if neighbor not in gscore or tentative_g_score < gscore[neighbor]:
                came_from[neighbor] = current
                gscore[neighbor] = tentative_g_score
                fscore[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                heapq.heappush(oheap, (fscore[neighbor], neighbor))     
    return []

def smooth_path(path):
    if len(path) < 5: return path
    path = np.array(path)
    smoothed = []
    for i in range(len(path)):
        s = max(0, i - 2); e = min(len(path), i + 3)
        smoothed.append([int(np.mean(path[s:e, 0])), int(np.mean(path[s:e, 1]))])
    return smoothed

def to_base64(img):
    _, buffer = cv2.imencode('.png', img)
    return base64.b64encode(buffer).decode('utf-8')

@app.get("/api/analyze/{sector_id}")
def analyze_sector(sector_id: int):
    filename = f"render{str(sector_id).zfill(4)}.png"
    
    # --- PATHS ---
    path_lr = os.path.join("processed_data", "member1_gan", "lr", filename)
    path_hr = os.path.join("processed_data", "member1_gan", "hr", filename) # <--- NEW: GROUND TRUTH PATH
    
    if not os.path.exists(path_lr): raise HTTPException(status_code=404, detail="Sector Data Not Found")

    # 1. READ INPUT
    low_res_raw = cv2.imread(path_lr)
    
    # 2. ENHANCE (SRResNet)
    if sr_model:
        lr_tensor = cv2.cvtColor(low_res_raw, cv2.COLOR_BGR2RGB).transpose(2,0,1) / 255.0
        lr_tensor = torch.tensor(lr_tensor, dtype=torch.float32).unsqueeze(0)
        with torch.no_grad(): sr_output = sr_model(lr_tensor)
        sr_img = sr_output.squeeze(0).permute(1,2,0).numpy()
        sr_img = np.clip(sr_img * 255, 0, 255).astype(np.uint8)
        img = cv2.cvtColor(sr_img, cv2.COLOR_RGB2BGR)
    else:
        img = cv2.resize(low_res_raw, (256, 256), interpolation=cv2.INTER_CUBIC)

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) 

    # 3. PHYSICS
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    slope_map = np.sqrt(sobelx**2 + sobely**2)
    slope_map = (slope_map - slope_map.min()) / (slope_map.max() - slope_map.min())

    # 4. AI
    input_tensor = torch.tensor(np.transpose(img_rgb/255.0, (2,0,1)), dtype=torch.float32).unsqueeze(0)
    with torch.no_grad():
        out = unet_model(input_tensor)
        probs = torch.softmax(out, dim=1).squeeze(0).numpy()
    risk_map = probs[1]

    cost_map = np.maximum(risk_map, slope_map * 0.5)

    # 5. PATH
    start, goal = (10, 10), (240, 240)
    while cost_map[start] > 0.6: start = (start[0]+1, start[1]+1)
    while cost_map[goal] > 0.6: goal = (goal[0]-1, goal[1]-1)
    
    raw_path = advanced_astar(cost_map, start, goal)
    final_path = smooth_path(raw_path)

    # 6. VISUALS (AI OUTPUT)
    vis_path = img.copy()
    if final_path:
        pts = np.array(final_path)[:, [1, 0]].reshape((-1, 1, 2))
        cv2.polylines(vis_path, [pts], False, (0, 255, 0), 3) # GREEN
        cv2.circle(vis_path, (start[1], start[0]), 4, (255, 0, 0), -1)
        cv2.circle(vis_path, (goal[1], goal[0]), 4, (0, 255, 255), -1)
        
    # --- NEW: GROUND TRUTH VISUAL ---
    if os.path.exists(path_hr):
        vis_gt = cv2.imread(path_hr)
    else:
        vis_gt = cv2.resize(low_res_raw, (256, 256)) # Fallback

    if final_path:
        # Draw path on GT too for comparison
        pts = np.array(final_path)[:, [1, 0]].reshape((-1, 1, 2))
        cv2.polylines(vis_gt, [pts], False, (0, 255, 0), 3)
        cv2.circle(vis_gt, (start[1], start[0]), 4, (255, 0, 0), -1)
        cv2.circle(vis_gt, (goal[1], goal[0]), 4, (0, 255, 255), -1)

    # Heatmap
    norm_cost = (cost_map / cost_map.max() * 255).astype(np.uint8)
    heatmap_color = cv2.applyColorMap(norm_cost, cv2.COLORMAP_JET)

    # Stats
    path_len = len(final_path) * 10
    fuel_est = int(np.sum([slope_map[p[0], p[1]] for p in final_path]) * 100) + path_len if final_path else 0
    safety_score = 100 - int(np.mean([risk_map[p[0], p[1]] for p in final_path]) * 100) if final_path else 0
    
    # Pie Chart Counts
    safe_count = int(np.sum(risk_map < 0.3))
    caution_count = int(np.sum((risk_map >= 0.3) & (risk_map < 0.7)))
    danger_count = int(np.sum(risk_map >= 0.7))

    return {
        "optical_feed": to_base64(vis_path),
        "ground_truth": to_base64(vis_gt), # <--- SENDING GROUND TRUTH
        "heatmap": to_base64(heatmap_color),
        "metrics": { "velocity": "1.63 km/s", "altitude": "12.4 km", "distance": f"{path_len} m", "fuel_cost": f"{fuel_est} kJ", "safety": f"{safety_score}%", "waypoints": len(final_path) },
        "sector_stats": { "safe": safe_count, "caution": caution_count, "danger": danger_count },
        "path_coords": final_path,
        "terrain_z": gray.tolist() 
    }