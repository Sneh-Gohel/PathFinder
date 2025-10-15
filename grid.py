# grid.py

import pygame
import random
from constants import *

class Cell:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.x = col * CELL_SIZE
        self.y = row * CELL_SIZE + UI_HEIGHT
        self.color = WHITE
        self.wall = False
        self.start = False
        self.goal = False
        self.visited = False
        self.in_frontier = False
        self.in_path = False
    
    def draw(self, screen):
        # Draw cell background
        pygame.draw.rect(screen, self.color, (self.x, self.y, CELL_SIZE, CELL_SIZE))
        
        # Draw cell border
        pygame.draw.rect(screen, GRAY, (self.x, self.y, CELL_SIZE, CELL_SIZE), 1)
        
        # Draw wall if present
        if self.wall:
            pygame.draw.rect(screen, BLACK, (self.x, self.y, CELL_SIZE, CELL_SIZE))
        
        # Draw special markers
        if self.start:
            pygame.draw.rect(screen, RED, (self.x, self.y, CELL_SIZE, CELL_SIZE))
        elif self.goal:
            pygame.draw.rect(screen, YELLOW, (self.x, self.y, CELL_SIZE, CELL_SIZE))
        elif self.in_path:
            pygame.draw.rect(screen, GREEN, (self.x, self.y, CELL_SIZE, CELL_SIZE))
        elif self.in_frontier:
            pygame.draw.rect(screen, ORANGE, (self.x, self.y, CELL_SIZE, CELL_SIZE))
        elif self.visited:
            pygame.draw.rect(screen, LIGHT_BLUE, (self.x, self.y, CELL_SIZE, CELL_SIZE))
    
    def reset_state(self):
        """Reset algorithm-related states but keep walls, start, and goal"""
        self.visited = False
        self.in_frontier = False
        self.in_path = False
        if not self.wall and not self.start and not self.goal:
            self.color = WHITE
    
    def reset_all(self):
        """Reset all states including walls, start, and goal"""
        self.wall = False
        self.start = False
        self.goal = False
        self.visited = False
        self.in_frontier = False
        self.in_path = False
        self.color = WHITE

class Grid:
    def __init__(self):
        self.rows = GRID_HEIGHT
        self.cols = GRID_WIDTH
        self.cells = [[Cell(row, col) for col in range(self.cols)] for row in range(self.rows)]
        self.start_pos = None
        self.goal_pos = None
    
    def draw(self, screen):
        for row in self.cells:
            for cell in row:
                cell.draw(screen)
    
    def get_cell(self, pos):
        """Get cell at mouse position"""
        x, y = pos
        if y < UI_HEIGHT:
            return None
        
        row = (y - UI_HEIGHT) // CELL_SIZE
        col = x // CELL_SIZE
        
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.cells[row][col]
        return None
    
    def toggle_wall(self, cell):
        """Toggle wall state for a cell"""
        if cell and not cell.start and not cell.goal:
            cell.wall = not cell.wall
            return True
        return False
    
    def set_start(self, cell):
        """Set a cell as start position"""
        if cell and not cell.wall and not cell.goal:
            # Remove previous start
            if self.start_pos:
                old_row, old_col = self.start_pos
                self.cells[old_row][old_col].start = False
            
            # Set new start
            cell.start = True
            self.start_pos = (cell.row, cell.col)
            return True
        return False
    
    def set_goal(self, cell):
        """Set a cell as goal position"""
        if cell and not cell.wall and not cell.start:
            # Remove previous goal
            if self.goal_pos:
                old_row, old_col = self.goal_pos
                self.cells[old_row][old_col].goal = False
            
            # Set new goal
            cell.goal = True
            self.goal_pos = (cell.row, cell.col)
            return True
        return False
    
    def clear_grid(self):
        """Clear all cells (walls, start, goal)"""
        for row in self.cells:
            for cell in row:
                cell.reset_all()
        self.start_pos = None
        self.goal_pos = None
    
    def reset_algorithm(self):
        """Reset algorithm visualization but keep walls, start, and goal"""
        for row in self.cells:
            for cell in row:
                cell.reset_state()
    
    def get_neighbors(self, row, col, diagonals=False):
        """Get valid neighboring cells (up, down, left, right)"""
        neighbors = []
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Right, Down, Left, Up
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < self.rows and 0 <= new_col < self.cols:
                neighbor = self.cells[new_row][new_col]
                if not neighbor.wall:
                    neighbors.append((new_row, new_col))
        
        return neighbors
    
    def generate_maze_prim(self):
        """Generate a random maze using Prim's algorithm"""
        # Reset grid first
        self.clear_grid()
        
        # Initialize all cells as walls
        for row in self.cells:
            for cell in row:
                cell.wall = True
        
        # Start from a random cell
        start_row = random.randint(0, self.rows - 1)
        start_col = random.randint(0, self.cols - 1)
        self.cells[start_row][start_col].wall = False
        
        # Add frontier cells
        frontiers = []
        for dr, dc in [(0, 2), (2, 0), (0, -2), (-2, 0)]:
            new_row, new_col = start_row + dr, start_col + dc
            if 0 <= new_row < self.rows and 0 <= new_col < self.cols:
                frontiers.append((new_row, new_col))
                self.cells[new_row][new_col].color = ORANGE  # Mark as frontier
        
        while frontiers:
            # Pick a random frontier cell
            row, col = random.choice(frontiers)
            frontiers.remove((row, col))
            
            # Find all neighbors that are passages
            neighbors = []
            for dr, dc in [(0, 2), (2, 0), (0, -2), (-2, 0)]:
                new_row, new_col = row + dr, col + dc
                if 0 <= new_row < self.rows and 0 <= new_col < self.cols and not self.cells[new_row][new_col].wall:
                    neighbors.append((new_row, new_col))
            
            if neighbors:
                # Connect the frontier cell to a random neighbor
                n_row, n_col = random.choice(neighbors)
                
                # Remove the wall between them
                wall_row = (row + n_row) // 2
                wall_col = (col + n_col) // 2
                self.cells[wall_row][wall_col].wall = False
                self.cells[row][col].wall = False
                
                # Add new frontiers
                for dr, dc in [(0, 2), (2, 0), (0, -2), (-2, 0)]:
                    new_row, new_col = row + dr, col + dc
                    if 0 <= new_row < self.rows and 0 <= new_col < self.cols and self.cells[new_row][new_col].wall:
                        frontiers.append((new_row, new_col))
                        self.cells[new_row][new_col].color = ORANGE
        
        # Set start and goal at opposite corners
        self.set_start(self.cells[0][0])
        self.set_goal(self.cells[self.rows-1][self.cols-1])