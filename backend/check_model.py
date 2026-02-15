from ultralytics import YOLO
import os

model_path = 'models/best.pt'
print(f'Model path: {os.path.abspath(model_path)}')
print(f'Model exists: {os.path.exists(model_path)}')

model = YOLO(model_path)
print(f'\nModel loaded successfully!')
print(f'Number of classes: {len(model.names)}')
print(f'\nClass names:')
for idx, name in model.names.items():
    print(f'  Class {idx}: {name}')
