import os
from bs4 import BeautifulSoup

def parse_html_file(input_path, output_path):
    """
    Reads an HTML file, removes script, style, and noscript tags,
    and extracts visible text using BeautifulSoup.
    """
    try:
        with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        soup = BeautifulSoup(content, 'html.parser')

        # Check for junk content
        page_text = soup.get_text().lower()
        if "404 not found" in page_text or "requested url was not found" in page_text:
            return
        if "change password" in page_text or "upload paper" in page_text:
            return

        # Target the main content area if it exists
        # In JUIT site, main content is usually in <div id="container"> or <div id="body-content">
        main_content = soup.find('div', id='container') or soup.find('div', class_='department-right')
        if main_content:
            soup = main_content

        # Remove script, style, and noscript elements
        for element in soup(['script', 'style', 'noscript']):
            element.decompose()

        # Get text, inserting a space in place of tags to avoid word concatenation
        text = soup.get_text(separator=' ')

        # Process lines: condense multiple spaces and remove empty lines
        lines = []
        for line in text.splitlines():
            clean_line = ' '.join(line.split())
            if clean_line:
                lines.append(clean_line)
        
        cleaned_text = '\n'.join(lines)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_text)
    except Exception as e:
        print(f"Error processing {input_path}: {e}")

def main():
    """
    Walks through the input directory, finds all HTML files, and parses them.
    """
    input_dir = './www.juit.ac.in'
    output_dir = 'PARSED_SHIT'

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for root, _, files in os.walk(input_dir):
        for file in files:
            # Match .html, .htm, any file containing .php, or files with no extension
            has_extension = "." in file
            if file.endswith(('.html', '.htm')) or '.php' in file or not has_extension:
                input_file_path = os.path.join(root, file)

                # Create corresponding output directory
                relative_path = os.path.relpath(input_file_path, input_dir)
                output_file_path = os.path.join(output_dir, relative_path + ".txt")
                output_file_dir = os.path.dirname(output_file_path)

                if not os.path.exists(output_file_dir):
                    os.makedirs(output_file_dir)

                parse_html_file(input_file_path, output_file_path)
                print(f"Parsed: {input_file_path} -> {output_file_path}")

if __name__ == '__main__':
    main()
