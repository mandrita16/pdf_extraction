#!/usr/bin/env python3
"""
Interactive PDF Extraction Demo
User-friendly interface for testing PDF extraction
"""

import sys
import os
from pathlib import Path

def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_menu():
    """Display main menu"""
    print(" PDF Extraction Interactive Demo")
    print("=" * 40)
    print("1.  List PDF files")
    print("2.  Extract from single PDF")
    print("3.  Batch process all PDFs")
    print("4.  Open output folder")
    print("5.  Help & Troubleshooting")
    print("0.  Exit")
    print("=" * 40)
    return input("Choose option (0-5): ").strip()

def list_pdf_files():
    """List available PDF files"""
    print("\n Available PDF Files:")
    print("-" * 30)

    test_pdf_dir = Path("../test_pdfs")
    pdf_files = list(test_pdf_dir.glob("*.pdf"))

    if not pdf_files:
        print(" No PDF files found!")
        print(f"Add PDF files to: {test_pdf_dir.absolute()}")
        return []

    for i, pdf in enumerate(pdf_files, 1):
        size_mb = pdf.stat().st_size / (1024 * 1024)
        print(f"{i}. {pdf.name} ({size_mb:.1f} MB)")

    return pdf_files

def extract_single_pdf():
    """Extract content from a single PDF"""
    pdf_files = list_pdf_files()
    if not pdf_files:
        return

    try:
        choice = int(input(f"\nSelect PDF (1-{len(pdf_files)}): ")) - 1
        if 0 <= choice < len(pdf_files):
            selected_pdf = pdf_files[choice]

            print(f"\n Processing: {selected_pdf.name}")

            
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            from pdf_extraction_pipeline import EfficientPDFExtractor

            pipeline = EfficientPDFExtractor(output_dir="../output")
            result = pipeline.extract_pdf_content(str(selected_pdf))

            
            print(" Extraction completed!")
            print(f" Results:")
            print(f"   Pages: {result.page_count}")
            print(f"   Words: {result.total_words:,}")
            print(f"   Characters: {result.total_chars:,}")
            print(f"   Fonts: {len(result.fonts_used)}")
            print(f"   Images: {result.images_count}")

            
            if result.pages:
                first_text = result.pages[0].get('text', '')[:200]
                print(f"\n First 200 characters:")
                print(f"   {repr(first_text)}...")

        else:
            print(" Invalid selection")

    except (ValueError, IndexError):
        print(" Invalid input")
    except Exception as e:
        print(f" Error: {e}")

def batch_process():
    """Process all PDF files"""
    pdf_files = list_pdf_files()
    if not pdf_files:
        return

    print(f"\n Processing {len(pdf_files)} PDF files...")

    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from pdf_extraction_pipeline import EfficientPDFExtractor

        pipeline = EfficientPDFExtractor(output_dir="../output")

        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"\n Processing {i}/{len(pdf_files)}: {pdf_file.name}")

            try:
                result = pipeline.extract_pdf_content(str(pdf_file))
                print(f"    Success! {result.total_words:,} words extracted")

            except Exception as e:
                print(f"    Failed: {e}")

        print(f"\n Batch processing completed!")
        print(f" Check output folder: {Path('../output').absolute()}")

    except Exception as e:
        print(f" Batch processing error: {e}")

def open_output_folder():
    """Open output folder in file explorer"""
    output_dir = Path("../output").absolute()

    try:
        if os.name == 'nt':  
            os.startfile(str(output_dir))
        elif os.name == 'posix':  
            os.system(f'open "{output_dir}"')

        print(f" Opened: {output_dir}")

    except Exception as e:
        print(f" Could not open folder: {e}")
        print(f" Manual path: {output_dir}")

def show_help():
    """Show help and troubleshooting"""
    print("\n Help & Troubleshooting")
    print("=" * 40)
    print("Common Issues:\n")
    print(" 'No PDF files found'")
    print("   ➤ Add PDF files to test_pdfs/ folder\n")
    print(" 'Module not found' errors")
    print("   ➤ Run: pip install PyMuPDF Pillow numpy\n")
    print(" 'Permission denied'")
    print("   ➤ Run VS Code as Administrator\n")
    print(" Virtual environment issues")
    print("   ➤ Run: pdf_env\\Scripts\\activate\n")
    print(" Need more help?")
    print("   ➤ 1. Check terminal errors")
    print("   ➤ 2. Verify all packages")
    print("   ➤ 3. Try bulletproof_test.py first")

def main():
    """Main interactive loop"""
    while True:
        try:
            clear_screen()
            choice = show_menu()

            if choice == '0':
                print(" Thanks,bye!")
                break
            elif choice == '1':
                list_pdf_files()
            elif choice == '2':
                extract_single_pdf()
            elif choice == '3':
                batch_process()
            elif choice == '4':
                open_output_folder()
            elif choice == '5':
                show_help()
            else:
                print(" Invalid option")

            input("\nPress Enter to continue...")

        except KeyboardInterrupt:
            print("\n Thanks!")
            break
        except Exception as e:
            print(f"\n Unexpected error: {e}")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()
