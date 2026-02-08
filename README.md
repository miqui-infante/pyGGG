# pyGGG - Python Git Graph Generator

Python script that generates Git logs with graph visualization in [Tig](https://github.com/jonas/tig) format, using Unicode box-drawing characters.

## What does it do?

Converts Git repository history into a visual log with:
- ✨ ASCII art graph showing branches and merges
- 📅 Formatted dates
- 👤 Authors
- 🏷️ References (branches, tags, remotes)
- 💬 Commit messages

## Example Output

```
2ebf7c2 2025-12-19 15:31 +0100 miqui                      o [develop] {origin/develop} chore: bump version
d3e2e5e 2025-12-19 15:02 +0100 Miqui Infante              M─┐ [master] {origin/master} <1.9.0> Merge pull request #14
4328f73 2025-12-19 14:56 +0100 miqui                      │ o feat: add capy new MVN type
d226456 2025-11-25 18:33 +0100 Miqui Infante              M─┤ <1.8.0> Merge pull request #13
3345d78 2025-11-25 18:29 +0100 miqui                      │ o chore: bump version
6cbc8ac 2025-11-25 18:26 +0100 Javier Lahoz               M─┤ Merge pull request #12
```

## Installation

No installation required. You only need Python 3.6+ and Git.

## Usage

```bash
./pyggg.py [repo_path] [output_file]
```

- If no arguments provided: uses current directory as repo, outputs to stdout
- If `repo_path` provided: uses that repository, outputs to stdout
- If both provided: uses `repo_path` as repo, outputs to `output_file`

### Examples

```bash
# Generate log for current repository. Output to stdout. No arguments needed!
./pyggg.py

# Output to stdout with redirection
./pyggg.py > git_log.txt

# Pipe to other commands
./pyggg.py | head -20

# Generate log for a specific Git repository with file output
./pyggg.py /path/to/git/repo /path/to/output/repo.git.txt
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
<hash> <date> <timezone> <author> <graph> <refs> <message>
```

- **Hash**: 7 characters of the SHA-1
- **Date**: Format `YYYY-MM-DD HH:MM`
- **Timezone**: Format `+HHMM` or `-HHMM`
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
- Python implementation by Miguel Infante
- Original Tig by Jonas Fonseca

## License

This project uses the same approach as Tig for Git graph visualization.
Tig is licensed under GPL v2.
