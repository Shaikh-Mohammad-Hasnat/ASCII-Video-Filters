import customtkinter as ctk
import cv2
import numpy as np
from PIL import Image
import threading
import time
import os
from datetime import datetime

# ── ASCII config ──────────────────────────────────────────────
CHARS = "  .'`^\",:;Il!i><~+_-?][}{1)(|\\/*#ht&8%B@$"
SCALE = 9

COLOR_MAP = {
    "Cyan":    (255, 255,   0),
    "White":   (255, 255, 255),
    "Green":   (  0, 255,   0),
    "Red":     (  0,   0, 255),
    "Yellow":  (  0, 255, 255),
    "Magenta": (255,   0, 255),
    "Blue":    (255,   0,   0),
}

# ── Globals ───────────────────────────────────────────────────
cap           = None
running       = False
last_frame    = None
frame_lock    = threading.Lock()
current_color = "Cyan"
canvas_w      = 1440
canvas_h      = 900

# ── Widgets (filled in build_ui) ──────────────────────────────
root          = None
video_label   = None
status_label  = None
save_label    = None

# ── Camera helpers ────────────────────────────────────────────
def open_camera(index: int):
    global cap, running
    if cap and cap.isOpened():
        cap.release()
    cap = cv2.VideoCapture(index)
    ok  = cap.isOpened()
    running = ok
    if status_label:
        status_label.configure(
            text="● LIVE" if ok else "✖ NO CAM",
            text_color="#00ff88" if ok else "#ff4444",
        )

def switch_camera(value: str):
    global running
    idx = int(value.split()[1])
    running = False
    time.sleep(0.08)
    open_camera(idx)

def change_color(value: str):
    global current_color
    current_color = value

# ── Capture thread ────────────────────────────────────────────
def capture_loop():
    global last_frame
    while True:
        if running and cap and cap.isOpened():
            suc, frame = cap.read()
            if suc:
                with frame_lock:
                    last_frame = frame
        time.sleep(0.033)

# ── ASCII renderer ────────────────────────────────────────────
def frame_to_ascii_image(frame, out_w: int, out_h: int) -> Image.Image:
    cols = max(out_w  // SCALE, 1)
    rows = max(out_h  // SCALE, 1)

    gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    small = cv2.resize(gray, (cols, rows))
    small = cv2.flip(small, 1)

    canvas = np.zeros((rows * SCALE, cols * SCALE, 3), dtype=np.uint8)
    color  = COLOR_MAP[current_color]

    for y in range(rows):
        for x in range(cols):
            brightness = int(small[y, x])
            idx  = int(brightness / 255 * (len(CHARS) - 1))
            char = CHARS[idx]
            cv2.putText(
                canvas, char,
                (x * SCALE, y * SCALE + SCALE - 2),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.28, color, 1, cv2.LINE_AA,
            )

    rgb = cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB)
    
    return Image.fromarray(rgb)

# ── Display loop (runs on main thread via after) ──────────────
def update_display():
    with frame_lock:
        frame = last_frame.copy() if last_frame is not None else None

    if frame is not None:
        img     = frame_to_ascii_image(frame, canvas_w, canvas_h)
        ctk_img = ctk.CTkImage(light_image=img, dark_image=img,
                                size=(canvas_w, canvas_h))
        video_label.configure(image=ctk_img)
        video_label._image = ctk_img  # prevent GC

    root.after(33, update_display)

def on_resize(event):
    global canvas_w, canvas_h
    canvas_w = max(event.width  // SCALE, 40) * SCALE
    canvas_h = max(event.height // SCALE, 30) * SCALE

# ── Capture image ─────────────────────────────────────────────
def capture_image():
    with frame_lock:
        frame = last_frame.copy() if last_frame is not None else None

    if frame is None:
        save_label.configure(text="No frame!", text_color="#ff4444")
        return

    img = frame_to_ascii_image(frame, canvas_w, canvas_h)
    ts  = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs("captures", exist_ok=True)
    path = f"captures/ascii_{ts}.png"
    img.save(path)
    save_label.configure(text=f"Saved → {path}", text_color="#00ff88")
    root.after(3000, lambda: save_label.configure(text=""))

# ── Cleanup ───────────────────────────────────────────────────
def on_close():
    global running
    running = False
    time.sleep(0.1)
    if cap:
        cap.release()
    root.destroy()

# ── UI builder ────────────────────────────────────────────────
def build_ui():
    global root, video_label, status_label, save_label

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("ASCII Webcam")
    root.geometry("1460x900")
    root.resizable(True, True)
    root.protocol("WM_DELETE_WINDOW", on_close)

    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=0)   # top bar
    root.rowconfigure(1, weight=1)   # video
    root.rowconfigure(2, weight=0)   # bottom bar

    # ── Top bar ──────────────────────────────────────────────
    top = ctk.CTkFrame(root, corner_radius=0, fg_color="#1a1a2e")
    top.grid(row=0, column=0, sticky="ew")
    top.columnconfigure((0, 1, 2, 3), weight=1)

    ctk.CTkLabel(
        top, text="🎥  ASCII WEBCAM",
        font=ctk.CTkFont(size=18, weight="bold"),
        text_color="#00d4ff",
    ).grid(row=0, column=0, padx=20, pady=10, sticky="w")

    ctk.CTkLabel(top, text="Camera:", text_color="#aaaaaa").grid(
        row=0, column=1, padx=(10, 0), pady=10, sticky="e"
    )

    cam_menu = ctk.CTkOptionMenu(
        top,
        values=["Camera 0 (Primary)", "Camera 1 (Secondary)", "Camera 2 (Tertiary)"],
        command=switch_camera,
        width=185,
        fg_color="#16213e",
        button_color="#0f3460",
    )
    cam_menu.grid(row=0, column=2, padx=10, pady=10)

    status_label = ctk.CTkLabel(
        top, text="● LIVE",
        text_color="#00ff88",
        font=ctk.CTkFont(size=13, weight="bold"),
    )
    status_label.grid(row=0, column=3, padx=20, pady=10, sticky="e")

    # ── Video area ────────────────────────────────────────────
    video_label = ctk.CTkLabel(root, text="", fg_color="#000000")
    video_label.grid(row=1, column=0, sticky="nsew")
    video_label.bind("<Configure>", on_resize)

    # ── Bottom bar ────────────────────────────────────────────
    bot = ctk.CTkFrame(root, corner_radius=0, fg_color="#1a1a2e")
    bot.grid(row=2, column=0, sticky="ew")
    bot.columnconfigure((0, 1, 2, 3, 4), weight=1)

    ctk.CTkLabel(bot, text="ASCII Color:", text_color="#aaaaaa").grid(
        row=0, column=1, padx=(10, 0), pady=12, sticky="e"
    )

    color_menu = ctk.CTkOptionMenu(
        bot,
        values=list(COLOR_MAP.keys()),
        command=change_color,
        width=140,
        fg_color="#16213e",
        button_color="#0f3460",
    )
    color_menu.set("Cyan")
    color_menu.grid(row=0, column=2, padx=10, pady=12)

    ctk.CTkButton(
        bot,
        text="📷  Capture",
        command=capture_image,
        width=140,
        height=38,
        fg_color="#0f3460",
        hover_color="#1a5276",
        font=ctk.CTkFont(size=14, weight="bold"),
    ).grid(row=0, column=3, padx=10, pady=12)

    save_label = ctk.CTkLabel(bot, text="", text_color="#00ff88",
                               font=ctk.CTkFont(size=11))
    save_label.grid(row=0, column=4, padx=10, pady=12, sticky="w")

# ── Entry point ───────────────────────────────────────────────
build_ui()
open_camera(0)

thread = threading.Thread(target=capture_loop, daemon=True)
thread.start()

update_display()
root.mainloop()