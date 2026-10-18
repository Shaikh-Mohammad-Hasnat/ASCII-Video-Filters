from PIL import Image
import numpy as np

def image_to_dot_grid(image_path, grid_size=80, threshold=128):
    """
    Convert an image to an 80x80 grid of dots and blanks.
    
    Args:
        image_path: Path to the image file
        grid_size: Size of the grid (default 80x80)
        threshold: Brightness threshold (0-255). Values below this show as dots
    """
    
    # Open and convert image to grayscale
    img = Image.open(image_path).convert('L')
    
    # Resize to 80x80
    img_resized = img.resize((grid_size, grid_size), Image.Resampling.LANCZOS)
    
    # Convert to numpy array
    img_array = np.array(img_resized)
    
    # Create dot grid (. for dark pixels, space for light pixels)
    dot_grid = []
    for row in img_array:
        line = ''.join('.' if pixel < threshold else ' ' for pixel in row)
        dot_grid.append(line)
    
    return dot_grid


def print_grid(dot_grid):
    """Print the dot grid to console"""
    for line in dot_grid:
        print(line)


def save_grid_to_file(dot_grid, output_file):
    """Save the dot grid to a text file"""
    with open(output_file, 'w') as f:
        f.write('\n'.join(dot_grid))
    print(f"Grid saved to {output_file}")


if __name__ == "__main__":
    # Convert the image
    image_path = "Gray_img.png"
    dot_grid = image_to_dot_grid(image_path, grid_size=180, threshold=128)
    
    # Print to console
    print("180x180 Dot Grid Representation:")
    print("=" * 180)
    print_grid(dot_grid)

    print("=" * 180)
    
    # Save to file
    save_grid_to_file(dot_grid, "image_dots.txt")
