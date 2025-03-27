import pdfkit

def test_pdf_generation():
    """
    Test PDF generation with minimal complexity.
    """
    # Full path to wkhtmltopdf
    path_to_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    pdfkit_config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)

    # Simple HTML content for testing
    html_content = "<h1>Test PDF Generation</h1><p>This is a simple test.</p>"
    
    # Output PDF file path
    pdf_filename = r'C:\Code_Projects\bf-estimator-v2\results\test_output.pdf'

    # Convert HTML string to PDF
    try:
        pdfkit.from_string(html_content, pdf_filename, configuration=pdfkit_config)
        print(f"PDF report saved as {pdf_filename}")
    except OSError as e:
        print(f"Error generating PDF: {e}")

# Run the test
test_pdf_generation()