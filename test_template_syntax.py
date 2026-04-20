#!/usr/bin/env python3
from jinja2 import Environment, FileSystemLoader, TemplateSyntaxError
import sys

try:
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('home.html')
    print("✅ home.html syntax is valid")
except TemplateSyntaxError as e:
    print(f"❌ Template Syntax Error:")
    print(f"  Line {e.lineno}: {e.message}")
    print(f"  {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
