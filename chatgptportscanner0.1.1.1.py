import tkinter as tk
from tkinter import scrolledtext
import socket
import threading
import queue
import concurrent.futures

# ----------------------------
# CONFIG
# ----------------------------
PORT_RANGE = (1, 1024)
TIMEOUT = 0.08

# ----------------------------
# THREAD SAFE OUTPUT QUEUE
# ----------------------------
q = queue.Queue()
scanning = False


def scan_ports():
    global scanning
    if scanning:
        return

    target = entry.get().strip()
    if not target:
        q.put("Enter a target (example: 127.0.0.1)\n")
        return

    scanning = True
    output.delete(1.0, tk.END)
    q.put(f"[+] Target: {target}\n")
    q.put("[*] Resolving host...\n")

    try:
        ip = socket.gethostbyname(target)
        q.put(f"[+] Resolved IP: {ip}\n\n")
    except:
        q.put("[-] Invalid host\n")
        scanning = False
        return

    def check_port(port):
        if not scanning:
            return
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(TIMEOUT)
            if s.connect_ex((ip, port)) == 0:
                q.put(f"[OPEN] Port {port}\n")

    def worker():
        global scanning
        q.put("[*] Scanning started...\n\n")

        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            executor.map(check_port, range(PORT_RANGE[0], PORT_RANGE[1]))

        q.put("\n[*] Scan complete\n")
        scanning = False

    threading.Thread(target=worker, daemon=True).start()


def stop_scan():
    global scanning
    scanning = False
    q.put("\n[!] Scan stopped by user\n")


# ----------------------------
# UI updater (thread safe)
# ----------------------------
def update_output():
    try:
        while True:
            msg = q.get_nowait()
            output.insert(tk.END, msg)
            output.see(tk.END)
    except:
        pass

    root.after(50, update_output)


# ----------------------------
# UI
# ----------------------------
root = tk.Tk()
root.title("AC Network Analyzer 0.2")
root.geometry("650x420")
root.configure(bg="black")

title = tk.Label(
    root,
    text="AC Network Analyzer 0.2",
    fg="cyan",
    bg="black",
    font=("Consolas", 16, "bold")
)
title.pack(pady=10)

entry = tk.Entry(
    root,
    width=40,
    fg="cyan",
    bg="black",
    insertbackground="cyan"
)
entry.insert(0, "127.0.0.1")
entry.pack(pady=5)

frame = tk.Frame(root, bg="black")
frame.pack(pady=10)

tk.Button(
    frame,
    text="SCAN",
    command=scan_ports,
    fg="cyan",
    bg="black"
).pack(side=tk.LEFT, padx=5)

tk.Button(
    frame,
    text="STOP",
    command=stop_scan,
    fg="cyan",
    bg="black"
).pack(side=tk.LEFT, padx=5)

output = scrolledtext.ScrolledText(
    root,
    width=75,
    height=18,
    fg="cyan",
    bg="black",
    insertbackground="cyan"
)
output.pack()

root.after(50, update_output)
root.mainloop()