# pyGGG - Python Git Graph Generator

Python script that generates Git logs with graph visualization in [Tig](https://github.com/jonas/tig) format, using Unicode box-drawing characters.

It requires Python 3.6+ and Git, and can be used as a standalone script or installed for easy command-line usage.

## What does it do?

Converts Git repository history into a visual log with:
- ✨ ASCII art graph showing branches and merges
- 📅 Formatted dates
- 👤 Authors
- 🏷️ References (branches, tags, remotes)
- 💬 Commit messages

## Example Output

```
2ebf7c2 2025-12-19 14:31 miqui                      o [develop] {origin/develop} chore: bump version
d3e2e5e 2025-12-19 14:02 Miqui Infante              M─┐ [master] {origin/master} <1.9.0> Merge pull request #14
4328f73 2025-12-19 13:56 miqui                      │ o feat: add capy new MVN type
d226456 2025-11-25 17:33 Miqui Infante              M─┤ <1.8.0> Merge pull request #13
3345d78 2025-11-25 17:29 miqui                      │ o chore: bump version
6cbc8ac 2025-11-25 17:26 Javier Lahoz               M─┤ Merge pull request #12
```

**Note:** All timestamps are displayed in UTC.

## Installation

### Quick Install (Recommended)

```bash
git clone https://github.com/miqui-infante/pyGGG.git
cd pyGGG
./install.sh
```

The installer automatically detects the best location for installation by checking (in order):
1. `~/.local/bin` (XDG standard)
2. `~/bin` (traditional)
3. `~/opt/bin`
4. `~/.local/share/bin`
5. `/usr/local/bin` (if writable)
6. `/usr/local/share/bin` (if writable)
7. `/opt/bin` (if writable)

It will use the first directory that exists, is writable, and is in your PATH. If none are in PATH, it uses the first available directory and warns you to add it to PATH.

**Installed commands:**
- **`ggg`** - Generate Git Graph (outputs to stdout)
- **`gg`**  - Git Graph - Interactive viewer (pipes to `less -S`)

After installation, you can delete the cloned repository - the commands will continue to work.
(You can also keep it if you want to run the script directly from there, or to keep uninstall script for later.)

**Requirements:** Python 3.6+ and Git

### Uninstall

```bash
./uninstall.sh
```

Or manually:
```bash
rm ~/.local/bin/ggg ~/.local/bin/gg
```

### Manual Usage (Without Installation)

You can also use the script directly without installing:

```bash
./pyggg.py [OPTIONS] [--] [repo_path] [output_file]
```

**Options:**
- `-h, --help` - Show usage information
- `--` - End of options (use if repo path starts with '-')

**Arguments:**
- If no arguments provided: uses current directory as repo, outputs to stdout
- If `repo_path` provided: uses that repository, outputs to stdout
- If both provided: uses `repo_path` as repo, outputs to `output_file`

## Usage

### With Installation

```bash
# Show help
ggg --help

# Interactive view with less (scroll horizontally with arrow keys)
gg

# Output to stdout
ggg

# Save to file
ggg > git_log.txt

# Pipe to other commands
ggg | head -20

# Use on a different repository
cd /path/to/other/repo && gg
```

### Without Installation

```bash
# Show help
./pyggg.py --help

# Generate log for current repository. Output to stdout. No arguments needed!
./pyggg.py

# Output to stdout with redirection
./pyggg.py > git_log.txt

# Pipe to other commands
./pyggg.py | head -20

# Generate log for a specific Git repository with file output
./pyggg.py /path/to/git/repo /path/to/output/repo.git.txt

# Use with paths starting with '-' (requires -- separator)
./pyggg.py -- -weird/repo/path
```

## Graph Symbols

| Symbol | Meaning |
|--------|---------|
| `o` | Regular commit |
| `M` | Merge commit |
| `I` | Initial commit |
| `│` | Vertical branch line |
| `─` | Horizontal line |
| `┐` | Merge opening new branch |
| `┤` | Merge closing/joining branch |
| `┘` | Branch closure |
| `┼` | Line crossing |
| `├` | Branch fork |

## References

References appear with different delimiters:
- `[branch]` - Local branch (can include `/`, e.g., `[feature/login]`)
- `{remote/branch}` - Remote branch (e.g., `{origin/master}`)
- `<tag>` - Tag (e.g., `<1.0.0>`)

## Output Format

Each line follows this format:
```
<hash> <date> <author> <graph> <refs> <message>
```

- **Hash**: 7 characters of the SHA-1
- **Date**: Format `YYYY-MM-DD HH:MM` (always in UTC)
- **Author**: Author name
- **Graph**: ASCII visualization of commit tree
- **Refs**: Associated branches, tags, and remotes
- **Message**: Commit message

## Features

- 🎯 **100% Tig-compatible**: Uses the same Graph V2 algorithm
- 🎨 **Unicode symbols**: Box-drawing characters for clean graphs
- 📊 **Smart detection**: Distinguishes between different merge types
- 🔍 **Accurate**: Exactly replicates Tig's visualization logic

## Comparison with other tools

| Tool | Advantage |
|------|-----------|
| `git log --graph` | Simpler, basic ASCII |
| `tig` | Interactive, requires ncurses |
| **`pyGGG`** | **Non-interactive, stdout/file output, Tig format** |

## Troubleshooting

### Script can't find the repository
```bash
# Make sure the path points to a valid Git repository
git -C /path/to/repo status

# Or use the absolute path
python3 pyggg.py /Users/user/projects/my-repo
```

### Strange characters in output
Box-drawing symbols require UTF-8 terminal support. To view them correctly:
```bash
# In terminal
cat output.txt

# Or open the file with a UTF-8 compatible editor
```

## Credits

- Based on the Graph V2 algorithm from [Tig](https://github.com/jonas/tig)
- Python implementation by Miqui Infante
- Original Tig by Jonas Fonseca

## License

This project uses the same approach as Tig for Git graph visualization.
Tig is licensed under GPL v2.
