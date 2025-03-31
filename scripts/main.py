import argparse
from scripts.pdf_to_lecture import pdf_to_lecture

def main():
    """
    Main entry point for the application.
    """
    parser = argparse.ArgumentParser(description='Convert PDF to lecture with text and audio')
    parser.add_argument('pdf_path', help='Path to the PDF file')
    parser.add_argument('--output', '-o', help='Output directory (default: same as PDF)')
    parser.add_argument('--visuals', '-v', default='visuals', help='Folder to save visuals (default: visuals)')
    parser.add_argument('--debug', '-d', action='store_true', help='Generate debug information for TTS')
    
    args = parser.parse_args()

    json_path, md_path, mp3_path = pdf_to_lecture(
        pdf_path=args.pdf_path,
        output_dir=args.output,
        visuals_dir=args.visuals,
        debug=args.debug
    )
    
    print("\nProcessing complete!")
    print(f"JSON file: {json_path}")
    print(f"Markdown file: {md_path}")
    print(f"Audio file: {mp3_path}")
        
    
    return 0

if __name__ == "__main__":
    exit(main())