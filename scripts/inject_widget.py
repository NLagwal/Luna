import os
from src.core.config import settings

# Directories to inject into
TARGET_DIR = os.path.join(settings.ROOT_DIR, "www.juit.ac.in")
WIDGET_SCRIPT = "<script src=\"/luna-widget/luna-widget.js\"></script>"


def inject_script(file_path):
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        if WIDGET_SCRIPT in content:
            return

        # Insert after <body> tag (case-insensitive)
        body_pos = content.lower().find("<body>")
        if body_pos != -1:
            new_content = content[:body_pos+6] + f"\n{WIDGET_SCRIPT}" + content[body_pos+6:]
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"Injected into {file_path}")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def main():
    for root, _, files in os.walk(TARGET_DIR):
        for file in files:
            if file.endswith((".html", ".htm")):
                full_path = os.path.join(root, file)
                inject_script(full_path)

if __name__ == "__main__":
    main()
