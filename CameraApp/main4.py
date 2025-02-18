import tkinter as tk
from tkinter import messagebox
import subprocess
import datetime
import os
import threading
import time

cams = [
    "rtsp://admin:Embedlab38.@192.168.100.10:554",
    "rtsp://admin:Embedlab38.@192.168.100.11:554",
    "rtsp://admin:Embedlab38.@192.168.100.12:554",
    "rtsp://admin:Embedlab38.@192.168.100.13:554",
    "rtsp://admin:Embedlab38.@192.168.100.14:554",
]

output_dir = "kayitlar"
processes = []
start_time = None
timer_running = False


def start_timer():
    global timer_running, start_time
    timer_running = True
    start_time = time.time()
    update_timer()


def stop_timer():
    global timer_running
    timer_running = False


def update_timer():
    if timer_running:
        elapsed_time = int(time.time() - start_time)
        mins, secs = divmod(elapsed_time, 60)
        time_formatted = f"{mins:02}:{secs:02}"
        timer_label.config(text=f"Kayıt Süresi: {time_formatted}")
        window.after(1000, update_timer)


def start_recording():
    global processes
    if processes:
        messagebox.showwarning("Uyarı", "Kayıt zaten devam ediyor.")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    for idx, cam in enumerate(cams):
        output_file = f"{output_dir}/kamera{idx+1}_{timestamp}.mp4"
        cmd = [
            "ffmpeg", "-rtsp_transport", "tcp", "-i", cam, "-c", "copy", "-loglevel", "error", output_file
        ]
        p = subprocess.Popen(cmd)
        processes.append(p)

    start_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)
    status_label.config(text="Kayıt Durumu: Aktif")
    messagebox.showinfo("Bilgi", "Kayıt başlatıldı.")
    start_timer()


def stop_recording():
    global processes
    if not processes:
        messagebox.showwarning("Uyarı", "Kayıt zaten durduruldu.")
        return

    for p in processes:
        p.terminate()
    processes.clear()

    stop_timer()
    timer_label.config(text="Kayıt Süresi: 00:00")
    start_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)
    status_label.config(text="Kayıt Durumu: Durduruldu")
    messagebox.showinfo("Bilgi", "Kayıt durduruldu.")


window = tk.Tk()
window.title("Kamera Kayıt Kontrolü")
window.geometry("400x250")

start_button = tk.Button(window, text="Kaydı Başlat", width=20, command=start_recording)
start_button.pack(pady=10)

stop_button = tk.Button(window, text="Kaydı Durdur", width=20, state=tk.DISABLED, command=stop_recording)
stop_button.pack(pady=10)

status_label = tk.Label(window, text="Kayıt Durumu: Durduruldu", font=("Helvetica", 12))
status_label.pack(pady=10)

timer_label = tk.Label(window, text="Kayıt Süresi: 00:00", font=("Helvetica", 12))
timer_label.pack(pady=10)

window.grid_rowconfigure(0, weight=1)
window.grid_columnconfigure(0, weight=1)

window.mainloop()
