from weasyprint import HTML

def generate_pdf_with_weasyprint(html_file, pdf_file):
    """
    Converts an HTML file to PDF format using WeasyPrint.

    Parameters:
    html_file (str): The path to the input HTML file.
    pdf_file (str): The path to the output PDF file.
    """
    # Read the HTML file content
    with open(html_file, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Convert the HTML content to PDF using WeasyPrint
    try:
        HTML(string=html_content).write_pdf(pdf_file)
        print(f"PDF saved as {pdf_file}")
    except Exception as e:
        print(f"Error generating PDF with WeasyPrint: {e}")

# Example usage
if __name__ == "__main__":
    # Paths to the HTML input and PDF output files
    html_input = r'C:\Code_Projects\bf-estimator-v2\results\example.html'
    pdf_output = r'C:\Code_Projects\bf-estimator-v2\results\example_output.pdf'
    
    # Generate PDF using WeasyPrint
    generate_pdf_with_weasyprint(html_input, pdf_output)
