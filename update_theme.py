#!/usr/bin/env python3
import os
import re

template_dir = 'templates'
replacements = [
    (r'#00E5FF|#00e5ff', '#10b981'),
    (r'#00626e', '#064e3b'),
    (r'cyan-500', 'green-600'),
    (r'cyan-900', 'emerald-900'),
    (r'cyan-600', 'green-600'),
    (r'rgba\(0, 229, 255,', 'rgba(16, 185, 129,'),
    (r'c3f5ff', '6ee7b7'),
]

for filename in sorted(os.listdir(template_dir)):
    if filename.endswith('.html'):
        filepath = os.path.join(template_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        for pattern, replacement in replacements:
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f'✓ {filename}')
        else:
            print(f'- {filename} (no changes)')

print('\nAll templates processed!')
