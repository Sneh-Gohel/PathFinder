# algorithms.py

import heapq
from collections import deque

class BFS:
    def __init__(self, grid):
        self.grid = grid
        self.visited = set()
        self.queue = deque()
        self.parent = {}
        self.found = False
        self.path = []
    
    def run_step(self):
        """Run one step of BFS algorithm"""
        if self.found or not self.queue:
            return True  # Algorithm finished
        
        # Get next cell from queue
        row, col = self.queue.popleft()
        cell = self.grid.cells[row][col]
        
        # Skip if already visited
        if (row, col) in self.visited:
            return False
        
        # Mark as visited
        self.visited.add((row, col))
        cell.visited = True
        cell.in_frontier = False
        
        # Check if we reached the goal
        if (row, col) == self.grid.goal_pos:
            self.found = True
            self.reconstruct_path()
            return True
        
        # Explore neighbors
        for neighbor in self.grid.get_neighbors(row, col):
            if neighbor not in self.visited and neighbor not in self.parent:
                self.queue.append(neighbor)
                self.parent[neighbor] = (row, col)
                n_row, n_col = neighbor
                self.grid.cells[n_row][n_col].in_frontier = True
        
        return False
    
    def reconstruct_path(self):
        """Reconstruct the path from goal to start"""
        if not self.found:
            return
        
        # Backtrack from goal to start
        current = self.grid.goal_pos
        while current != self.grid.start_pos:
            self.path.append(current)
            current = self.parent[current]
        
        # Mark path cells
        for row, col in self.path:
            self.grid.cells[row][col].in_path = True
    
    def start(self):
        """Initialize and start BFS algorithm"""
        if not self.grid.start_pos or not self.grid.goal_pos:
            return False
        
        self.visited.clear()
        self.queue.clear()
        self.parent.clear()
        self.found = False
        self.path.clear()
        
        # Start from the start position
        self.queue.append(self.grid.start_pos)
        self.parent[self.grid.start_pos] = None
        
        return True

class AStar:
    def __init__(self, grid):
        self.grid = grid
        self.open_set = []
        self.closed_set = set()
        self.g_score = {}
        self.f_score = {}
        self.parent = {}
        self.found = False
        self.path = []
    
    def heuristic(self, a, b):
        """Manhattan distance heuristic"""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    def run_step(self):
        """Run one step of A* algorithm"""
        if self.found or not self.open_set:
            return True  # Algorithm finished
        
        # Get cell with lowest f_score
        _, current = heapq.heappop(self.open_set)
        row, col = current
        cell = self.grid.cells[row][col]
        
        # Skip if already processed
        if current in self.closed_set:
            return False
        
        # Mark as visited
        self.closed_set.add(current)
        cell.visited = True
        cell.in_frontier = False
        
        # Check if we reached the goal
        if current == self.grid.goal_pos:
            self.found = True
            self.reconstruct_path()
            return True
        
        # Explore neighbors
        for neighbor in self.grid.get_neighbors(row, col):
            if neighbor in self.closed_set:
                continue
            
            # Calculate tentative g_score
            tentative_g = self.g_score[current] + 1
            
            if neighbor not in self.g_score or tentative_g < self.g_score[neighbor]:
                # This path to neighbor is better than any previous one
                self.parent[neighbor] = current
                self.g_score[neighbor] = tentative_g
                self.f_score[neighbor] = tentative_g + self.heuristic(neighbor, self.grid.goal_pos)
                
                # Add to open set if not already there
                if not any(neighbor == item[1] for item in self.open_set):
                    heapq.heappush(self.open_set, (self.f_score[neighbor], neighbor))
                    n_row, n_col = neighbor
                    self.grid.cells[n_row][n_col].in_frontier = True
        
        return False
    
    def reconstruct_path(self):
        """Reconstruct the path from goal to start"""
        if not self.found:
            return
        
        # Backtrack from goal to start
        current = self.grid.goal_pos
        while current != self.grid.start_pos:
            self.path.append(current)
            current = self.parent[current]
        
        # Mark path cells
        for row, col in self.path:
            self.grid.cells[row][col].in_path = True
    
    def start(self):
        """Initialize and start A* algorithm"""
        if not self.grid.start_pos or not self.grid.goal_pos:
            return False
        
        self.open_set.clear()
        self.closed_set.clear()
        self.g_score.clear()
        self.f_score.clear()
        self.parent.clear()
        self.found = False
        self.path.clear()
        
        # Initialize scores
        self.g_score[self.grid.start_pos] = 0
        self.f_score[self.grid.start_pos] = self.heuristic(self.grid.start_pos, self.grid.goal_pos)
        
        # Start from the start position
        heapq.heappush(self.open_set, (self.f_score[self.grid.start_pos], self.grid.start_pos))
        
        return True