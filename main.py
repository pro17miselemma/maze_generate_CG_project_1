import pygame
import sys
import random

R = 20
C = 20
CELL_SIZE = 30
WIDTH = C * CELL_SIZE
HEIGHT = R * CELL_SIZE

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

GENERATION_DELAY = 20
SOLVER_DELAY = 50

northWall = [[True for _ in range(C)] for _ in range(R)]
eastWall = [[True for _ in range(C)] for _ in range(R)]
visited_gen = [[False for _ in range(C)] for _ in range(R)]

start_pos = (0, 0)
end_pos = (0, 0)

def remove_wall_between(cell_a, cell_b):
    r1, c1 = cell_a
    r2, c2 = cell_b
    if r1 == r2:
        if c1 < c2:
            eastWall[r1][c1] = False
        else:
            eastWall[r2][c2] = False
    elif c1 == c2:
        if r1 < r2:
            northWall[r2][c1] = False
        else:
            northWall[r1][c1] = False

def get_unvisited_neighbors(r, c):
    neighbors = []
    if r > 0 and not visited_gen[r-1][c]:
        neighbors.append((r-1, c))
    if r < R-1 and not visited_gen[r+1][c]:
        neighbors.append((r+1, c))
    if c > 0 and not visited_gen[r][c-1]:
        neighbors.append((r, c-1))
    if c < C-1 and not visited_gen[r][c+1]:
        neighbors.append((r, c+1))
    return neighbors

def draw_maze(screen):
    screen.fill(WHITE)
    for r in range(R):
        for c in range(C):
            x = c * CELL_SIZE
            y = r * CELL_SIZE
            if northWall[r][c]:
                pygame.draw.line(screen, BLACK, (x, y), (x + CELL_SIZE, y), 2)
            if eastWall[r][c]:
                pygame.draw.line(screen, BLACK, (x + CELL_SIZE, y), (x + CELL_SIZE, y + CELL_SIZE), 2)
    for c in range(C):
        pygame.draw.line(screen, BLACK, (c*CELL_SIZE, HEIGHT), ((c+1)*CELL_SIZE, HEIGHT), 2)
        pygame.draw.line(screen, BLACK, (c*CELL_SIZE, 0), ((c+1)*CELL_SIZE, 0), 2)
    for r in range(R):
        pygame.draw.line(screen, BLACK, (WIDTH, r*CELL_SIZE), (WIDTH, (r+1)*CELL_SIZE), 2)
        pygame.draw.line(screen, BLACK, (0, r*CELL_SIZE), (0, (r+1)*CELL_SIZE), 2)
    pygame.display.flip()

def draw_circle_at(screen, pos, color):
    r, c = pos
    cx = c * CELL_SIZE + CELL_SIZE // 2
    cy = r * CELL_SIZE + CELL_SIZE // 2
    pygame.draw.circle(screen, color, (cx, cy), CELL_SIZE // 3)

def generate_maze(screen, clock):
    for r in range(R):
        for c in range(C):
            northWall[r][c] = True
            eastWall[r][c] = True
            visited_gen[r][c] = False
    r = random.randrange(R)
    c = random.randrange(C)
    visited_gen[r][c] = True
    stack = [(r, c)]
    while stack:
        current = stack[-1]
        r, c = current
        neighbors = get_unvisited_neighbors(r, c)
        if neighbors:
            next_cell = random.choice(neighbors)
            remove_wall_between(current, next_cell)
            nr, nc = next_cell
            visited_gen[nr][nc] = True
            stack.append(next_cell)
            draw_maze(screen)
            pygame.time.delay(GENERATION_DELAY)
            clock.tick(60)
        else:
            stack.pop()

def solve_maze(screen, clock):
    visited_solver = [[False for _ in range(C)] for _ in range(R)]
    stack = [start_pos]
    visited_solver[start_pos[0]][start_pos[1]] = True
    current = start_pos
    while stack:
        r, c = current
        draw_maze(screen)
        draw_circle_at(screen, current, RED)
        pygame.display.flip()
        pygame.time.delay(SOLVER_DELAY)
        clock.tick(60)
        if current == end_pos:
            return
        moved = False
        if r > 0 and not northWall[r][c] and not visited_solver[r-1][c]:
            next_cell = (r-1, c)
            visited_solver[next_cell[0]][next_cell[1]] = True
            stack.append(next_cell)
            current = next_cell
            moved = True
        elif c < C-1 and not eastWall[r][c] and not visited_solver[r][c+1]:
            next_cell = (r, c+1)
            visited_solver[next_cell[0]][next_cell[1]] = True
            stack.append(next_cell)
            current = next_cell
            moved = True
        elif r < R-1 and not northWall[r+1][c] and not visited_solver[r+1][c]:
            next_cell = (r+1, c)
            visited_solver[next_cell[0]][next_cell[1]] = True
            stack.append(next_cell)
            current = next_cell
            moved = True
        elif c > 0 and not eastWall[r][c-1] and not visited_solver[r][c-1]:
            next_cell = (r, c-1)
            visited_solver[next_cell[0]][next_cell[1]] = True
            stack.append(next_cell)
            current = next_cell
            moved = True
        if not moved:
            draw_circle_at(screen, current, BLUE)
            pygame.display.flip()
            pygame.time.delay(SOLVER_DELAY)
            stack.pop()
            if stack:
                current = stack[-1]

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Maze")
    clock = pygame.time.Clock()
    global start_pos, end_pos
    start_pos = (random.randrange(R), 0)
    end_pos = (random.randrange(R), C-1)
    generate_maze(screen, clock)
    solve_maze(screen, clock)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        clock.tick(60)

if __name__ == "__main__":
    main()