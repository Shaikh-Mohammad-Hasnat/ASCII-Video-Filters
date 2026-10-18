import cv2
import numpy as np

# ASCII characters from dark to light
ASCII_CHARS = "@%#*+=-:. "

def pixel_to_ascii(pixel_value):
    """Map a pixel brightness (0-255) to an ASCII character."""
    index = int(pixel_value / 255 * (len(ASCII_CHARS) - 1))
    return ASCII_CHARS[index]

def frame_to_ascii_image(frame, char_width=200):
    """Convert a frame to an ASCII art image (rendered as cv2 image)."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray=cv2.flip(gray,1)

    # Calculate char height to maintain aspect ratio (chars are ~2x taller than wide)
    h, w = gray.shape
    char_height = int(char_width * (h / w) * 1.1)

    # Resize grayscale image to ASCII grid size
    small = cv2.resize(gray, (char_width, char_height))

    # Font settings
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.35
    thickness = 1

    # Get size of a single character cell
    (char_w, char_h), baseline = cv2.getTextSize("A", font, font_scale, thickness)
    cell_w = char_w + 1
    cell_h = char_h + baseline + 1

    # Create output black image
    out_h = char_height * cell_h
    out_w = char_width * cell_w
    output = np.zeros((out_h, out_w, 3), dtype=np.uint8)

    for row in range(char_height):
        for col in range(char_width):
            pixel_val = small[row, col]
            char = pixel_to_ascii(pixel_val)

            # Map brightness to a green color (classic terminal look)
            intensity = int(pixel_val)
            color = (0, intensity, 0)  # BGR: green channel

            x = col * cell_w
            y = row * cell_h + char_h

            cv2.putText(output, char, (x, y), font, font_scale, color, thickness)

    return output


def main():
    cap = cv2.VideoCapture(0)  # Use 0 for webcam, or replace with a video file path

    if not cap.isOpened():
        print("Error: Cannot open camera/video.")
        return

    print("Press 'q' to quit | '+'/'-' to adjust ASCII resolution")

    char_width = 80  # Number of ASCII columns

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        ascii_img = frame_to_ascii_image(frame, char_width=char_width)
        cv2.imshow("ASCII Art", ascii_img)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('+') or key == ord('='):
            char_width = min(char_width + 10, 200)
            print(f"Resolution: {char_width} cols")
        elif key == ord('-'):
            char_width = max(char_width - 10, 20)
            print(f"Resolution: {char_width} cols")

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()