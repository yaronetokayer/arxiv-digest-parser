## ArXiv Digest Parser

This is a command-line tool for parsing daily arXiv email digests. It extracts and summarizes article titles and authors, allowing for optional filtering and highlighting of keyword matches in the title or author list.

Example input and output files are in this repo.

### Setup

Clone the repo and make sure you have Python 3.7+ installed. No external dependencies are required.

```bash
git clone https://github.com/YOUR_USERNAME/arxiv-digest-parser.git
cd arxiv-digest-parser
```

### Input

Copy the full body of your arXiv digest email and paste it into a plain text file, e.g. `digest.txt`.

### Usage

```bash
python digest_parser.py digest.txt [--keywords ...] [--authors ...] [--outfile output.txt]
```

* `digest.txt`: Plaintext version of the arXiv email body
* `--keywords`: Highlight articles with these words/phrases in the title
* `--authors`: Highlight articles with these names in the full author list
* `--outfile`: Save results to a file instead of printing to the terminal

### Examples

#### Show all articles:

```bash
python digest_parser.py digest.txt
```

#### Prioritize articles with one or more keywords (multi-word supported):

```bash
python digest_parser.py digest.txt --keywords "dark matter" AGN
```

#### Highlight author matches (even if not one of the first 3 authors shown):

```bash
python digest_parser.py digest.txt --authors "van der Waals" Curie
```

#### Save the results to a file:

```bash
python digest_parser.py digest.txt --keywords "black hole" collapse --outfile highlights.txt
```

### Output

* Matches are grouped under **Keyword Matches**
* Remaining articles are shown under **Other Articles**
* Colors are used for terminal output; they are disabled when writing to a file
