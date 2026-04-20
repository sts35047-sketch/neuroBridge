#!/usr/bin/env python3
"""Test home.html template rendering"""
from flask import Flask, render_template
from jinja2 import TemplateSyntaxError, TemplateNotFound
import traceback

app = Flask(__name__, template_folder='templates')

try:
    with app.app_context():
        html = render_template('home.html')
        print("✅ Successfully rendered home.html")
        print(f"Output size: {len(html)} bytes")
        # Check if there are HTML errors
        if '<html>' in html.lower() and '</html>' in html.lower():
            print("✅ HTML structure looks complete")
        if '<script>' in html or '<script ' in html:
            print(f"✅ Found {html.count('<script')} script tags")
        if '</script>' in html:
            print(f"✅ Found {html.count('</script>')} closing script tags")
except TemplateSyntaxError as e:
    print(f"❌ Template Syntax Error on line {e.lineno}:")
    print(f"   {e.message}")
    print(f"\nContext:")
    if e.source:
        lines = e.source.split('\n')
        start = max(0, e.lineno - 3)
        end = min(len(lines), e.lineno + 2)
        for i in range(start, end):
            prefix = ">>> " if i == e.lineno - 1 else "    "
            print(f"{prefix}{i+1}: {lines[i]}")
except TemplateNotFound as e:
    print(f"❌ Template not found: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
    traceback.print_exc()
