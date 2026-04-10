import threading
import time

# Attempt to import winsound (Windows only)
try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False

def _sound_worker():
    """Worker function to play sound in a separate thread."""
    if HAS_WINSOUND:
        # Play a system exclamation sound or a simple beep
        # MessageBeep(-1) is a simple beep
        winsound.Beep(1000, 500)  # 1000Hz for 500ms
    else:
        # Fallback for non-windows (though user is on windows)
        print("\a") # System bell

def play_alarm():
    """Plays an alarm sound in a non-blocking thread."""
    threading.Thread(target=_sound_worker, daemon=True).start()
