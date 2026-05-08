import pygame
import sys
import random
from collections import deque

# -------------------------------
# Constants & Configuration
# -------------------------------
R = 20                # rows
C = 20                # columns
CELL_SIZE = 30        # pixels per cell
WIDTH = C * CELL_SIZE
HEIGHT = R * CELL_SIZE
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (255, 0, 0)
BLUE  = (0, 0, 255)
GREEN = (0, 255, 0)
GRAY  = (200, 200, 200)

# Speed of animation (milliseconds per wall removal)
GENERATION_DELAY = 20
SOLVER_DELAY = 50

# Bonus: create extra cycles (remove 5% of walls after generation)
BONUS_CYCLES = True
EXTRA_WALL_REMOVE_PROB = 0.05

# -------------------------------
# Maze Data Structures
# -------------------------------
# northWall[r][c] = True  -> solid wall above cell (r,c)
# eastWall[r][c]  = True  -> solid wall to the right of cell (r,c)
northWall = [[True for _ in range(C)] for _ in range(R)]
eastWall  = [[True for _ in range(C)] for _ in range(R)]

# Visited array for generation
visited_gen = [[False for _ in range(C)] for _ in range(R)]

# Start and end positions (left edge & right edge)
start_pos = (0, 0)   # will be set later
end_pos   = (0, 0)

# -------------------------------
# Utility Functions
# -------------------------------
def remove_wall_between(cell_a, cell_b):
    """
    Remove the wall between two adjacent cells.
    cell_a and cell_b are tuples (r,c).
    """
    r1, c1 = cell_a
    r2, c2 = cell_b
    if r1 == r2:  # same row -> horizontal neighbours (left/right)
        if c1 < c2:
            # cell_a is left, cell_b is right -> remove east wall of a
            eastWall[r1][c1] = False
        else:
            eastWall[r2][c2] = False
    elif c1 == c2:  # same column -> vertical neighbours (up/down)
        if r1 < r2:
            # cell_a is above, cell_b is below -> remove north wall of b
            northWall[r2][c1] = False
        else:
            northWall[r1][c1] = False

def get_unvisited_neighbors(r, c):
    """Return list of neighbor positions that are inside grid and not visited during generation."""
    neighbors = []
    # Up
    if r > 0 and not visited_gen[r-1][c]:
        neighbors.append((r-1, c))
    # Down
    if r < R-1 and not visited_gen[r+1][c]:
        neighbors.append((r+1, c))
    # Left
    if c > 0 and not visited_gen[r][c-1]:
        neighbors.append((r, c-1))
    # Right
    if c < C-1 and not visited_gen[r][c+1]:
        neighbors.append((r, c+1))
    return neighbors

def draw_maze(screen, show_start_end=True):
    """Draw all walls (north and east) and optionally start/end markers."""
    screen.fill(WHITE)

    # Draw north walls and east walls
    for r in range(R):
        for c in range(C):
            x = c * CELL_SIZE
            y = r * CELL_SIZE
            if northWall[r][c]:
                pygame.draw.line(screen, BLACK, (x, y), (x + CELL_SIZE, y), 2)
            if eastWall[r][c]:
                pygame.draw.line(screen, BLACK, (x + CELL_SIZE, y), (x + CELL_SIZE, y + CELL_SIZE), 2)

    # Draw south and west boundaries (outer walls)
    # Bottom boundary: south walls of last row are drawn as north walls of phantom row
    for c in range(C):
        pygame.draw.line(screen, BLACK, (c*CELL_SIZE, HEIGHT), ((c+1)*CELL_SIZE, HEIGHT), 2)
    # Right boundary
    for r in range(R):
        pygame.draw.line(screen, BLACK, (WIDTH, r*CELL_SIZE), (WIDTH, (r+1)*CELL_SIZE), 2)
    # Left boundary (except where start gap is) – draw but solver knows start is open
    for r in range(R):
        pygame.draw.line(screen, BLACK, (0, r*CELL_SIZE), (0, (r+1)*CELL_SIZE), 2)
    # Top boundary
    for c in range(C):
        pygame.draw.line(screen, BLACK, (c*CELL_SIZE, 0), ((c+1)*CELL_SIZE, 0), 2)

    if show_start_end:
        # Mark start (left edge) with a small green square
        sr, sc = start_pos
        sx = sc * CELL_SIZE + 2
        sy = sr * CELL_SIZE + 2
        pygame.draw.rect(screen, GREEN, (sx, sy, CELL_SIZE-4, CELL_SIZE-4))
        # Mark end (right edge) with a small green square
        er, ec = end_pos
        ex = ec * CELL_SIZE + 2
        ey = er * CELL_SIZE + 2
        pygame.draw.rect(screen, GREEN, (ex, ey, CELL_SIZE-4, CELL_SIZE-4))

    pygame.display.flip()

def draw_circle_at(screen, pos, color):
    """Draw a filled circle at the center of cell 'pos' (r,c)."""
    r, c = pos
    center_x = c * CELL_SIZE + CELL_SIZE // 2
    center_y = r * CELL_SIZE + CELL_SIZE // 2
    pygame.draw.circle(screen, color, (center_x, center_y), CELL_SIZE // 3)

def generate_maze(screen, clock):
    """
    Randomized DFS (stack) maze generation.
    Returns True when finished.
    """
    # Reset walls and visited
    for r in range(R):
        for c in range(C):
            northWall[r][c] = True
            eastWall[r][c] = True
            visited_gen[r][c] = False

    # Choose random starting cell
    r = random.randrange(R)
    c = random.randrange(C)
    visited_gen[r][c] = True
    stack = [(r, c)]

    while stack:
        current = stack[-1]
        r, c = current
        neighbors = get_unvisited_neighbors(r, c)
        if neighbors:
            # Choose a random unvisited neighbor
            next_cell = random.choice(neighbors)
            remove_wall_between(current, next_cell)
            nr, nc = next_cell
            visited_gen[nr][nc] = True
            stack.append(next_cell)

            # Animate
            draw_maze(screen, show_start_end=False)
            pygame.time.delay(GENERATION_DELAY)
            clock.tick(FPS)
        else:
            # Dead end -> backtrack
            stack.pop()

    # All cells visited -> maze is a spanning tree.
    return True

def solve_maze_mouse(screen, clock):
    """
    Backtracking solver using a stack.
    Red dot = current position, Blue dot = dead end.
    Returns path (list of positions) if found, else None.
    """
    # Reset solver visited (different from generation visited)
    visited_solver = [[False for _ in range(C)] for _ in range(R)]
    stack = [start_pos]
    visited_solver[start_pos[0]][start_pos[1]] = True
    current = start_pos

    while stack:
        r, c = current
        # Draw current as red dot
        draw_maze(screen, show_start_end=True)
        draw_circle_at(screen, current, RED)
        pygame.display.flip()
        pygame.time.delay(SOLVER_DELAY)
        clock.tick(FPS)

        if current == end_pos:
            # Found exit
            return stack  # path

        # Try all four directions (order: up, right, down, left)
        # Check for no wall between current and neighbor
        moved = False
        # Up
        if r > 0 and not northWall[r][c] and not visited_solver[r-1][c]:
            next_cell = (r-1, c)
            visited_solver[next_cell[0]][next_cell[1]] = True
            stack.append(next_cell)
            current = next_cell
            moved = True
        # Right
        elif c < C-1 and not eastWall[r][c] and not visited_solver[r][c+1]:
            next_cell = (r, c+1)
            visited_solver[next_cell[0]][next_cell[1]] = True
            stack.append(next_cell)
            current = next_cell
            moved = True
        # Down
        elif r < R-1 and not northWall[r+1][c] and not visited_solver[r+1][c]:
            next_cell = (r+1, c)
            visited_solver[next_cell[0]][next_cell[1]] = True
            stack.append(next_cell)
            current = next_cell
            moved = True
        # Left
        elif c > 0 and not eastWall[r][c-1] and not visited_solver[r][c-1]:
            next_cell = (r, c-1)
            visited_solver[next_cell[0]][next_cell[1]] = True
            stack.append(next_cell)
            current = next_cell
            moved = True

        if not moved:
            # Dead end: mark blue, backtrack
            draw_circle_at(screen, current, BLUE)
            pygame.display.flip()
            pygame.time.delay(SOLVER_DELAY)
            stack.pop()
            if stack:
                current = stack[-1]
            else:
                return None  # no path (should not happen in a proper maze)
    return None

def add_extra_walls():
    """Bonus: remove some existing walls (with probability) to create cycles."""
    if not BONUS_CYCLES:
        return
    for r in range(R):
        for c in range(C):
            # Remove north wall with probability (except top boundary)
            if r > 0 and random.random() < EXTRA_WALL_REMOVE_PROB:
                northWall[r][c] = False
            # Remove east wall with probability (except right boundary)
            if c < C-1 and random.random() < EXTRA_WALL_REMOVE_PROB:
                eastWall[r][c] = False

def left_hand_rule_solve(screen, clock):
    """
    Implement the 'shoulder-to-the-wall' (left-hand rule) solver.
    Returns True if it reaches the end, False if it loops indefinitely (simplified detection).
    Note: This is for demonstration of the bonus; it may fail when cycles exist.
    """
    # Directions: 0=up, 1=right, 2=down, 3=left
    direction = 1  # start facing right (towards interior from left edge)
    r, c = start_pos
    visited_states = set()  # to detect loops
    steps = 0
    max_steps = R*C*4

    while (r, c) != end_pos and steps < max_steps:
        draw_maze(screen, show_start_end=True)
        draw_circle_at(screen, (r, c), RED)
        pygame.display.flip()
        pygame.time.delay(50)
        clock.tick(FPS)

        state = (r, c, direction)
        if state in visited_states:
            # Likely in a cycle -> cannot reach exit
            return False
        visited_states.add(state)

        # Try left, forward, right, backward in that order
        # directions: left = (direction - 1) % 4, forward = direction, etc.
        for turn in [-1, 0, 1, 2]:  # left, straight, right, back
            new_dir = (direction + turn) % 4
            dr, dc = [( -1, 0), (0, 1), (1, 0), (0, -1)][new_dir]
            nr, nc = r + dr, c + dc
            if nr < 0 or nr >= R or nc < 0 or nc >= C:
                continue
            # Check wall between (r,c) and (nr,nc)
            blocked = False
            if dr == -1:  # up
                if northWall[r][c]:
                    blocked = True
            elif dr == 1:  # down
                if northWall[nr][nc]:
                    blocked = True
            elif dc == 1:  # right
                if eastWall[r][c]:
                    blocked = True
            elif dc == -1:  # left
                if eastWall[nr][nc]:
                    blocked = True
            if not blocked:
                r, c = nr, nc
                direction = new_dir
                break
        steps += 1

    return (r, c) == end_pos

# -------------------------------
# Main Program
# -------------------------------
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Maze Generator & Solver")
    clock = pygame.time.Clock()

    # Choose start on left edge (column 0) and end on right edge (column C-1)
    global start_pos, end_pos
    start_pos = (random.randrange(R), 0)
    end_pos   = (random.randrange(R), C-1)

    # Phase 1: Generate proper maze (spanning tree)
    print("Generating maze (mouse eating walls)...")
    generate_maze(screen, clock)
    print("Generation finished. Press any key to start solver...")
    # Wait for user to watch the final maze
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting = False
        clock.tick(FPS)

    # Phase 2: Solve the maze with backtracking (red/blue dots)
    print("Solving maze with backtracking (red dot = current, blue = dead end)...")
    path = solve_maze_mouse(screen, clock)
    if path:
        print(f"Path found! Length: {len(path)} steps.")
    else:
        print("No path found (should not happen in a proper maze).")

    # Phase 3: Bonus - add cycles and show left-hand rule failure
    if BONUS_CYCLES:
        print("\n--- BONUS: Adding extra walls (cycles) ---")
        add_extra_walls()
        print("Maze now contains cycles. Re-drawing...")
        draw_maze(screen, show_start_end=True)
        pygame.display.flip()
        pygame.time.delay(2000)

        print("Now running 'left-hand rule' solver on cyclic maze...")
        success = left_hand_rule_solve(screen, clock)
        if success:
            print("Left-hand rule reached the exit (unlikely with cycles).")
        else:
            print("Left-hand rule FAILED to reach exit (stuck in a cycle or dead end).")
        print("This demonstrates that adding cycles defeats the simple shoulder-to-the-wall method.")

        # Also show that backtracking solver still works (optional)
        print("\nHowever, backtracking solver still works on the cyclic maze:")
        path2 = solve_maze_mouse(screen, clock)
        if path2:
            print("Backtracking solver succeeded again.")
        else:
            print("Backtracking solver also failed (should not happen).")

    # Wait for user to close
    print("\nDone. Close the window to exit.")
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        clock.tick(FPS)

if __name__ == "__main__":
    main()