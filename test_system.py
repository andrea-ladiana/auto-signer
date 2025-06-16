#!/usr/bin/env python3
"""
Test script per verificare che tutte le dipendenze siano installate correttamente
e che le funzionalità principali funzionino.
"""

import sys
import os

def test_imports():
    """Testa l'importazione di tutte le dipendenze."""
    print("🔍 Testing imports...")
    
    try:
        import tkinter as tk
        print("✅ tkinter - OK")
    except ImportError as e:
        print(f"❌ tkinter - ERROR: {e}")
        return False
    
    try:
        from tkinterdnd2 import TkinterDnD
        print("✅ tkinterdnd2 - OK")
    except ImportError as e:
        print(f"❌ tkinterdnd2 - ERROR: {e}")
        return False
    
    try:
        import fitz  # PyMuPDF
        print("✅ PyMuPDF - OK")
    except ImportError as e:
        print(f"❌ PyMuPDF - ERROR: {e}")
        return False
    
    try:
        import yaml
        print("✅ PyYAML - OK")
    except ImportError as e:
        print(f"❌ PyYAML - ERROR: {e}")
        return False
    
    try:
        from PIL import Image
        print("✅ Pillow - OK")
    except ImportError as e:
        print(f"❌ Pillow - ERROR: {e}")
        return False
    
    try:
        from PyPDF2 import PdfReader
        print("✅ PyPDF2 - OK")
    except ImportError as e:
        print(f"❌ PyPDF2 - ERROR: {e}")
        return False
    
    try:
        from reportlab.pdfgen import canvas
        print("✅ ReportLab - OK")
    except ImportError as e:
        print(f"❌ ReportLab - ERROR: {e}")
        return False
    
    return True

def test_core_functionality():
    """Testa le funzionalità core del PDF signer."""
    print("\n🧪 Testing core functionality...")
    
    try:
        from pdf_signer import create_watermark_pdf, add_watermark_to_pdf
        print("✅ Core functions import - OK")
    except ImportError as e:
        print(f"❌ Core functions import - ERROR: {e}")
        return False
    
    return True

def test_gui_classes():
    """Testa l'importazione delle classi GUI."""
    print("\n🎨 Testing GUI classes...")
    
    try:
        from pdf_signer_gui import ConfigManager, PDFPreviewCanvas, PDFSignerGUI
        print("✅ GUI classes import - OK")
    except ImportError as e:
        print(f"❌ GUI classes import - ERROR: {e}")
        return False
    
    return True

def test_file_existence():
    """Verifica l'esistenza dei file necessari."""
    print("\n📁 Testing file existence...")
    
    required_files = [
        'pdf_signer.py',
        'pdf_signer_gui.py', 
        'requirements.txt',
        'README.md'
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} - EXISTS")
        else:
            print(f"❌ {file} - MISSING")
            all_exist = False
    
    # File opzionali
    optional_files = ['sign.png', 'signAL.png']
    for file in optional_files:
        if os.path.exists(file):
            print(f"ℹ️  {file} - EXISTS (optional)")
        else:
            print(f"⚠️  {file} - MISSING (optional, but recommended)")
    
    return all_exist

def test_config_creation():
    """Testa la creazione della configurazione."""
    print("\n⚙️ Testing configuration...")
    
    try:
        from pdf_signer_gui import ConfigManager
        config_manager = ConfigManager()
        print("✅ ConfigManager creation - OK")
        print(f"ℹ️  Config directory: {config_manager.config_dir}")
        return True
    except Exception as e:
        print(f"❌ ConfigManager creation - ERROR: {e}")
        return False

def main():
    """Funzione principale del test."""
    print("=" * 60)
    print("🧪 PDF SIGNER - SYSTEM TEST")
    print("=" * 60)
    
    tests = [
        ("Import Dependencies", test_imports),
        ("Core Functionality", test_core_functionality), 
        ("GUI Classes", test_gui_classes),
        ("File Existence", test_file_existence),
        ("Configuration", test_config_creation)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} - EXCEPTION: {e}")
            results.append((test_name, False))
    
    # Risultati finali
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 OVERALL: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! The system is ready to use.")
        print("\n🚀 You can now run:")
        print("   - python pdf_signer_gui.py    (GUI mode)")
        print("   - python pdf_signer.py        (CLI mode)")
        print("   - start_gui.bat               (Windows GUI)")
        return True
    else:
        print("⚠️  SOME TESTS FAILED! Check the errors above.")
        print("\n🔧 Try running:")
        print("   - pip install -r requirements.txt")
        print("   - pip install PyMuPDF tkinterdnd2 pyyaml")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
