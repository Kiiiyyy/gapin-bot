import os
import sys
from contextlib import contextmanager

@contextmanager
def silence_alsa():
    """
    Fungsi sakti untuk membungkam error level C (ALSA/JACK)
    agar tidak mengotori terminal.
    """
    try:
        # Simpan file descriptor asli
        original_stderr = os.dup(sys.stderr.fileno())
        original_stdout = os.dup(sys.stdout.fileno())
        
        # Buka tempat sampah (devnull)
        devnull = os.open(os.devnull, os.O_WRONLY)
        
        # Redirect output error ke tempat sampah
        os.dup2(devnull, sys.stderr.fileno())
        os.dup2(devnull, sys.stdout.fileno())
        
        yield
        
    finally:
        # Kembalikan output ke terminal seperti semula
        os.dup2(original_stderr, sys.stderr.fileno())
        os.dup2(original_stdout, sys.stdout.fileno())
        
        os.close(original_stderr)
        os.close(original_stdout)
        if 'devnull' in locals():
            os.close(devnull)