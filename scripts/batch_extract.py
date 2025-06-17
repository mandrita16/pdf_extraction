#!/usr/bin/env python3
"""
Batch PDF Processing Script
Process all PDFs in a folder with one command
"""

import sys
import os
from pathlib import Path


sys.path.append(str(Path(__file__).parent.parent / "src"))

from pdf_extraction_pipeline import PDFExtractionPipeline

def batch_extract(input_folder, output_folder):
    """Extract content from all PDFs in a folder"""
    
    input_path = Path(input_folder)
    output_path = Path(output_folder)
    
    
    pdf_files = list(input_path.glob("*.pdf"))
    
    if not pdf_files:
        print(f" No PDF files found in {input_path}")
        return
    
    print(f" Found {len(pdf_files)} PDF files")
    print(f" Output folder: {output_path}")
    
    
    pipeline = PDFExtractionPipeline(output_dir=str(output_path))
    
    
    success_count = 0
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\n Processing {i}/{len(pdf_files)}: {pdf_file.name}")
        
        try:
           
            result = pipeline.process_pdf(str(pdf_file))
            
            
            pipeline.save_results(result, "json")
            pipeline.save_results(result, "markdown")
            
            print(f"    Success! {result.summary['extraction_overview']['total_words']:,} words")
            success_count += 1
            
        except Exception as e:
            print(f"    Failed: {e}")
    
    print(f"\n Batch processing completed!")
    print(f" Successfully processed: {success_count}/{len(pdf_files)} files")
    print(f" Results saved to: {output_path.absolute()}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python batch_extract.py <input_folder> <output_folder>")
        print("Example: python batch_extract.py ../test_pdfs ../output")
    else:
        batch_extract(sys.argv[1], sys.argv[2])