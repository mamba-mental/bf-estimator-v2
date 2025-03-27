import subprocess

try:
    result = subprocess.run([r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe', '--version'], capture_output=True, text=True)
    print(result.stdout)
except FileNotFoundError as e:
    print(f"Error: {e}")
