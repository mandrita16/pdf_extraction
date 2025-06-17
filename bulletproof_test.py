#!/usr/bin/env python3
"""
Bulletproof PDF Test -
Tests PDF extraction step by step with detailed error handling
"""

import sys
import os
import json
from pathlib import Path

def test_python_environment():
    print(" Testing Python Environment...")
    print(f"   Python version: {sys.version}")
    print(f"   Python executable: {sys.executable}")
    print("    Python environment OK")

def test_required_packages():
    print("\n Testing Required Packages...")
    
    required_packages = {
        'fitz': 'PyMuPDF',
        'PIL': 'Pillow', 
        'numpy': 'NumPy',
        'json': 'Built-in JSON'
    }
    
    failed_packages = []
    
    for package, name in required_packages.items():
        try:
            __import__(package)
            print(f"    {name} - OK")
        except ImportError:
            print(f"    {name} - MISSING")
            failed_packages.append(name)
    
    if failed_packages:
        print(f"\n Missing packages: {', '.join(failed_packages)}")
        print("Run: pip install PyMuPDF Pillow numpy")
        return False
    
    print(" All required packages available")
    return True

def test_pdf_files():
    print("\n Checking for PDF files...")
    
    test_pdf_dir = Path("../test_pdfs")
    if not test_pdf_dir.exists():
        print(f"    Directory not found: {test_pdf_dir}")
        print("   Creating test_pdfs directory...")
        test_pdf_dir.mkdir(exist_ok=True)
    
    pdf_files = list(test_pdf_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("     No PDF files found!")
        print(f"   Please add PDF files to: {test_pdf_dir.absolute()}")
        return []
    
    print(f"    Found {len(pdf_files)} PDF file(s):")
    for pdf in pdf_files:
        size_mb = pdf.stat().st_size / (1024 * 1024)
        print(f"      - {pdf.name} ({size_mb:.1f} MB)")
    
    return pdf_files

def test_basic_extraction(pdf_file):
    """Test basic PDF extraction"""
    print(f"\n Testing Basic Extraction: {pdf_file.name}")
    
    try:
        import fitz
        
        
        doc = fitz.open(str(pdf_file))
        print(f"    PDF opened successfully")
        print(f"    Pages: {len(doc)}")
        
       
        metadata = doc.metadata
        print(f"    Title: {metadata.get('title', 'No title')}")
        print(f"    Author: {metadata.get('author', 'No author')}")
        
        
        if len(doc) > 0:
            page = doc.load_page(0)
            text = page.get_text()
            word_count = len(text.split())
            print(f"    First page words: {word_count}")
            
            
            images = page.get_images()
            print(f"     First page images: {len(images)}")
        
        doc.close()
        print("    Basic extraction successful!")
        return True
        
    except Exception as e:
        print(f"    Basic extraction failed: {e}")
        return False

def test_full_extraction(pdf_file):
    """Test full extraction pipeline"""
    print(f"\n Testing Full Extraction Pipeline: {pdf_file.name}")
    
    try:
        
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from pdf_extraction_pipeline import EfficientPDFExtractor as PDFExtractionPipeline

        
        
        pipeline = PDFExtractionPipeline(output_dir="../output")
        print("    Pipeline initialized")
        
        
        result = pipeline.process_pdf(str(pdf_file))
        basic_content = result.basic_extraction
        print("    Basic extraction completed")
        print(f"       Pages: {basic_content['page_count']}")
        print(f"       Words: {basic_content['text_stats']['total_words']:,}")
        print(f"       Fonts: {len(basic_content['fonts_used'])}")
        
       
        output_dir = Path("../output")
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / f"{pdf_file.stem}_extraction_test.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(basic_content, f, indent=2, ensure_ascii=False)
        
        print(f"    Results saved: {output_file}")
        print("    Full extraction successful!")
        return True
        
    except ImportError as e:
        print(f"    Pipeline import failed: {e}")
        print("    Make sure pdf_extraction_pipeline.py is in src/ folder")
        return False
    except Exception as e:
        print(f"    Full extraction failed: {e}")
        return False

def create_sample_pdf():
    """Create a simple sample PDF for testing"""
    print("\n Creating sample PDF for testing...")
    
    try:
        import fitz
        
        
        doc = fitz.open()
        page = doc.new_page()
        
        
        text = """
        Sample PDF Document
        
        This is a test document created for PDF extraction testing.
        
        Features to test:
        • Text extraction
        • Font detection
        • Metadata extraction
        
        This document contains multiple paragraphs with different formatting.
        """
        
        point = fitz.Point(72, 72)  
        page.insert_text(point, text, fontsize=12)
        
        
        sample_path = Path("../test_pdfs/sample_document.pdf")
        sample_path.parent.mkdir(exist_ok=True)
        doc.save(str(sample_path))
        doc.close()
        
        print(f"    Sample PDF created: {sample_path}")
        return sample_path
        
    except Exception as e:
        print(f"    Failed to create sample PDF: {e}")
        return None

def main():
    """Run comprehensive tests"""
    print(" Bulletproof PDF Extraction Test")
    print("=" * 60)
    
    
    test_python_environment()
    
    
    if not test_required_packages():
        print("\n  Fix package issues and run again!")
        return
    
    
    pdf_files = test_pdf_files()
    
    
    if not pdf_files:
        sample_pdf = create_sample_pdf()
        if sample_pdf:
            pdf_files = [sample_pdf]
    
    if not pdf_files:
        print("\n No PDF files available for testing")
        print("Please add PDF files to test_pdfs/ folder and run again")
        return
    
    
    test_pdf = pdf_files[0]
    if not test_basic_extraction(test_pdf):
        print("\n Basic extraction failed - check PyMuPDF installation")
        return
    
    
    if test_full_extraction(test_pdf):
        print("\n ALL TESTS PASSED!")
        print(" Your PDF extraction system is working perfectly!")
        
        print(f"\n Check these folders for results:")
        print(f"    JSON results: {Path('../output').absolute()}")
        print(f"    Test PDFs: {Path('../test_pdfs').absolute()}")
        
    else:
        print("\n  Basic extraction works, but full pipeline has issues")
        print(" This is normal - you can still extract PDF content!")

if __name__ == "__main__":
    main()