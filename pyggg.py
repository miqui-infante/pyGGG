#!/usr/bin/env python3
"""
Exact replication of Tig's graph-v2.c algorithm in Python.
This follows the same logic, structures, and symbols as Tig's graph V2 code.

Generated with [Claude Code](https://claude.com/claude-code)

Based on the original C code from Tig's graph-v2.c - https://github.com/jonas/tig
"""

import subprocess
import sys
from typing import List, Optional
from dataclasses import dataclass, field


@dataclass
class GraphSymbol:
    """Replicates struct graph_symbol from graph-v2.c"""
    color: int = 0

    # Basic flags
    commit: bool = False
    boundary: bool = False
    initial: bool = False
    merge: bool = False

    # Continuation flags
    continued_down: bool = False
    continued_up: bool = False
    continued_right: bool = False
    continued_left: bool = False
    continued_up_left: bool = False

    # Parent flags
    parent_down: bool = False
    parent_right: bool = False

    # Position flags
    below_commit: bool = False
    flanked: bool = False
    next_right: bool = False
    matches_commit: bool = False

    # Shift flags
    shift_left: bool = False
    continue_shift: bool = False
    below_shift: bool = False

    # Column flags
    new_column: bool = False
    empty: bool = False


@dataclass
class GraphColumn:
    """Replicates struct graph_column from graph-v2.c"""
    symbol: GraphSymbol = field(default_factory=GraphSymbol)
    id: Optional[str] = None  # Parent SHA1 ID


@dataclass
class GraphRow:
    """Replicates struct graph_row from graph-v2.c"""
    columns: List[GraphColumn] = field(default_factory=list)

    @property
    def size(self) -> int:
        return len(self.columns)


@dataclass
class Commit:
    """Git commit data"""
    hash: str
    short_hash: str
    parents: List[str]
    author: str
    date: str
    timezone: str
    message: str
    refs: List[str]


class TigGraphV2:
    """Exact replication of Tig's graph-v2.c algorithm"""

    GRAPH_COLORS = 14

    def __init__(self):
        self.row = GraphRow()
        self.parents = GraphRow()
        self.prev_row = GraphRow()
        self.next_row = GraphRow()
        self.position = 0
        self.prev_position = 0
        self.expanded = 0
        self.id = ""
        self.has_parents = False
        self.is_boundary = False
        self.colors_map = {}  # Maps ID to color
        self.colors_count = [0] * self.GRAPH_COLORS

    def get_color(self, commit_id: Optional[str]) -> int:
        """Get color for commit ID"""
        if not commit_id:
            commit_id = ""

        if commit_id in self.colors_map:
            return self.colors_map[commit_id]

        # Find least-used color
        free_color = min(range(self.GRAPH_COLORS), key=lambda i: self.colors_count[i])
        self.colors_map[commit_id] = free_color
        self.colors_count[free_color] += 1
        return free_color

    def remove_color(self, commit_id: str):
        """Remove color mapping for commit ID"""
        if commit_id in self.colors_map:
            color = self.colors_map[commit_id]
            self.colors_count[color] -= 1
            del self.colors_map[commit_id]

    def column_has_commit(self, column: GraphColumn) -> bool:
        """Check if column has a commit"""
        return column.id is not None

    def find_column_by_id(self, row: GraphRow, commit_id: str) -> int:
        """Find column by commit ID"""
        free_column = row.size

        for i in range(row.size):
            if not self.column_has_commit(row.columns[i]) and free_column == row.size:
                free_column = i
            elif row.columns[i].id == commit_id:
                return i

        return free_column

    def find_free_column(self, row: GraphRow) -> int:
        """Find first free column"""
        for i in range(row.size):
            if not self.column_has_commit(row.columns[i]):
                return i
        return row.size

    def insert_column(self, row: GraphRow, pos: int, commit_id: Optional[str]) -> Optional[GraphColumn]:
        """Insert a column at position"""
        column = GraphColumn()
        column.id = commit_id
        column.symbol.boundary = self.is_boundary

        if pos < row.size:
            row.columns.insert(pos, column)
        else:
            row.columns.append(column)

        return column

    def add_parent(self, parent: Optional[str]) -> bool:
        """Add a parent to the parents list"""
        if self.has_parents:
            return True
        return self.insert_column(self.parents, self.parents.size, parent) is not None

    def needs_expansion(self) -> bool:
        """Check if we need to expand columns"""
        return self.position + self.parents.size > self.row.size

    def expand(self) -> bool:
        """Expand columns to fit parents"""
        while self.needs_expansion():
            if not self.insert_column(self.prev_row, self.prev_row.size, None):
                return False
            if not self.insert_column(self.row, self.row.size, None):
                return False
            if not self.insert_column(self.next_row, self.next_row.size, None):
                return False
        return True

    def needs_collapsing(self) -> bool:
        """Check if we need to collapse"""
        return (self.row.size > 1 and
                not self.column_has_commit(self.row.columns[self.row.size - 1]))

    def collapse(self) -> bool:
        """Remove empty trailing columns"""
        while self.needs_collapsing():
            self.prev_row.columns.pop()
            self.row.columns.pop()
            self.next_row.columns.pop()
        return True

    def row_clear_commit(self, row: GraphRow, commit_id: str):
        """Clear commit from row"""
        for i in range(row.size):
            if row.columns[i].id == commit_id:
                row.columns[i].id = None

    def commit_is_in_row(self, commit_id: str, row: GraphRow) -> bool:
        """Check if commit is in row"""
        for i in range(row.size):
            if self.column_has_commit(row.columns[i]) and row.columns[i].id == commit_id:
                return True
        return False

    def insert_parents(self):
        """Insert parents into next_row"""
        for i in range(self.parents.size):
            new = self.parents.columns[i]

            if self.column_has_commit(new):
                match = self.find_free_column(self.next_row)

                if match == self.next_row.size and self.column_has_commit(self.next_row.columns[self.next_row.size - 1]):
                    self.insert_column(self.next_row, self.next_row.size, new.id)
                    self.insert_column(self.row, self.row.size, None)
                    self.insert_column(self.prev_row, self.prev_row.size, None)
                else:
                    self.next_row.columns[match].id = new.id
                    self.next_row.columns[match].symbol = GraphSymbol(**vars(new.symbol))

    def remove_collapsed_columns(self):
        """Remove collapsed columns from next_row"""
        row = self.next_row

        for i in range(row.size - 1, 0, -1):
            if i == self.position:
                continue
            if i == self.position + 1:
                continue
            if row.columns[i].id == self.id:
                continue
            if row.columns[i].id != row.columns[i - 1].id:
                continue
            if self.commit_is_in_row(row.columns[i].id, self.parents) and not self.column_has_commit(self.prev_row.columns[i]):
                continue

            if row.columns[i - 1].id != self.prev_row.columns[i - 1].id or self.prev_row.columns[i - 1].symbol.shift_left:
                if i + 1 >= row.size:
                    row.columns[i] = GraphColumn()
                else:
                    row.columns[i] = GraphColumn(**vars(row.columns[i + 1]))

    def fill_empty_columns(self):
        """Fill empty columns in next_row"""
        row = self.next_row

        for i in range(row.size - 2, -1, -1):
            if not self.column_has_commit(row.columns[i]):
                row.columns[i] = GraphColumn(**vars(row.columns[i + 1]))

    def generate_next_row(self):
        """Generate the next row"""
        self.row_clear_commit(self.next_row, self.id)
        self.insert_parents()
        self.remove_collapsed_columns()
        self.fill_empty_columns()

    def commits_in_row(self, row: GraphRow) -> int:
        """Count commits in row"""
        count = 0
        for i in range(row.size):
            if self.column_has_commit(row.columns[i]):
                count += 1
        return count

    def commit_next_row(self):
        """Commit the next row to current row"""
        for i in range(self.row.size):
            self.prev_row.columns[i] = GraphColumn(**vars(self.row.columns[i]))

            if i == self.position and self.commits_in_row(self.parents) > 0:
                self.prev_row.columns[i] = GraphColumn(**vars(self.next_row.columns[i]))

            if not self.column_has_commit(self.prev_row.columns[i]):
                self.prev_row.columns[i] = GraphColumn(**vars(self.next_row.columns[i]))

            self.row.columns[i] = GraphColumn(**vars(self.next_row.columns[i]))

        self.prev_position = self.position

    # Symbol detection functions

    def continued_down(self, row: GraphRow, next_row: GraphRow, pos: int) -> bool:
        """Check if line continues down"""
        if row.columns[pos].id != next_row.columns[pos].id:
            return False
        if row.columns[pos].symbol.shift_left:
            return False
        return True

    def shift_left(self, row: GraphRow, prev_row: GraphRow, pos: int) -> bool:
        """Check if position shifts left"""
        if not self.column_has_commit(row.columns[pos]):
            return False

        for i in range(pos - 1, -1, -1):
            if not self.column_has_commit(row.columns[i]):
                continue
            if row.columns[i].id != row.columns[pos].id:
                continue
            if not self.continued_down(prev_row, row, i):
                return True
            break

        return False

    def new_column(self, row: GraphRow, prev_row: GraphRow, pos: int) -> bool:
        """Check if this is a new column"""
        if not self.column_has_commit(prev_row.columns[pos]):
            return True

        for i in range(pos, row.size):
            if row.columns[pos].id == prev_row.columns[i].id:
                return False

        return True

    def continued_right(self, row: GraphRow, pos: int, commit_pos: int) -> bool:
        """Check if line continues right"""
        if pos < commit_pos:
            end = commit_pos
        else:
            end = row.size

        for i in range(pos + 1, end):
            if row.columns[pos].id == row.columns[i].id:
                return True

        return False

    def continued_left(self, row: GraphRow, pos: int, commit_pos: int) -> bool:
        """Check if line continues left"""
        if pos < commit_pos:
            start = 0
        else:
            start = commit_pos

        for i in range(start, pos):
            if not self.column_has_commit(row.columns[i]):
                continue
            if row.columns[pos].id == row.columns[i].id:
                return True

        return False

    def parent_down(self, parents: GraphRow, next_row: GraphRow, pos: int) -> bool:
        """Check if parent goes down"""
        for parent in range(parents.size):
            if not self.column_has_commit(parents.columns[parent]):
                continue
            if parents.columns[parent].id == next_row.columns[pos].id:
                return True
        return False

    def parent_right(self, parents: GraphRow, row: GraphRow, next_row: GraphRow, pos: int) -> bool:
        """Check if parent goes right"""
        for parent in range(parents.size):
            if not self.column_has_commit(parents.columns[parent]):
                continue

            for i in range(pos + 1, next_row.size):
                if parents.columns[parent].id != next_row.columns[i].id:
                    continue
                if parents.columns[parent].id != row.columns[i].id:
                    return True

        return False

    def flanked(self, row: GraphRow, pos: int, commit_pos: int, commit_id: str) -> bool:
        """Check if position is flanked by commit"""
        if pos < commit_pos:
            start, end = 0, pos
        else:
            start, end = pos + 1, row.size

        for i in range(start, end):
            if row.columns[i].id == commit_id:
                return True

        return False

    def below_commit(self, pos: int) -> bool:
        """Check if position is below commit"""
        if pos != self.prev_position:
            return False
        if self.row.columns[pos].id != self.prev_row.columns[pos].id:
            return False
        return True

    def generate_symbols(self, canvas_symbols: List[GraphSymbol]):
        """Generate symbols for current row"""
        commits = self.commits_in_row(self.parents)
        initial = commits < 1
        merge = commits > 1

        for pos in range(self.row.size):
            column = self.row.columns[pos]
            symbol = GraphSymbol()
            commit_id = self.next_row.columns[pos].id

            # Basic flags
            symbol.commit = (pos == self.position)
            symbol.boundary = (pos == self.position and self.next_row.columns[pos].symbol.boundary)
            symbol.initial = initial
            symbol.merge = merge

            # Continuation flags
            symbol.continued_down = self.continued_down(self.row, self.next_row, pos)
            symbol.continued_up = self.continued_down(self.prev_row, self.row, pos)
            symbol.continued_right = self.continued_right(self.row, pos, self.position)
            symbol.continued_left = self.continued_left(self.row, pos, self.position)
            symbol.continued_up_left = self.continued_left(self.prev_row, pos, self.prev_row.size)

            # Parent flags
            symbol.parent_down = self.parent_down(self.parents, self.next_row, pos)
            symbol.parent_right = (pos > self.position and self.parent_right(self.parents, self.row, self.next_row, pos))

            # Position flags
            symbol.below_commit = self.below_commit(pos)
            symbol.flanked = self.flanked(self.row, pos, self.position, self.id)
            symbol.next_right = self.continued_right(self.next_row, pos, 0)
            symbol.matches_commit = column.id == self.id

            # Shift flags
            symbol.shift_left = self.shift_left(self.row, self.prev_row, pos)
            symbol.continue_shift = self.shift_left(self.row, self.prev_row, pos + 1) if pos + 1 < self.row.size else False
            symbol.below_shift = self.prev_row.columns[pos].symbol.shift_left

            # Column flags
            symbol.new_column = self.new_column(self.row, self.prev_row, pos)
            symbol.empty = not self.column_has_commit(self.row.columns[pos])

            # Color
            if self.column_has_commit(column):
                commit_id = column.id
            symbol.color = self.get_color(commit_id)

            canvas_symbols.append(symbol)

        self.remove_color(self.id)

    def add_commit(self, commit_id: str, parent_ids: List[str], is_boundary: bool = False):
        """Add a commit to the graph"""
        self.position = self.find_column_by_id(self.row, commit_id)
        self.id = commit_id
        self.is_boundary = is_boundary
        self.has_parents = False

        # Add all parents
        has_parents = 0
        for parent in parent_ids:
            if not self.add_parent(parent):
                return False
            has_parents += 1

        self.has_parents = has_parents > 0

        return True

    def render_parents(self, canvas_symbols: List[GraphSymbol]) -> bool:
        """Render the graph"""
        if self.parents.size == 0:
            if not self.add_parent(None):
                return False

        if not self.expand():
            return False

        self.generate_next_row()
        self.generate_symbols(canvas_symbols)
        self.commit_next_row()

        self.parents = GraphRow()
        self.position = 0

        if not self.collapse():
            return False

        return True

    # Symbol to character conversion functions (matching graph-v2.c exactly)

    def symbol_to_utf8(self, symbol: GraphSymbol) -> str:
        """Convert symbol to UTF-8 characters (rounded corners)"""
        if symbol.commit:
            if symbol.boundary:
                return ' ◯'
            elif symbol.initial:
                return ' ◎'
            elif symbol.merge:
                return ' ●'
            return ' ∙'

        if self.symbol_cross_merge(symbol):
            return '─┼'
        if self.symbol_vertical_merge(symbol):
            return '─┤'
        if self.symbol_cross_over(symbol):
            return '─│'
        if self.symbol_vertical_bar(symbol):
            return ' │'
        if self.symbol_turn_left(symbol):
            return '─╯'
        if self.symbol_multi_branch(symbol):
            return '─┴'
        if self.symbol_horizontal_bar(symbol):
            return '──'
        if self.symbol_forks(symbol):
            return ' ├'
        if self.symbol_turn_down_cross_over(symbol):
            return '─╭'
        if self.symbol_turn_down(symbol):
            return ' ╭'
        if self.symbol_merge(symbol):
            return '─╮'
        if self.symbol_multi_merge(symbol):
            return '─┬'

        return '  '

    def symbol_to_box(self, symbol: GraphSymbol) -> str:
        """Convert symbol to standard box-drawing characters (matching Tig chtype output)"""
        if symbol.commit:
            if symbol.boundary:
                return ' o'
            elif symbol.initial:
                return ' I'
            elif symbol.merge:
                return ' M'
            return ' o'

        if self.symbol_cross_merge(symbol):
            return '─┼'
        if self.symbol_vertical_merge(symbol):
            return '─┤'
        if self.symbol_cross_over(symbol):
            return '─│'
        if self.symbol_vertical_bar(symbol):
            return ' │'
        if self.symbol_turn_left(symbol):
            return '─┘'
        if self.symbol_multi_branch(symbol):
            return '─┴'
        if self.symbol_horizontal_bar(symbol):
            return '──'
        if self.symbol_forks(symbol):
            return ' ├'
        if self.symbol_turn_down_cross_over(symbol):
            return '─┌'
        if self.symbol_turn_down(symbol):
            return ' ┌'
        if self.symbol_merge(symbol):
            return '─┐'
        if self.symbol_multi_merge(symbol):
            return '─┬'

        return '  '

    def symbol_forks(self, symbol: GraphSymbol) -> bool:
        return (symbol.continued_down and symbol.continued_right and symbol.continued_up)

    def symbol_cross_merge(self, symbol: GraphSymbol) -> bool:
        if symbol.empty:
            return False
        if not symbol.continued_up and not symbol.new_column and not symbol.below_commit:
            return False
        if symbol.shift_left and symbol.continued_up_left:
            return False
        if symbol.next_right:
            return False
        if (symbol.merge and symbol.continued_up and symbol.continued_right and
            symbol.continued_left and symbol.parent_down and not symbol.next_right):
            return True
        return False

    def symbol_vertical_merge(self, symbol: GraphSymbol) -> bool:
        """This is the KEY function for M─┤ detection"""
        if symbol.empty:
            return False
        if not symbol.continued_up and not symbol.new_column and not symbol.below_commit:
            return False
        if symbol.shift_left and symbol.continued_up_left:
            return False
        if symbol.next_right:
            return False
        if not symbol.matches_commit:
            return False
        if (symbol.merge and symbol.continued_up and symbol.continued_left and
            symbol.parent_down and not symbol.continued_right):
            return True
        return False

    def symbol_cross_over(self, symbol: GraphSymbol) -> bool:
        if symbol.empty:
            return False
        if not symbol.continued_down:
            return False
        if not symbol.continued_up and not symbol.new_column and not symbol.below_commit:
            return False
        if symbol.shift_left:
            return False
        if symbol.parent_right and symbol.merge:
            return True
        if symbol.flanked:
            return True
        return False

    def symbol_turn_left(self, symbol: GraphSymbol) -> bool:
        if symbol.matches_commit and symbol.continued_right and not symbol.continued_down:
            return False
        if symbol.continue_shift:
            return False
        if symbol.continued_up or symbol.new_column or symbol.below_commit:
            if symbol.matches_commit:
                return True
            if symbol.shift_left:
                return True
        return False

    def symbol_turn_down_cross_over(self, symbol: GraphSymbol) -> bool:
        if not symbol.continued_down:
            return False
        if not symbol.continued_right:
            return False
        if not symbol.parent_right and not symbol.flanked:
            return False
        if symbol.flanked:
            return True
        if symbol.merge:
            return True
        return False

    def symbol_turn_down(self, symbol: GraphSymbol) -> bool:
        return symbol.continued_down and symbol.continued_right

    def symbol_merge(self, symbol: GraphSymbol) -> bool:
        return (not symbol.continued_down and symbol.parent_down and
                not symbol.parent_right and not symbol.continued_right)

    def symbol_multi_merge(self, symbol: GraphSymbol) -> bool:
        if not symbol.parent_down:
            return False
        if not symbol.parent_right and not symbol.continued_right:
            return False
        return True

    def symbol_vertical_bar(self, symbol: GraphSymbol) -> bool:
        if symbol.empty:
            return False
        if symbol.shift_left:
            return False
        if not symbol.continued_down:
            return False
        if symbol.continued_up:
            return True
        if symbol.parent_right:
            return False
        if symbol.flanked:
            return False
        if symbol.continued_right:
            return False
        return True

    def symbol_horizontal_bar(self, symbol: GraphSymbol) -> bool:
        if not symbol.next_right:
            return False
        if symbol.shift_left:
            return True
        if symbol.continued_down:
            return False
        if not symbol.parent_right and not symbol.continued_right:
            return False
        if symbol.continued_up and not symbol.continued_up_left:
            return False
        if not symbol.below_commit:
            return True
        return False

    def symbol_multi_branch(self, symbol: GraphSymbol) -> bool:
        if symbol.continued_down:
            return False
        if not symbol.continued_right:
            return False
        if symbol.below_shift:
            return False
        if symbol.continued_up or symbol.new_column or symbol.below_commit:
            if symbol.matches_commit:
                return True
            if symbol.shift_left:
                return True
        return False


class TigStyleRendererV2:
    """Main renderer using TigGraphV2 algorithm"""

    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.graph = TigGraphV2()

    def run_git(self, args: List[str]) -> str:
        """Execute git command"""
        cmd = ['git', '-C', self.repo_path] + args
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout

    def get_commits(self) -> List[Commit]:
        """Get all commits"""
        output = self.run_git([
            'log', '--all', '--topo-order',
            '--pretty=format:%H%n%P%n%an%n%ci%n%s%n%d%n---END---'
        ])

        commits = []
        lines = output.split('\n')
        i = 0

        while i < len(lines):
            if i + 5 >= len(lines):
                break

            hash_full = lines[i].strip()
            if not hash_full:
                i += 1
                continue

            parents_line = lines[i + 1].strip()
            parents = parents_line.split() if parents_line else []
            author = lines[i + 2].strip()
            date_line = lines[i + 3].strip()
            message = lines[i + 4].strip()
            refs_line = lines[i + 5].strip()

            # Parse date
            date_parts = date_line.split()
            if len(date_parts) >= 2:
                date_str = date_parts[0]
                time_parts = date_parts[1].split(':')
                time_str = f"{time_parts[0]}:{time_parts[1]}" if len(time_parts) >= 2 else date_parts[1]
                date = f"{date_str} {time_str}"
                timezone = date_parts[2] if len(date_parts) > 2 else '+0000'
            else:
                date = date_line
                timezone = '+0000'

            # Parse refs
            refs = self._parse_refs(refs_line)

            commit = Commit(
                hash=hash_full,
                short_hash=hash_full[:7],
                parents=parents,
                author=author,
                date=date,
                timezone=timezone,
                message=message,
                refs=refs
            )

            commits.append(commit)

            while i < len(lines) and lines[i].strip() != '---END---':
                i += 1
            i += 1

        return commits

    def _parse_refs(self, refs_line: str) -> List[str]:
        """Parse and format references"""
        if not refs_line or refs_line == '---END---':
            return []

        refs_line = refs_line.strip()
        if refs_line.startswith('(') and refs_line.endswith(')'):
            refs_line = refs_line[1:-1]

        if not refs_line:
            return []

        local_branches = []
        remote_branches = []
        tags = []

        # Common remote names. Actually we will always find 'origin'
        common_remotes = {'origin', 'upstream'}  # , 'fork', 'github', 'gitlab', 'bitbucket'}

        for ref in refs_line.split(','):
            ref = ref.strip()
            if not ref:
                continue

            if ref.startswith('tag: '):
                tags.append(f'<{ref[5:].strip()}>')
            elif 'HEAD ->' in ref:
                # Extract the branch name from "HEAD -> branch"
                branch = ref.split('->')[1].strip()
                local_branches.append(f'[{branch}]')
            elif ref == 'HEAD':
                continue
            elif '/' in ref:
                # Check if it's a remote reference by examining the prefix
                ref_parts = ref.split('/', 1)
                if ref_parts[0] in common_remotes:
                    # This is a remote reference (e.g., origin/master)
                    remote_branches.append(f'{{{ref}}}')
                else:
                    # This is a local branch with / in the name (e.g., feature/login)
                    local_branches.append(f'[{ref}]')
            else:
                local_branches.append(f'[{ref}]')

        return local_branches + remote_branches + tags

    def render(self) -> str:
        """Render the complete log"""
        commits = self.get_commits()
        output_lines = []

        # Calculate max author length
        max_author_len = min(max((len(c.author) for c in commits), default=20), 40)

        for commit in commits:
            # Add commit to graph
            self.graph.add_commit(commit.hash, commit.parents, is_boundary=False)

            # Render graph for this commit
            canvas_symbols = []
            self.graph.render_parents(canvas_symbols)

            # Convert symbols to string (use symbol_to_box for standard box-drawing chars)
            graph_str = ''.join(self.graph.symbol_to_box(sym) for sym in canvas_symbols).rstrip()

            # Format output line
            author = commit.author[:max_author_len].ljust(max_author_len)
            refs_str = ' ' + ' '.join(commit.refs) if commit.refs else ''
            line = f"{commit.short_hash} {commit.date} {commit.timezone} {author} {graph_str}{refs_str} {commit.message}"
            output_lines.append(line)

        return '\n'.join(output_lines)

    def render_to_file(self, output_path: str):
        """Render to file"""
        output = self.render()
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output)
            f.writelines('\n')  # Ensure final newline


def main():
    if len(sys.argv) < 2:
        print("Usage: python tig_graph_v2.py <repo_path> [output_file]", file=sys.stderr)
        sys.exit(1)

    repo_path = sys.argv[1]
    renderer = TigStyleRendererV2(repo_path)

    if len(sys.argv) > 2:
        # Output to file
        output_file = sys.argv[2]
        renderer.render_to_file(output_file)
    else:
        # Output to stdout
        output = renderer.render()
        print(output)


if __name__ == '__main__':
    main()
