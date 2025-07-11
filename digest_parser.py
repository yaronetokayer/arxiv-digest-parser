import re
import sys
import argparse

def parse_arxiv_digest(text):
    """
    Parse the raw arXiv digest email text into a list of article metadata.

    Each article is extracted based on the visual separator and includes:
    - title (str)
    - first 3 authors (List[str])
    - all authors (List[str])
    - arXiv link (str)

    Returns: List of tuples (title, short_authors, all_authors, link)
    """
    entries = re.split(r"-+\n\\\\", text)
    articles = []

    for entry in entries:
        arxiv_id_match = re.search(r"arXiv:(\d{4}\.\d{5})", entry)
        if not arxiv_id_match:
            continue
        arxiv_id = arxiv_id_match.group(1)

        # Handle multiline titles
        title_match = re.search(r"Title:\s+((?:.*\n(?:\s{2,}.*\n)*))", entry)
        title = ""
        if title_match:
            title_block = title_match.group(1)
            title = " ".join(line.strip() for line in title_block.strip().splitlines())

        # Handle multiline author blocks
        author_match = re.search(r"Authors:\s+((?:.*\n(?:\s{2,}.*\n)*))", entry)
        authors_raw = ""
        if author_match:
            author_block = author_match.group(1)
            authors_raw = " ".join(line.strip() for line in author_block.strip().splitlines())

        all_authors = [a.strip() for a in authors_raw.split(',') if a.strip()]
        authors = all_authors[:3]

        # Extract arXiv link
        link_match = re.search(r"https://arxiv.org/abs/\d{4}\.\d{5}", entry)
        link = link_match.group(0) if link_match else f"https://arxiv.org/abs/{arxiv_id}"

        articles.append((title, authors, all_authors, link))

    return articles


def sort_by_keywords(articles, keywords, author_terms):
    """
    Sort articles into matched and unmatched lists based on title keywords or author name matches.

    Returns:
        matched: List of (title, short_authors, link, match_tags)
        unmatched: same structure but with empty match_tags
    """
    matched = []
    unmatched = []

    for title, short_authors, all_authors, link in articles:
        matched_fields = []

        if any(kw.lower() in title.lower() for kw in keywords):
            matched_fields.append("title")

        matched_authors = [aterm for aterm in author_terms if any(aterm.lower() in a.lower() for a in all_authors)]
        for ma in matched_authors:
            matched_fields.append(f"author: {ma}")

        if matched_fields:
            matched.append((title, short_authors, link, matched_fields))
        else:
            unmatched.append((title, short_authors, link, []))

    return matched, unmatched


def format_articles(matched, unmatched, use_color):
    """
    Format the list of matched and unmatched articles into a printable report.
    Supports optional color output for terminal display.
    """
    output = []
    total = len(matched) + len(unmatched)
    summary = f"Collected {total} total articles, {len(matched)} of which are keyword articles."
    if use_color:
        summary = f"\033[1m{summary}\033[0m"
    output.append(summary + "\n")

    def colorize(title, authors, link, notes, title_color, author_color):
        author_str = ', '.join(authors)
        note_str = f"\n  → match: {', '.join(notes)}" if notes else ""
        return f"{title_color}- {title} {author_color}[{author_str}]\033[0m\n  {link}{note_str}"

    if matched:
        output.append("=== Keyword Matches ===")
        for title, authors, link, notes in matched:
            if use_color:
                output.append(colorize(title, authors, link, notes, "\033[92m", "\033[93m"))
            else:
                base = f"- {title} [{', '.join(authors)}]\n  {link}"
                if notes:
                    base += f"\n  → match: {', '.join(notes)}"
                output.append(base)

    if unmatched:
        if matched:
            output.append("\n=== Other Articles ===")
        for title, authors, link, _ in unmatched:
            if use_color:
                output.append(colorize(title, authors, link, [], "\033[96m", "\033[94m"))
            else:
                output.append(f"- {title} [{', '.join(authors)}]\n  {link}")

    return '\n'.join(output)


def main():
    """
    Command-line interface for parsing an arXiv digest email and printing or saving a filtered summary.
    """
    parser = argparse.ArgumentParser(description="Parse arXiv digest email")
    parser.add_argument("infile", help="Path to text file containing the email body")
    parser.add_argument("--keywords", nargs="*", default=[], help="Keywords to prioritize")
    parser.add_argument("--authors", nargs="*", default=[], help="Author names to prioritize")
    parser.add_argument("--outfile", help="Optional output file to save results")
    args = parser.parse_args()

    with open(args.infile, 'r') as f:
        text = f.read()

    articles = parse_arxiv_digest(text)
    matched, unmatched = sort_by_keywords(articles, args.keywords, args.authors)
    use_color = not args.outfile and sys.stdout.isatty()
    output = format_articles(matched, unmatched, use_color)

    if args.outfile:
        with open(args.outfile, 'w') as out:
            out.write(output)
    else:
        print(output)


if __name__ == "__main__":
    main()
