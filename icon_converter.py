# icon_converter.py
# Tool to convert PNG/JPG images to proper icon format for Windows and macOS

import os
import sys
import subprocess
from PIL import Image

def create_windows_icon(input_image, output_icon="app_icon.ico", sizes=[16, 32, 48, 64, 128, 256]):
    """
    Convert an image to Windows ICO format with multiple sizes
    """
    print(f"Converting {input_image} to Windows icon...")
    img = Image.open(input_image)
    
    # Create a multi-size icon
    img.save(output_icon, format='ICO', sizes=[(size, size) for size in sizes])
    print(f"Windows icon created: {output_icon}")

def create_macos_icon(input_image, output_iconset="icon.iconset", output_icon="app_icon.icns"):
    """
    Convert an image to macOS ICNS format
    Note: This works only on macOS as it requires 'sips' and 'iconutil'
    """
    if sys.platform != 'darwin':
        print("Error: macOS icon creation is only available on macOS.")
        return
    
    print(f"Converting {input_image} to macOS icon...")
    
    # Create iconset directory
    os.makedirs(output_iconset, exist_ok=True)
    
    # Generate different icon sizes
    sizes = [16, 32, 64, 128, 256, 512, 1024]
    for size in sizes:
        subprocess.run([
            "sips", "-z", str(size), str(size),
            input_image, "--out", f"{output_iconset}/icon_{size}x{size}.png"
        ])
        
        # For Retina/HiDPI (2x) versions
        if size <= 512:  # 1024px is already the 2x version of 512px
            subprocess.run([
                "sips", "-z", str(size*2), str(size*2),
                input_image, "--out", f"{output_iconset}/icon_{size}x{size}@2x.png"
            ])
    
    # Create ICNS file from iconset
    subprocess.run(["iconutil", "-c", "icns", output_iconset])
    
    # Cleanup the iconset directory if successful
    if os.path.exists(output_icon):
        import shutil
        shutil.rmtree(output_iconset)
        print(f"macOS icon created: {output_icon}")
    else:
        print("Warning: ICNS file creation may have failed.")

def optimize_png_for_app(input_image, output_image=None, app_icon_size=256):
    """
    Optimize a PNG for application icons by ensuring proper dimensions and format
    """
    if output_image is None:
        # Use the same name but ensure .png extension
        name, ext = os.path.splitext(input_image)
        output_image = f"{name}.png"
    
    print(f"Optimizing {input_image} for application icon...")
    
    # Open and resize the image
    img = Image.open(input_image)
    
    # Create a square canvas with transparent background
    size = max(img.width, img.height)
    new_img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    
    # Paste the original image in the center
    paste_pos = ((size - img.width) // 2, (size - img.height) // 2)
    new_img.paste(img, paste_pos)
    
    # Resize to the final size
    new_img = new_img.resize((app_icon_size, app_icon_size), Image.LANCZOS)
    
    # Save the optimized image
    new_img.save(output_image, format="PNG")
    print(f"Optimized icon saved to {output_image}")
    
    return output_image

def main():
    # Check for command line arguments
    if len(sys.argv) > 1:
        input_image = sys.argv[1]
    else:
        # Try common icon names
        possible_icons = ["app_icon.png", "logo.png", "icon.png", "zenia_logo.png"]
        found = False
        
        for icon in possible_icons:
            if os.path.exists(icon):
                input_image = icon
                found = True
                break
        
        if not found:
            print("Error: No input image specified.")
            print("Usage: python icon_converter.py [input_image]")
            print("Or place an image named app_icon.png, logo.png, or icon.png in the current directory.")
            return
    
    # Check if the input file exists
    if not os.path.exists(input_image):
        print(f"Error: Input file '{input_image}' not found.")
        return
    
    # Optimize the image first
    optimized_image = optimize_png_for_app(input_image)
    
    # Create Windows icon
    try:
        create_windows_icon(optimized_image)
    except Exception as e:
        print(f"Error creating Windows icon: {e}")
    
    # Create macOS icon if on macOS
    if sys.platform == 'darwin':
        try:
            create_macos_icon(optimized_image)
        except Exception as e:
            print(f"Error creating macOS icon: {e}")
    
    print("Icon conversion complete!")

if __name__ == "__main__":
    main()