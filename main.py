import tkinter as tk
import time
from pynput import keyboard

MAX_TIME = 15.0

root = tk.Tk()
root.title("X-4K")
root.geometry("280x190")
root.attributes("-topmost", True)
root.resizable(False, False)

running = False
m_held = False
start_time = 0.0
listener = None

tk.Label(
    root, text="X-4K",
    font=("Arial", 18, "bold")
).pack(pady=10)

timer_label = tk.Label(
    root, text="Süre: 0.0 / 15.0 sn",
    font=("Arial", 12)
)
timer_label.pack(pady=5)

status_label = tk.Label(
    root, text="Durum: Hazır",
    font=("Arial", 10)
)
status_label.pack(pady=5)

test_window = tk.Toplevel(root)
test_window.title("Test Penceresi")
test_window.geometry("280x100")

test_status = tk.Label(
    test_window,
    text="TEST: DEVAM EDİYOR",
    font=("Arial", 11)
)
test_status.pack(expand=True)


def start_test():
    global running, start_time

    if running:
        return

    running = True
    start_time = time.monotonic()

    status_label.config(text="Durum: Simülasyon başladı")
    test_status.config(text="TEST: DURAKLATILMIŞ GİBİ")
    update_timer()


def stop_test(message="Devam ediyor"):
    global running

    if not running:
        return

    running = False
    status_label.config(text=f"Durum: {message}")
    test_status.config(text="TEST: DEVAM EDİYOR")


def update_timer():
    if not running:
        return

    elapsed = time.monotonic() - start_time

    if elapsed >= MAX_TIME:
        timer_label.config(text="Süre: 15.0 / 15.0 sn")
        stop_test("15 saniye doldu")
        return

    timer_label.config(
        text=f"Süre: {elapsed:.1f} / 15.0 sn"
    )

    root.after(50, update_timer)


def on_press(key):
    global m_held

    try:
        if key.char and key.char.lower() == "m" and not m_held:
            m_held = True
            root.after(0, start_test)
    except AttributeError:
        pass


def on_release(key):
    global m_held

    try:
        if key.char and key.char.lower() == "m":
            m_held = False
            root.after(0, stop_test, "M bırakıldı")
    except AttributeError:
        pass


def close_app():
    listener.stop()
    root.destroy()


listener = keyboard.Listener(
    on_press=on_press,
    on_release=on_release
)
listener.start()

root.protocol("WM_DELETE_WINDOW", close_app)
root.mainloop()
