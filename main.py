```python
import tkinter as tk
import time
import ctypes
import ctypes.wintypes as wt
from pynput import keyboard
from pynput.mouse import Controller as MouseController, Button

MAX_TIME = 15.0
user32 = ctypes.windll.user32
mouse = MouseController()

running = m_held = x_held = False
start_time = 0.0
target_hwnd = None
saved_pos = (0, 0)

def get_window_rect(hwnd):
    r = wt.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(r))
    return r.left, r.top, r.right, r.bottom

def get_window_title(hwnd):
    n = user32.GetWindowTextLengthW(hwnd)
    b = ctypes.create_unicode_buffer(n + 1)
    user32.GetWindowTextW(hwnd, b, n + 1)
    return b.value

def list_windows():
    out = []
    P = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
    def cb(h, l):
        if user32.IsWindowVisible(h):
            t = get_window_title(h)
            if t.strip():
                out.append((h, t))
        return True
    user32.EnumWindows(P(cb), 0)
    return out

root = tk.Tk()
root.title("X-4K")
root.geometry("320x230")
root.attributes("-topmost", True)
root.resizable(False, False)

tk.Label(root, text="X-4K", font=("Arial", 20, "bold")).pack(pady=(8, 2))
target_label = tk.Label(root, text="Hedef: (seçilmedi)", font=("Arial", 9), fg="blue")
target_label.pack(pady=2)
timer_label = tk.Label(root, text="0.0 / 15.0 s", font=("Arial", 14))
timer_label.pack(pady=2)
status_label = tk.Label(root, text="READY", font=("Arial", 10))
status_label.pack(pady=2)

def open_selector():
    sel = tk.Toplevel(root)
    sel.title("Uygulama Seç")
    sel.geometry("400x400")
    sel.attributes("-topmost", True)
    lb = tk.Listbox(sel, font=("Arial", 10))
    lb.pack(fill="both", expand=True, padx=6, pady=6)
    ws = list_windows()
    for _, t in ws:
        lb.insert("end", t)
    def choose():
        global target_hwnd
        i = lb.curselection()
        if not i:
            return
        target_hwnd = ws[i[0]][0]
        target_label.config(text=f"Hedef: {ws[i[0]][1][:35]}")
        sel.destroy()
    tk.Button(sel, text="Seç", command=choose).pack(pady=6)
    lb.bind("<Double-Button-1>", lambda e: choose())

tk.Button(root, text="Uygulama Seç", command=open_selector).pack(pady=4)

def press_target_x():
    global x_held, saved_pos
    if target_hwnd is None or x_held:
        return
    _, t, r, _ = get_window_rect(target_hwnd)
    saved_pos = mouse.position
    mouse.position = (r - 30, t + 15)
    mouse.press(Button.left)
    x_held = True

def release_target_x_safely():
    global x_held
    if not x_held:
        return
    cx, cy = mouse.position
    mouse.position = (cx - 50, cy)
    mouse.release(Button.left)
    mouse.position = saved_pos
    x_held = False

def start_timer():
    global running, start_time
    if running:
        return
    if target_hwnd is None:
        status_label.config(text="ÖNCE UYGULAMA SEÇ", fg="red")
        return
    running = True
    start_time = time.monotonic()
    status_label.config(text="ACTIVE", fg="green")
    press_target_x()
    update_timer()

def stop_timer():
    global running
    if not running:
        return
    running = False
    status_label.config(text="READY", fg="black")
    release_target_x_safely()

def update_timer():
    if not running:
        return
    e = time.monotonic() - start_time
    if e >= MAX_TIME:
        timer_label.config(text=f"{MAX_TIME:.1f} / {MAX_TIME:.1f} s")
        stop_timer()
        return
    timer_label.config(text=f"{e:.1f} / {MAX_TIME:.1f} s")
    root.after(50, update_timer)

def on_press(key):
    global m_held
    try:
        if key.char and key.char.lower() == "m" and not m_held:
            m_held = True
            root.after(0, start_timer)
    except AttributeError:
        pass

def on_release(key):
    global m_held
    try:
        if key.char and key.char.lower() == "m":
            m_held = False
            root.after(0, stop_timer)
    except AttributeError:
        pass

def close_app():
    release_target_x_safely()
    listener.stop()
    root.destroy()

listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()
root.protocol("WM_DELETE_WINDOW", close_app)
root.mainloop()
```
