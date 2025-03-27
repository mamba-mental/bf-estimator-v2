from weasyprint import HTML

HTML('https://www.google.com').write_pdf('test.pdf')