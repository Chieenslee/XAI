import os
import numpy as np
from PIL import Image
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def generate_dummy_images():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    normal_dir = os.path.join(base_dir, 'sample_dataset', 'normal')
    effusion_dir = os.path.join(base_dir, 'sample_dataset', 'effusion')

    os.makedirs(normal_dir, exist_ok=True)
    os.makedirs(effusion_dir, exist_ok=True)

    def create_dummy_xray(path, text=""):
        # Create a random gray scale image resembling noise
        img_array = np.random.randint(50, 200, (256, 256), dtype=np.uint8)
        
        # Draw some dark areas to simulate lungs
        img_array[50:200, 40:110] = img_array[50:200, 40:110] - 30
        img_array[50:200, 140:210] = img_array[50:200, 140:210] - 30
        
        # If effusion, add a bright area at the bottom of one lung
        if "effusion" in text:
            img_array[150:200, 40:110] = img_array[150:200, 40:110] + 80
            
        img = Image.fromarray(img_array, mode='L')
        img.save(path)

    # Generate 5 normal and 5 effusion dummy images
    for i in range(1, 6):
        normal_path = os.path.join(normal_dir, f"normal_{i}.jpg")
        effusion_path = os.path.join(effusion_dir, f"effusion_{i}.jpg")
        
        create_dummy_xray(normal_path, "normal")
        create_dummy_xray(effusion_path, "effusion")
        
    logging.info("Generated 5 normal and 5 effusion dummy X-ray images.")

if __name__ == "__main__":
    generate_dummy_images()
