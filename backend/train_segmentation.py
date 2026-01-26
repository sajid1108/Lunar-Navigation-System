import os
import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import time

# --- CONFIGURATION ---
DATA_DIR = "processed_data/member2_seg"
MODEL_SAVE_PATH = "lunar_unet_model.pth"
BATCH_SIZE = 16
LEARNING_RATE = 0.0001
EPOCHS = 50

# --- DATASET ---
class LunarDataset(Dataset):
    def __init__(self, images_dir, masks_dir):
        self.images_dir = images_dir
        self.masks_dir = masks_dir
        self.images = sorted(os.listdir(images_dir))

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        img_name = self.images[idx]
        img_path = os.path.join(self.images_dir, img_name)
        mask_path = os.path.join(self.masks_dir, img_name)

        image = cv2.imread(img_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = image / 255.0
        image = np.transpose(image, (2, 0, 1))
        
        mask = cv2.imread(mask_path, 0)
        
        return torch.tensor(image, dtype=torch.float32), torch.tensor(mask, dtype=torch.long)

# --- U-NET ARCHITECTURE (MATCHING COLAB WEIGHTS) ---
class SimpleUNet(nn.Module):
    def __init__(self, n_class):
        super().__init__()
        # MATCHING KEYS: enc1, enc2, bottleneck, dec1, dec2, head
        self.enc1 = self.conv(3, 64)
        self.enc2 = self.conv(64, 128)
        self.pool = nn.MaxPool2d(2)
        self.bottleneck = self.conv(128, 256)
        self.up1 = nn.ConvTranspose2d(256, 128, 2, 2)
        self.dec1 = self.conv(256, 128)
        self.up2 = nn.ConvTranspose2d(128, 64, 2, 2)
        self.dec2 = self.conv(128, 64)
        self.head = nn.Conv2d(64, n_class, 1) # Was 'out', now 'head'

    def conv(self, i, o):
        return nn.Sequential(
            nn.Conv2d(i, o, 3, padding=1), nn.ReLU(inplace=True),
            nn.Conv2d(o, o, 3, padding=1), nn.ReLU(inplace=True)
        )

    def forward(self, x):
        e1 = self.enc1(x)
        p1 = self.pool(e1)
        e2 = self.enc2(p1)
        p2 = self.pool(e2)
        
        b = self.bottleneck(p2)
        
        u1 = self.up1(b)
        # Fix dimensions if needed (simple concat for 256x256)
        d1 = self.dec1(torch.cat([u1, e2], dim=1))
        
        u2 = self.up2(d1)
        d2 = self.dec2(torch.cat([u2, e1], dim=1))
        
        return self.head(d2)

# --- TRAINING LOOP (If needed locally) ---
def main():
    print(f"--- 🚀 INITIALIZING TRAINING ---")
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    img_dir = os.path.join(DATA_DIR, "images")
    mask_dir = os.path.join(DATA_DIR, "masks")
    
    dataset = LunarDataset(img_dir, mask_dir)
    loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)
    
    model = SimpleUNet(n_class=3).to(device)
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
    criterion = nn.CrossEntropyLoss()

    for epoch in range(EPOCHS):
        model.train()
        for images, masks in loader:
            images = images.to(device)
            masks = masks.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, masks)
            loss.backward()
            optimizer.step()
        print(f"Epoch {epoch+1} Complete")
        torch.save(model.state_dict(), MODEL_SAVE_PATH)

if __name__ == "__main__":
    main()