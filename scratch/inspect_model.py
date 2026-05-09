import torch
try:
    state_dict = torch.load('polskie_znaki_model_92.pth', map_location='cpu')
    for k, v in state_dict.items():
        print(f"{k}: {v.shape}")
except Exception as e:
    print(f"Error: {e}")
