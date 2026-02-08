# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**pyGGG** (Python Git Graph Generator) is a Python implementation of Tig's Graph V2 algorithm. It generates Git logs with visual graph representation using Unicode box-drawing characters, matching Tig's exact output format.

## Installation

The project includes installation scripts:

```bash
./install.sh    # Installs ggg and gg commands to ~/.local/bin
./uninstall.sh  # Removes installed commands
```

**What gets installed:**
- `ggg` - Copy of pyggg.py, generates git graph to stdout
- `gg` - Wrapper script that pipes ggg output to `less -S`

After installation, the cloned repository can be deleted safely.

## Running the Script

### Installed commands (after ./install.sh):
```bash
ggg              # Current directory → stdout
ggg > out.txt    # Current directory → file
gg               # Current directory → less (interactive)
```

### Direct script usage:
```bash
./pyggg.py [repo_path] [output_file]

# No arguments: uses current directory, outputs to stdout
./pyggg.py
./pyggg.py > output.txt
./pyggg.py | head -20

# With repo path: outputs to stdout
./pyggg.py /path/to/any/git/repo

# With both: outputs to file
./pyggg.py /path/to/any/git/repo output.txt
```

**Argument logic:**
- 0 args: current directory → stdout
- 1 arg: specified repo → stdout (always treated as repo path, never as output file)
- 2 args: specified repo → specified file

## Testing the Script

To validate the script works correctly, run it on any Git repository and verify the output:

```bash
# Test on this repository itself
./pyggg.py

# Test on another repository and compare with tig
cd /path/to/test/repo
pyggg.py > pyggg_output.txt
tig --all  # Visual comparison (press Shift+X to toggle commit IDs)

# Or test from outside the repo
/path/to/pyggg.py /path/to/test/repo | diff - <(cd /path/to/test/repo && tig --all)
```

## Architecture

### Core Algorithm: Graph V2 from Tig

The implementation in `pyggg.py` is a line-by-line Python translation of Tig's `src/graph-v2.c`. Key characteristics:

**State Management:**
- Maintains 4 rows (prev_row, row, next_row, parents) for lookahead/lookback
- Uses 20 boolean flags per symbol for precise pattern detection
- 3-phase algorithm: Expand → Generate Next Row → Collapse

**Critical Symbol Detection:**
The most important distinction is between merge types:
- `M─┐` (merge opening) - detected by `symbol_merge()` - line 639
- `M─┤` (merge closing) - detected by `symbol_vertical_merge()` - line 579

The `symbol_vertical_merge()` function is THE KEY to accurate merge visualization. It checks `matches_commit` flag (whether the column contains the current commit ID) to distinguish closing merges from opening ones.

**Why Graph V2:**
- Graph V1 (~90% accuracy) was insufficient
- Graph V2 achieves 100% symbol accuracy through complex flag logic
- See lines 393-444 for the 20-flag symbol generation

### Reference Detection

Lines 771-815 implement smart reference parsing:
- Local branches: `[branch-name]` (can include `/`, e.g., `[feature/login]`)
- Remote branches: `{remote/branch}` (detected by known remote prefixes)
- Tags: `<version>`

Remote detection uses a known list: `origin`, `upstream`. If a ref has `/` but doesn't start with these, it's treated as a local branch with `/` in the name.

### Date Format

Lines 738-759: Uses commit date (`%ci`) not author date (`%ai`). All dates are converted to UTC and displayed as `YYYY-MM-DD HH:MM` (no seconds, no timezone suffix). The conversion happens using Python's `datetime.fromisoformat()` and `astimezone(timezone.utc)`.

### Git Log Ordering

Line 713: Uses `--topo-order` which is critical for the graph algorithm to work correctly.

## Tig Source Reference

This implementation is based on Tig's Graph V2 algorithm from `src/graph-v2.c`. If you need to reference the original C code or understand implementation details, clone the Tig repository:

```bash
git clone https://github.com/jonas/tig.git
cd tig/
make              # Build executable
```

Key files in Tig source:
- `src/graph-v2.c` - Original C implementation (THE reference for this Python port)
- `src/graph-v1.c` - Simpler but less accurate algorithm (not used)

## Key Implementation Notes

1. **Symbol Priority Matters**: The order of symbol detection functions (lines 486-521 and 524-560) must match Tig's logic exactly. Later checks have lower priority.

2. **Empty Columns**: The algorithm creates and removes empty columns dynamically. This is essential for proper graph layout.

3. **Color Assignment**: Uses least-recently-used color allocation (lines 104-123) to minimize visual confusion.

4. **Box Drawing vs UTF-8**: Two symbol sets available:
   - `symbol_to_box()` (line 524) - Standard box-drawing (used by default)
   - `symbol_to_utf8()` (line 486) - Rounded corners variant

## Repository Structure

```
pyGGG/
├── pyggg.py        # Main script (complete Graph V2 implementation)
├── install.sh      # Installation script (copies to ~/.local/bin)
├── uninstall.sh    # Uninstallation script
├── README.md       # User documentation
├── CLAUDE.md       # Development documentation
└── .gitignore
```

The script is self-contained and requires only Python 3.6+ and Git to run.

## Modifying the Algorithm

**WARNING**: The Graph V2 algorithm is extremely sensitive to changes. Even minor modifications to flag logic or detection order can break symbol accuracy.

If you need to modify symbol detection:
1. Clone Tig's source and read the corresponding C code in `src/graph-v2.c` first
2. Test thoroughly on various Git repositories with complex merge histories
3. Pay special attention to merge symbols (`M─┐` vs `M─┤`) as these are the most subtle
4. Compare output with `tig --all` to validate

The 20 flags (lines 22-52 in GraphSymbol class) form a complex interdependent system. Changing one flag's calculation often requires adjusting multiple symbol detection functions.
