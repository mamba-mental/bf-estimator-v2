import os
from weasyprint import HTML

def test_weasyprint():
    html_content = '''
    <html>
        <head>
            <title>Test PDF</title>
        </head>
        <body>
            <h1>This is a Test PDF</h1>
            <p>If you can see this, WeasyPrint is working correctly.</p>
        </body>
    </html>
    '''
    try:
        # Generate PDF
        pdf = HTML(string=html_content).write_pdf()
        # Save PDF to file
        output_path = os.path.join(os.path.dirname(__file__), 'test_output.pdf')
        with open(output_path, 'wb') as f:
            f.write(pdf)
        print("Test PDF generated successfully at:", output_path)
    except Exception as e:
        print("Error during WeasyPrint test:", e)

if __name__ == "__main__":
    test_weasyprint()
