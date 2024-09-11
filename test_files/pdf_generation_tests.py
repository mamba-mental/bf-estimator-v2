import pdfkit
import os

# Configure the path to wkhtmltopdf
path_to_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
pdfkit_config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)

def debug_print(message):
    """Utility function for printing debug messages."""
    print(f"DEBUG: {message}")

def test_simple_pdf_generation():
    """Test simple PDF generation with basic HTML."""
    debug_print("Starting simple PDF generation test.")
    html_content = "<h1>Test PDF Generation</h1><p>This is a simple test.</p>"
    pdf_filename = r'C:\Code_Projects\bf-estimator-v2\results\test_simple_output.pdf'
    
    try:
        debug_print("Attempting to generate simple PDF...")
        pdfkit.from_string(html_content, pdf_filename, configuration=pdfkit_config)
        debug_print(f"Simple PDF report saved as {pdf_filename}")
    except OSError as e:
        debug_print(f"Error generating simple PDF: {e}")

def test_full_html_without_css():
    """Test PDF generation with full HTML content but without CSS."""
    html_file = r'C:\Code_Projects\bf-estimator-v2\templates\example.html'
    pdf_filename = r'C:\Code_Projects\bf-estimator-v2\results\test_full_output_without_css.pdf'
    
    # Check if HTML file exists
    if not os.path.exists(html_file):
        debug_print(f"HTML file not found: {html_file}")
        return
    
    # Read and print the HTML content for debugging
    try:
        with open(html_file, 'r') as file:
            html_content = file.read()
        debug_print("HTML content loaded successfully:")
        debug_print(html_content)
    except Exception as e:
        debug_print(f"Error reading HTML file: {e}")
        return
    
    try:
        debug_print("Attempting to generate full HTML PDF (without CSS)...")
        pdfkit.from_file(html_file, pdf_filename, configuration=pdfkit_config)
        debug_print(f"Full HTML PDF (without CSS) saved as {pdf_filename}")
    except OSError as e:
        debug_print(f"Error generating full HTML PDF without CSS: {e}")

def test_full_html_with_css():
    """Test PDF generation with full HTML content and CSS."""
    html_file = r'C:\Code_Projects\bf-estimator-v2\templates\example.html'
    pdf_filename = r'C:\Code_Projects\bf-estimator-v2\results\test_full_output_with_css.pdf'
    css_file = r'C:\Code_Projects\bf-estimator-v2\styles\report_style.css'

    # Check if HTML and CSS files exist
    if not os.path.exists(html_file):
        debug_print(f"HTML file not found: {html_file}")
        return
    
    if not os.path.exists(css_file):
        debug_print(f"CSS file not found: {css_file}")
        return
    
    # Read and print the HTML and CSS content for debugging
    try:
        with open(html_file, 'r') as file:
            html_content = file.read()
        debug_print("HTML content loaded successfully:")
        debug_print(html_content)
        
        with open(css_file, 'r') as file:
            css_content = file.read()
        debug_print("CSS content loaded successfully:")
        debug_print(css_content)
    except Exception as e:
        debug_print(f"Error reading HTML or CSS file: {e}")
        return
    
    try:
        debug_print("Attempting to generate full HTML PDF (with CSS)...")
        pdfkit.from_file(html_file, pdf_filename, configuration=pdfkit_config, css=css_file)
        debug_print(f"Full HTML PDF (with CSS) saved as {pdf_filename}")
    except OSError as e:
        debug_print(f"Error generating full HTML PDF with CSS: {e}")

# Run the script with detailed debugging
debug_print("Running individual tests...")

debug_print("\nRunning test_simple_pdf_generation...")
test_simple_pdf_generation()

debug_print("\nRunning test_full_html_without_css...")
test_full_html_without_css()

debug_print("\nRunning test_full_html_with_css...")
test_full_html_with_css()

debug_print("Testing complete.")
