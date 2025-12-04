import os
import json
import re
from bs4 import BeautifulSoup

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="stylesheet" href="../styles.css">
    <script src="https://unpkg.com/@phosphor-icons/web"></script>
    <script src="../script.js" defer></script>
</head>
<body>
    <nav class="navbar">
        <div class="nav-content">
            <a href="../index.html" class="nav-brand">
                <i class="ph ph-books"></i> Cheatsheets
            </a>
            <div class="nav-controls">
                <button id="theme-toggle" class="btn-icon" aria-label="Toggle theme">
                    <i class="ph ph-moon"></i>
                </button>
                <button id="download-btn" class="btn-icon" aria-label="Download PDF">
                    <i class="ph ph-download-simple"></i>
                </button>
                <a href="https://github.com/keyurgolani/Cheatsheets" class="btn-icon" aria-label="GitHub" target="_blank" rel="noopener noreferrer">
                    <i class="ph ph-github-logo"></i>
                </a>
            </div>
        </div>
    </nav>

    <div class="container">
        <header class="cheatsheet-header">
            <h1>{header_title}</h1>
            <p>{subtitle}</p>
            <div class="search-container" style="margin-top: 1.5rem; margin-bottom: 0;">
                <span class="search-icon"><i class="ph ph-magnifying-glass"></i></span>
                <input type="text" class="search-input" id="cheatsheet-search" placeholder="Filter this cheatsheet..." aria-label="Filter cheatsheet">
            </div>
        </header>

        <div class="masonry-grid" id="cheatsheet-grid">
            {cards_html}
        </div>

        <footer>
            <p>&copy; 2025 Cheatsheets Collection. Open source and community driven.</p>
        </footer>
    </div>
</body>
</html>"""


def slugify(text):
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)
    return text.strip("-")


def regenerate_file(filepath, search_index):
    with open(filepath, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    # Extract Metadata
    title_tag = soup.find("title")
    title = title_tag.text if title_tag else "Cheatsheet"

    # Extract Header Info
    h1 = soup.find("h1")
    header_title = h1.text.strip() if h1 else title
    header_title = (
        header_title.replace("🐍", "").replace("☕", "").replace("⚡", "").strip()
    )

    subtitle = ""
    if h1:
        next_elem = h1.find_next_sibling("p")
        if next_elem:
            subtitle = next_elem.text.strip()

    # Extract Cards
    cards_html = ""
    cards = soup.find_all(class_="card")

    filename = os.path.basename(filepath)

    for card in cards:
        card_header = card.find(class_="card-header")
        card_title = card_header.text.strip() if card_header else "Section"
        card_title_clean = "".join(c for c in card_title if c.isprintable()).strip()
        card_id = slugify(card_title_clean)

        code_block = card.find(class_="code-block")
        code_content = ""
        raw_code_text = ""
        if code_block:
            code_content = "".join(
                [str(child) for child in code_block.children if child.name == "div"]
            )
            raw_code_text = code_block.get_text(separator=" ", strip=True)

        # Add to search index
        search_index.append(
            {
                "title": header_title,
                "section": card_title_clean,
                "url": f"cheatsheets/{filename}#{card_id}",
                "content": raw_code_text,
            }
        )

        cards_html += f"""
            <div class="card" id="{card_id}">
                <div class="card-header">{card_title_clean}</div>
                <div class="code-block">
                    {code_content}
                </div>
            </div>"""

    new_content = TEMPLATE.format(
        title=title, header_title=header_title, subtitle=subtitle, cards_html=cards_html
    )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"Regenerated {filepath}")


def main():
    cheatsheets_dir = "/Users/golani/PersonalProjects/Cheatsheets/cheatsheets"
    search_index = []

    for filename in os.listdir(cheatsheets_dir):
        if filename.endswith(".html"):
            filepath = os.path.join(cheatsheets_dir, filename)
            try:
                regenerate_file(filepath, search_index)
            except Exception as e:
                print(f"Failed to regenerate {filename}: {e}")

    # Save search index
    with open(
        "/Users/golani/PersonalProjects/Cheatsheets/search_index.json",
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(search_index, f, indent=2)
    print("Generated search_index.json")


if __name__ == "__main__":
    main()
