from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import torch

processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")

def describe_image(image: Image.Image):
    prompts = [
        "an image of a smiling person",
        "an image with a lot of text",
        "an image with vibrant colors",
        "an image with product packaging",
        "an emotional photo",
        "a boring or empty image"
    ]
    
    inputs = processor(text=prompts, images=image, return_tensors="pt", padding=True)
    outputs = model(**inputs)
    logits_per_image = outputs.logits_per_image
    probs = logits_per_image.softmax(dim=1).detach().numpy()[0]

    top_prompt = prompts[probs.argmax()]
    return top_prompt, dict(zip(prompts, probs))
