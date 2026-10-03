import os
import tkinter as tk
import time
import threading

try:
    import speech_recognition as sr
    STT_AVAILABLE = True
except ImportError:
    STT_AVAILABLE = False

# ── Commands ───────────────────────────────────────────────────────────────
def shutdown():
    os.system("shutdown /s /t 0")

def restart():
    os.system("shutdown /r /t 0")

def logout():
    os.system("shutdown /l /t 0")

# ── Palette ────────────────────────────────────────────────────────────────
BG      = "#050a14"
PANEL   = "#0a1628"
CYAN    = "#00f5ff"
RED     = "#ff2244"
AMBER   = "#ffaa00"
GREEN   = "#00ff88"
DIM     = "#3a5a7a"
MID     = "#7ab8d4"

# ── Window ─────────────────────────────────────────────────────────────────
window = tk.Tk()
window.geometry("700x960")
window.title("NEXUS // POWER CONTROL")
window.configure(bg=BG)
window.resizable(False, False)

# ── Clock bar ──────────────────────────────────────────────────────────────
clock = tk.Label(window, text="", font=("Courier", 9), fg=MID, bg=PANEL, pady=5)
clock.pack(fill="x")

def tick():
    clock.config(text=f"  ● ONLINE    {time.strftime('SYS-TIME  %H:%M:%S    DATE  %Y-%m-%d')}    SYS v3.7.1")
    window.after(1000, tick)
tick()

# ── Title ──────────────────────────────────────────────────────────────────
tk.Label(window, text="\nNEXUS POWER CONTROL",
         font=("Courier", 22, "bold"), fg=CYAN, bg=BG).pack()
tk.Label(window, text="SYSTEM OPERATIONS TERMINAL  //  CLASS-A CLEARANCE",
         font=("Courier", 9), fg=DIM, bg=BG).pack()
tk.Label(window, text="─" * 55, font=("Courier", 10), fg=CYAN, bg=BG).pack(pady=8)
tk.Label(window, text="⚠  ACTIONS ARE IRREVERSIBLE  ⚠",
         font=("Courier", 10, "bold"), fg=AMBER, bg=BG).pack(pady=(0, 18))

# ── Fancy Button Factory ───────────────────────────────────────────────────
class NexusButton(tk.Canvas):
    """A sleek sci-fi button drawn on a Canvas with animated hover."""
    W, H = 340, 58

    def __init__(self, parent, text, command, accent, icon="◈", **kw):
        super().__init__(parent, width=self.W, height=self.H,
                         bg=BG, highlightthickness=0, cursor="hand2", **kw)
        self.text    = text
        self.icon    = icon
        self.accent  = accent
        self.command = command
        self._hover  = False

        self.bind("<Enter>",           self._enter)
        self.bind("<Leave>",           self._leave)
        self.bind("<ButtonPress-1>",   self._press)
        self.bind("<ButtonRelease-1>", self._release)
        self._draw(hover=False)

    # ── drawing ────────────────────────────────────────────────────────────
    def _draw(self, hover=False):
        self.delete("all")
        W, H, A = self.W, self.H, self.accent

        # background fill
        fill = A if hover else BG
        self.create_rectangle(1, 1, W-1, H-1, fill=fill, outline=A, width=2)

        # left side accent strip (3 px wide)
        self.create_rectangle(1, 1, 6, H-1, fill=A, outline="")

        # corner notch top-right
        self.create_polygon(W-18, 1, W-1, 1, W-1, 18, outline=A, fill=A)

        # diagonal cut line top-right
        self.create_line(W-18, 1, W-1, 18, fill=BG, width=2)

        # bottom-left tick mark
        self.create_line(1, H-10, 12, H-1, fill=A, width=2)

        # icon + label
        text_color = BG if hover else A
        self.create_text(26, H//2, text=self.icon,
                         font=("Courier", 14, "bold"), fill=A if not hover else BG,
                         anchor="center")
        self.create_text(W//2 + 10, H//2, text=self.text.upper(),
                         font=("Courier", 14, "bold"), fill=text_color, anchor="center")

        # right-side arrow hint
        arrow_col = BG if hover else DIM
        self.create_text(W-22, H//2+6, text="▶", font=("Courier", 8),
                         fill=arrow_col, anchor="center")

    def _enter(self, _):
        self._hover = True
        self._draw(hover=True)

    def _leave(self, _):
        self._hover = False
        self._draw(hover=False)

    def _press(self, _):
        # quick flash
        self.create_rectangle(1, 1, self.W-1, self.H-1,
                               fill="white", outline="", stipple="gray50")

    def _release(self, _):
        self._draw(hover=self._hover)
        if self.command:
            self.command()

# ── Power buttons ──────────────────────────────────────────────────────────
btn_configs = [
    ("SHUTDOWN", shutdown, RED,   "⏻"),
    ("RESTART",  restart,  CYAN,  "↺"),
    ("LOGOUT",   logout,   AMBER, "⇥"),
]

for label, cmd, color, icon in btn_configs:
    b = NexusButton(window, text=label, command=cmd, accent=color, icon=icon)
    b.pack(pady=9)

# ── Divider ────────────────────────────────────────────────────────────────
tk.Label(window, text="─" * 55, font=("Courier", 10), fg=CYAN, bg=BG).pack(pady=(18, 6))
tk.Label(window, text="◈  VOICE COMMAND INTERFACE  ◈",
         font=("Courier", 11, "bold"), fg=CYAN, bg=BG).pack()
tk.Label(window, text="SAY: 'shutdown' · 'restart' · 'logout'  //  OR TRANSCRIBE FREELY",
         font=("Courier", 8), fg=DIM, bg=BG).pack(pady=(2, 10))

# ── Status label ───────────────────────────────────────────────────────────
stt_status = tk.Label(window, text="● STANDBY",
                      font=("Courier", 10, "bold"), fg=DIM, bg=BG)
stt_status.pack()

# ── Transcript box ─────────────────────────────────────────────────────────
transcript_wrap = tk.Frame(window, bg=CYAN, padx=1, pady=1)
transcript_wrap.pack(padx=30, pady=10, fill="x")
transcript_frame = tk.Frame(transcript_wrap, bg=PANEL)
transcript_frame.pack(fill="x")
tk.Label(transcript_frame, text="[ VOICE TRANSCRIPT LOG ]",
         font=("Courier", 8), fg=DIM, bg=PANEL).pack(anchor="w", padx=8, pady=(6, 0))
transcript_box = tk.Text(
    transcript_frame, height=6, font=("Courier", 10),
    fg=CYAN, bg=PANEL, insertbackground=CYAN,
    relief="flat", wrap="word", state="disabled", selectbackground="#0d2040"
)
transcript_box.pack(fill="x", padx=8, pady=(2, 8))

def append_transcript(text, color=CYAN):
    transcript_box.config(state="normal")
    ts = time.strftime("%H:%M:%S")
    tag = f"t{transcript_box.index('end')}"
    start = transcript_box.index("end")
    transcript_box.insert("end", f"[{ts}]  {text}\n")
    transcript_box.tag_add(tag, start, transcript_box.index("end"))
    transcript_box.tag_config(tag, foreground=color)
    transcript_box.see("end")
    transcript_box.config(state="disabled")

# ── Voice handler ──────────────────────────────────────────────────────────
def handle_voice_command(text):
    lower = text.lower().strip()
    if "shutdown" in lower:
        append_transcript("COMMAND DETECTED: SHUTDOWN", RED)
        stt_status.config(text="⚡ EXECUTING: SHUTDOWN", fg=RED)
        window.after(1500, shutdown)
    elif "restart" in lower or "reboot" in lower:
        append_transcript("COMMAND DETECTED: RESTART", CYAN)
        stt_status.config(text="⚡ EXECUTING: RESTART", fg=CYAN)
        window.after(1500, restart)
    elif "logout" in lower or "log out" in lower or "sign out" in lower:
        append_transcript("COMMAND DETECTED: LOGOUT", AMBER)
        stt_status.config(text="⚡ EXECUTING: LOGOUT", fg=AMBER)
        window.after(1500, logout)
    else:
        append_transcript(text)
        stt_status.config(text="● STANDBY — NO COMMAND MATCHED", fg=DIM)

# ── STT thread ─────────────────────────────────────────────────────────────
is_listening = False

def listen_once():
    global is_listening
    if not STT_AVAILABLE:
        append_transcript("ERROR: speechrecognition not installed.")
        append_transcript("Run:  pip install speechrecognition pyaudio")
        stt_status.config(text="✕ MODULE NOT INSTALLED", fg=RED)
        is_listening = False
        mic_btn._draw(hover=False)
        return

    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            window.after(0, lambda: stt_status.config(text="◈ CALIBRATING...", fg=AMBER))
            recognizer.adjust_for_ambient_noise(source, duration=0.6)
            window.after(0, lambda: stt_status.config(text="◉ LISTENING... SPEAK NOW", fg=GREEN))
            audio = recognizer.listen(source, timeout=8, phrase_time_limit=10)
        window.after(0, lambda: stt_status.config(text="◈ PROCESSING...", fg=AMBER))
        text = recognizer.recognize_google(audio)
        window.after(0, lambda: handle_voice_command(text))
    except sr.WaitTimeoutError:
        window.after(0, lambda: stt_status.config(text="● TIMEOUT — NO SPEECH DETECTED", fg=DIM))
        window.after(0, lambda: append_transcript("Timeout: no speech detected."))
    except sr.UnknownValueError:
        window.after(0, lambda: stt_status.config(text="● COULD NOT UNDERSTAND AUDIO", fg=AMBER))
        window.after(0, lambda: append_transcript("Could not understand audio."))
    except sr.RequestError as e:
        window.after(0, lambda: stt_status.config(text="✕ NETWORK ERROR", fg=RED))
        window.after(0, lambda: append_transcript(f"API error: {e}"))
    except Exception as e:
        window.after(0, lambda: stt_status.config(text="✕ MIC ERROR", fg=RED))
        window.after(0, lambda: append_transcript(f"Error: {e}"))
    finally:
        is_listening = False
        window.after(0, lambda: mic_btn._draw(hover=False))

def toggle_listen():
    global is_listening
    if is_listening:
        return
    is_listening = True
    mic_btn._draw(hover=True)
    append_transcript("── Mic activated ──", DIM)
    threading.Thread(target=listen_once, daemon=True).start()

# ── Mic button ─────────────────────────────────────────────────────────────
mic_btn = NexusButton(window, text="ACTIVATE MIC", command=toggle_listen,
                      accent=GREEN, icon="🎙")
mic_btn.pack(pady=10)

# ── Clear button ───────────────────────────────────────────────────────────
def clear_transcript():
    transcript_box.config(state="normal")
    transcript_box.delete("1.0", "end")
    transcript_box.config(state="disabled")
    stt_status.config(text="● STANDBY", fg=DIM)

clr = tk.Button(window, text="◈  CLEAR LOG", command=clear_transcript,
                font=("Courier", 9), fg=DIM, bg=BG,
                activebackground=DIM, activeforeground=BG,
                relief="flat", bd=0, cursor="hand2")
clr.pack(pady=(0, 6))
clr.bind("<Enter>", lambda e: clr.config(fg=MID))
clr.bind("<Leave>", lambda e: clr.config(fg=DIM))

# ── Footer ─────────────────────────────────────────────────────────────────
tk.Label(window, text="─" * 55, font=("Courier", 8), fg="#0d2040", bg=BG).pack(pady=(10, 0))
tk.Label(window, text="ALL OPERATIONS LOGGED  //  SESSION ENCRYPTED",
         font=("Courier", 8), fg=DIM, bg=BG).pack()
tk.Label(window, text="◈ — NEXUS SYSTEMS — ◈",
         font=("Courier", 9, "bold"), fg=CYAN, bg=BG).pack(pady=6)

if not STT_AVAILABLE:
    append_transcript("speechrecognition not found.")
    append_transcript("pip install speechrecognition pyaudio")
    stt_status.config(text="✕ MODULE NOT INSTALLED", fg=RED)

window.mainloop()