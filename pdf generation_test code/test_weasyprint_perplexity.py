# pdf generation_test code\test_weasyprint_perplexity.py
from weasyprint import HTML

HTML('https://www.google.com').write_pdf('test.pdf')