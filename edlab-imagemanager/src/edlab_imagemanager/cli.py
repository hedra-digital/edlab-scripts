#!/usr/bin/env python3

import argparse
from PIL import Image, ImageOps
import os
import glob

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def add_border(image, border_width, color):
    return ImageOps.expand(image, border=border_width, fill=color)

def process_image(input_path, output_directory, args):
    with Image.open(input_path) as img:
        if args.square:
            # Criar imagem quadrada
            background_color = hex_to_rgb(args.background_color)
            background_size = (400, 400)
            img_with_border = add_border(img, args.border_width, "black")
            
            output_image = Image.new("RGB", background_size, background_color)
            
            img_width, img_height = img_with_border.size
            x = (background_size[0] - img_width) // 2
            y = (background_size[1] - img_height) // 2
            
            output_image.paste(img_with_border, (x, y))
        else:
            # Apenas adicionar borda
            output_image = add_border(img, args.border_width, "black")
        
        base_name = os.path.basename(input_path)
        output_name = f"{os.path.splitext(base_name)[0]}_{args.suffix}.png"
        
        if output_directory:
            os.makedirs(output_directory, exist_ok=True)
            output_path = os.path.join(output_directory, output_name)
        else:
            output_path = os.path.join(os.path.dirname(input_path), output_name)
        
        output_image.save(output_path)
        print(f"Processed: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Process images with various options.")
    parser.add_argument("input", nargs="*", help="Input image file(s) or wildcard pattern")
    parser.add_argument("-i", "--input-dir", help="Input directory for images")
    parser.add_argument("-o", "--output-dir", help="Output directory for processed images")
    parser.add_argument("-b", "--border-width", type=int, default=0, help="Width of the black border (default: 0)")
    parser.add_argument("-s", "--square", action="store_true", help="Create a square image with centered content")
    parser.add_argument("--suffix", default="new", help="Suffix for processed images (default: 'new')")
    parser.add_argument("--background-color", default="#E9EAEC", help="Background color in hex format (default: #E9EAEC)")
    
    args = parser.parse_args()

    project_directory = os.path.dirname(os.path.abspath(__file__))
    
    if args.input_dir:
        input_directory = args.input_dir
    else:
        input_directory = os.path.join(project_directory, "input_images")
    
    output_directory = args.output_dir

    if args.input:
        for pattern in args.input:
            if os.path.isfile(pattern):
                # Single file processing
                if pattern.lower().endswith(('.png', '.jpg', '.jpeg')):
                    process_image(pattern, output_directory, args)
            else:
                # Wildcard pattern processing
                for input_path in glob.glob(pattern):
                    if input_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                        process_image(input_path, output_directory, args)
    else:
        # Process all files in the input directory
        for image_name in os.listdir(input_directory):
            if image_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                input_path = os.path.join(input_directory, image_name)
                process_image(input_path, output_directory, args)

    print("All images have been processed and saved.")

if __name__ == "__main__":
    main()