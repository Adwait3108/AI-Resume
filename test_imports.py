#!/usr/bin/env python3
"""Test script to check if all required modules are available"""

import sys

print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print(f"\nPython path:")
for path in sys.path:
    print(f"  - {path}")

print("\n" + "="*50)
print("Testing imports...")
print("="*50)

modules = [
    'flask',
    'flask_cors',
    'google.generativeai',
    'werkzeug.utils',
    'PyPDF2'
]

failed = []
for module in modules:
    try:
        __import__(module)
        print(f"✓ {module} - OK")
    except ImportError as e:
        print(f"✗ {module} - FAILED: {e}")
        failed.append(module)

print("\n" + "="*50)
if failed:
    print(f"FAILED: {len(failed)} module(s) not found")
    print("\nTo fix, run:")
    print("  python3 -m pip install -r requirements.txt")
else:
    print("SUCCESS: All modules are available!")
    print("\nYou can now run the app with:")
    print("  python3 app.py")
