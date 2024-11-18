from PIL import Image
import os

# Define the directory containing the images and the output directory within the project structure
project_directory = os.path.dirname(os.path.abspath(__file__))
image_directory = os.path.join(project_directory, "input_images")
output_directory = os.path.join(project_directory, "output_images")

# Ensure the input and output directories exist
os.makedirs(image_directory, exist_ok=True)
os.makedirs(output_directory, exist_ok=True)

# Define the color and size for the background (square with hex color #CFCFCF)
background_color = (233, 234, 236)
background_size = (400, 400)  # Example size, can be adjusted

# Function to process each image
def process_image(image_name):
    book_cover_path = os.path.join(image_directory, image_name)
    book_cover = Image.open(book_cover_path)
    
    # Create a new image with the defined background color
    output_image = Image.new("RGB", background_size, background_color)
    
    # Calculate the position to paste the book cover (centered)
    book_width, book_height = book_cover.size
    x = (background_size[0] - book_width) // 2
    y = (background_size[1] - book_height) // 2
    
    # Paste the book cover onto the background
    output_image.paste(book_cover, (x, y))
    
    # Save the output image
    output_image_path = os.path.join(output_directory, f"centered_{image_name}")
    output_image.save(output_image_path)

# Iterate over all PNG files in the directory
for image_name in os.listdir(image_directory):
    if image_name.endswith(".png"):
        process_image(image_name)

print("All images have been processed and saved.")
