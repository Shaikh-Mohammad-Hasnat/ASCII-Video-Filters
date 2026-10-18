# ASCII Video Filters

Turn a webcam feed or a video into live ASCII art, plus a small set of image filters, with CustomTkinter GUIs.

## What's inside

| File | What it does |
|---|---|
| `Ascii_video_ctk.py` | **ASCII Webcam** GUI. Pick a camera, pick the ASCII colour, and press Capture to save the current ASCII frame as a PNG. |
| `ascii_vid.py` | Webcam to ASCII in an OpenCV window. |
| `ascii_player.py` | Plays `video.mp4` as ASCII (put your own clip next to the script). Steps: open the video, convert to grayscale and resize, draw each pixel as a character from a brightness ramp on a blank canvas. |
| `Video_filter_ctk.py` | Webcam filter GUI: negative, thresholding, contrast stretching, Laplacian, noise, histogram equalization and more. |
| `image_to_dots.py` | Converts an image to an 80×80 grid of dots and blanks, thresholded by brightness. |
| `samples/` | Example captures from the ASCII Webcam GUI. |

## How the ASCII conversion works

The brightness of each (downscaled) pixel picks a character from a ramp. The command-line scripts use a short one, `@%#*+=-:. `, and the GUI uses a longer ramp of about 40 characters for finer shading. Dense characters stand for one end of the brightness range and sparse ones for the other. The characters are drawn onto a canvas with OpenCV, so each output frame is again an image.

## Run it

```bash
pip install opencv-python numpy pillow customtkinter
python Ascii_video_ctk.py
```

`SCALE` at the top of the file sets how many source pixels become one character. A larger value gives a faster, coarser picture.

## Related
- [OpenCV-Vision-Lab](https://github.com/Shaikh-Mohammad-Hasnat/OpenCV-Vision-Lab) for other real-time vision apps.

## Author
Shaikh Mohammad Hasnat, [GitHub](https://github.com/Shaikh-Mohammad-Hasnat)
