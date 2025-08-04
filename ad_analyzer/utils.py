from PIL import Image
import io

def load_image(uploaded_file):
    image = Image.open(uploaded_file)
    return image.convert("RGB")
