#!/usr/bin/env python3
"""
Efficient PDF Extraction Pipeline - 
Focuses on reliability and speed with minimal dependencies
Uses only PyMuPDF (fitz) for maximum compatibility
"""

import os
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


try:
    import fitz  
    PYMUPDF_AVAILABLE = True
    logger.info(" PyMuPDF available")
except ImportError:
    PYMUPDF_AVAILABLE = False
    logger.error(" PyMuPDF required. Install with: pip install PyMuPDF")
    sys.exit(1)


try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    logger.info("  NumPy not available - some optimizations disabled")

@dataclass
class PDFExtractionResult:
    """Streamlined result structure"""
    file_path: str
    file_hash: str
    timestamp: str
    page_count: int
    total_words: int
    total_chars: int
    fonts_used: List[str]
    images_count: int
    metadata: Dict[str, Any]
    pages: List[Dict[str, Any]]
    extraction_time: float
    file_size_mb: float
    basic_extraction: Dict[str, Any]


class EfficientPDFExtractor:
    """
    Streamlined PDF extractor focusing on:
    - Speed and efficiency
    - Minimal memory usage
    - Robust error handling
    - Parallel processing capability
    """
    
    def __init__(self, output_dir: str = "extracted_content", enable_images: bool = True):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.enable_images = enable_images
        self.processed_files = set()  
        
        logger.info(f" Extractor initialized - Output: {self.output_dir}")

    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate MD5 hash for file deduplication"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def _extract_page_content(self, page, page_num: int) -> Dict[str, Any]:
        """Extract content from a single page with optimizations"""
        
        
        text = page.get_text()
        word_count = len(text.split()) if text else 0
        char_count = len(text)
        
        page_content = {
            "page_number": page_num + 1,
            "text": text,
            "word_count": word_count,
            "char_count": char_count,
            "fonts": [],
            "images": [],
            "bbox": list(page.rect)
        }
        
        
        if text and word_count > 0:
            try:
                text_dict = page.get_text("dict")
                fonts_on_page = set()
                
                for block in text_dict.get("blocks", []):
                    if "lines" in block:
                        for line in block["lines"]:
                            for span in line["spans"]:
                                font_info = f"{span.get('font', 'Unknown')} ({span.get('size', 0):.1f}pt)"
                                fonts_on_page.add(font_info)
                
                page_content["fonts"] = list(fonts_on_page)
                
            except Exception as e:
                logger.warning(f"Font extraction failed for page {page_num + 1}: {e}")
        
        
        if self.enable_images:
            try:
                image_list = page.get_images()
                images_info = []
                
                for img_index, img in enumerate(image_list):
                    try:
                        xref = img[0]
                        base_image = page.parent.extract_image(xref)
                        images_info.append({
                            "index": img_index,
                            "width": base_image.get("width", 0),
                            "height": base_image.get("height", 0),
                            "ext": base_image.get("ext", "unknown"),
                            "size_bytes": len(base_image.get("image", b""))
                        })
                    except Exception:
                        
                        continue
                
                page_content["images"] = images_info
                
            except Exception as e:
                logger.warning(f"Image extraction failed for page {page_num + 1}: {e}")
        
        return page_content

    def extract_pdf_content(self, pdf_path: str, skip_cache: bool = False) -> PDFExtractionResult:
        """
        Efficiently extract content from PDF with caching and optimization
        """
        start_time = time.time()
        
        
        pdf_file = Path(pdf_path)
        if not pdf_file.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        file_size_mb = pdf_file.stat().st_size / (1024 * 1024)
        file_hash = self._calculate_file_hash(pdf_path)
        
        
        if not skip_cache and file_hash in self.processed_files:
            logger.info(f" File already processed (cached): {pdf_file.name}")
            
        logger.info(f" Processing: {pdf_file.name} ({file_size_mb:.1f} MB)")
        
        
        try:
            doc = fitz.open(pdf_path)
        except Exception as e:
            raise Exception(f"Cannot open PDF file: {e}")
        
        
        metadata = {}
        try:
            raw_metadata = doc.metadata
            
            for key, value in raw_metadata.items():
                if value and value.strip():
                    metadata[key] = value.strip()
        except Exception as e:
            logger.warning(f"Metadata extraction failed: {e}")
        
        
        total_words = 0
        total_chars = 0
        all_fonts = set()
        total_images = 0
        pages_content = []
        
       
        for page_num in range(len(doc)):
            try:
                page = doc.load_page(page_num)
                page_content = self._extract_page_content(page, page_num)
                
                
                total_words += page_content["word_count"]
                total_chars += page_content["char_count"]
                all_fonts.update(page_content["fonts"])
                total_images += len(page_content["images"])
                
                pages_content.append(page_content)
                
                
                if (page_num + 1) % 10 == 0:
                    logger.info(f"    Processed {page_num + 1}/{len(doc)} pages")
                
            except Exception as e:
                logger.error(f"Error processing page {page_num + 1}: {e}")
                
                continue
        
        doc.close()
        
        
        extraction_time = time.time() - start_time

        
        extracted_data = {
            "page_count": len(pages_content),
            "text_stats": {
                "total_words": total_words,
                "total_chars": total_chars
            },
            "fonts_used": sorted(list(all_fonts)),
            "images_count": total_images,
            "metadata": metadata,
            "pages": pages_content,
        }

        
        
        result = PDFExtractionResult(
            file_path=pdf_path,
            file_hash=file_hash,
            timestamp=datetime.now().isoformat(),
            page_count=len(pages_content),
            total_words=total_words,
            total_chars=total_chars,
            fonts_used=sorted(list(all_fonts)),
            images_count=total_images,
            metadata=metadata,
            pages=pages_content,
            extraction_time=extraction_time,
            file_size_mb=file_size_mb,
            basic_extraction=extracted_data
        )
        
        self.processed_files.add(file_hash)
        
        logger.info(f" Completed in {extraction_time:.2f}s - {total_words:,} words, {total_images} images")
        return result

    def save_result(self, result: PDFExtractionResult, format_type: str = "json") -> str:
        """Save extraction result efficiently"""
        
        file_stem = Path(result.file_path).stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format_type.lower() == "json":
            output_file = self.output_dir / f"{file_stem}_{timestamp}.json"
            
            
            with open(output_file, 'w', encoding='utf-8') as f:
                if result.file_size_mb > 50:  
                    
                    json.dump(asdict(result), f, ensure_ascii=False, separators=(',', ':'))
                else:
                    
                    json.dump(asdict(result), f, indent=2, ensure_ascii=False)
        
        elif format_type.lower() == "summary":
            output_file = self.output_dir / f"{file_stem}_{timestamp}_summary.txt"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(self._generate_summary_report(result))
        
        else:
            raise ValueError(f"Unsupported format: {format_type}")
        
        logger.info(f" Saved: {output_file}")
        return str(output_file)

    def _generate_summary_report(self, result: PDFExtractionResult) -> str:
        """Generate concise summary report"""
        
        report = f"""PDF EXTRACTION SUMMARY
                    {'='*50}

                    File: {Path(result.file_path).name}
                    Size: {result.file_size_mb:.1f} MB
                    Hash: {result.file_hash[:16]}...
                    Processed: {result.timestamp}
                    Time: {result.extraction_time:.2f} seconds

                    CONTENT STATISTICS
                    {'-'*30}
                    Pages: {result.page_count}
                    Words: {result.total_words:,}
                    Characters: {result.total_chars:,}
                    Images: {result.images_count}
                    Fonts: {len(result.fonts_used)}

                    METADATA
                    {'-'*30}
                    """
        
        for key, value in result.metadata.items():
            report += f"{key}: {value}\n"
        
        
        if len(result.fonts_used) <= 10:
            report += f"\nFONTS USED\n{'-'*30}\n"
            for font in result.fonts_used:
                report += f"• {font}\n"
        
       
        rate = result.total_words / result.extraction_time if result.extraction_time > 0 else 0
        report += f"\nProcessing Rate: {rate:,.0f} words/second\n"
        
        return report

    def batch_process(self, pdf_directory: str, max_workers: int = 4, 
                     save_format: str = "json") -> List[str]:
        """
        Process multiple PDFs in parallel for maximum efficiency
        """
        pdf_dir = Path(pdf_directory)
        if not pdf_dir.exists():
            raise FileNotFoundError(f"Directory not found: {pdf_directory}")
        
        pdf_files = list(pdf_dir.glob("*.pdf"))
        if not pdf_files:
            logger.warning(f"No PDF files found in: {pdf_directory}")
            return []
        
        logger.info(f" Starting batch processing: {len(pdf_files)} files, {max_workers} workers")
        
        output_files = []
        failed_files = []
        start_time = time.time()
        
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            
            future_to_file = {
                executor.submit(self._process_single_file, str(pdf_file), save_format): pdf_file
                for pdf_file in pdf_files
            }
            
            
            for future in as_completed(future_to_file):
                pdf_file = future_to_file[future]
                try:
                    output_file = future.result()
                    if output_file:
                        output_files.append(output_file)
                        logger.info(f" Completed: {pdf_file.name}")
                    else:
                        failed_files.append(str(pdf_file))
                        
                except Exception as e:
                    logger.error(f" Failed: {pdf_file.name} - {e}")
                    failed_files.append(str(pdf_file))
        
       
        total_time = time.time() - start_time
        success_count = len(output_files)
        fail_count = len(failed_files)
        
        logger.info(f" Batch processing completed in {total_time:.1f}s")
        logger.info(f"    Success: {success_count}")
        logger.info(f"    Failed: {fail_count}")
        
        if fail_count > 0:
            logger.info(f"   Failed files: {[Path(f).name for f in failed_files[:5]]}")
        
        return output_files

    def _process_single_file(self, pdf_path: str, save_format: str) -> Optional[str]:
        """Process single file (used by batch processor)"""
        try:
            result = self.extract_pdf_content(pdf_path)
            return self.save_result(result, save_format)
        except Exception as e:
            logger.error(f"Processing failed for {Path(pdf_path).name}: {e}")
            return None

    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        return {
            "files_processed": len(self.processed_files),
            "output_directory": str(self.output_dir),
            "image_extraction_enabled": self.enable_images,
            "numpy_available": NUMPY_AVAILABLE
        }
    def process_pdf(self, pdf_path: str) -> PDFExtractionResult:
        """
        Alias for extract_pdf_content() for compatibility with bulletproof_test.py
        """
        return self.extract_pdf_content(pdf_path)


def demonstrate_usage():
    """Demonstrate efficient PDF extraction on all PDFs"""

    print(" Efficient PDF Extraction Demo")
    print("=" * 50)

   
    extractor = EfficientPDFExtractor(
        output_dir="efficient_extraction_results",
        enable_images=True
    )

    
    from pathlib import Path
    pdf_folder = Path("../test_pdfs")
    pdf_list = list(pdf_folder.glob("*.pdf"))

    if not pdf_list:
        print(" No PDFs found in '../test_pdfs' folder.")
        return

    print("\n Batch Processing All PDFs:")
    for i, pdf_file in enumerate(pdf_list, 1):
        print(f"\n [{i}/{len(pdf_list)}] Processing: {pdf_file.name}")
        try:
            result = extractor.extract_pdf_content(str(pdf_file))
            extractor.save_result(result, "json")
            extractor.save_result(result, "summary")

            print(f" Done: {result.page_count} pages, {result.total_words:,} words, {result.images_count} images")
        except Exception as e:
            print(f" Error processing {pdf_file.name}: {e}")

    
    stats = extractor.get_processing_stats()
    print("\n Final Processing Stats:")
    for key, value in stats.items():
        print(f"   {key}: {value}")


if __name__ == "__main__":
    if not PYMUPDF_AVAILABLE:
        print("PyMuPDF is required. Install with:")
        print("   pip install PyMuPDF")
        sys.exit(1)
    
    demonstrate_usage()