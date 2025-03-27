import ctypes
import os

# Ensure the GTK+ bin directory is in the PATH
gtk_bin_path = r'C:\Program Files\GTK3-Runtime Win64\bin'
os.environ['PATH'] += os.pathsep + gtk_bin_path

try:
    gobject = ctypes.CDLL('libgobject-2.0-0.dll')
    print("GTK+ libraries loaded successfully.")
except OSError as e:
    print(f"Error loading GTK+ libraries: {e}")