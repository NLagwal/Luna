
import os
import re

def parse_html_file(input_path, output_path):
    """
    Reads an HTML file, removes script and style tags, then all other HTML tags,
    and saves the cleaned text to the output path.
    """
    try:
        with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Remove script and style blocks
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
        content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL)

        # Remove all other HTML tags
        cleaned_text = re.sub(r'<[^>]*>', '', content)

        # Remove excessive blank lines
        cleaned_text = os.linesep.join([s for s in cleaned_text.splitlines() if s.strip()])

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_text)
    except Exception as e:
        print(f"Error processing {input_path}: {e}")

def main():
    """
    Walks through the input directory, finds all HTML files, and parses them.
    """
    input_dir = 'juit_website/www.juit.ac.in'
    output_dir = 'PARSED_SHIT'

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith(('.html', '.htm')):
                input_file_path = os.path.join(root, file)

                # Create corresponding output directory
                relative_path = os.path.relpath(input_file_path, input_dir)
                output_file_path = os.path.join(output_dir, relative_path)
                output_file_dir = os.path.dirname(output_file_path)

                if not os.path.exists(output_file_dir):
                    os.makedirs(output_file_dir)

                parse_html_file(input_file_path, output_file_path)
                print(f"Parsed: {input_file_path} -> {output_file_path}")

if __name__ == '__main__':
    main()
