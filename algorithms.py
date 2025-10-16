# algorithms.py

import heapq
from collections import deque
import time
from fpdf import FPDF
import os

class AlgorithmBase:
    def __init__(self, grid):
        self.grid = grid
        self.steps = []
        self.start_time = None
        self.end_time = None
        self.nodes_explored = 0
        self.path_length = 0
        self.found = False
    
    def add_step(self, description, node=None):
        """Record a step for PDF report"""
        step_info = {
            'description': description,
            'node': node,
            'timestamp': time.time() - self.start_time if self.start_time else 0,
            'nodes_explored': self.nodes_explored
        }
        self.steps.append(step_info)
    
    def generate_pdf_report(self, algorithm_name):
        """Generate PDF report with algorithm steps and results"""
        if not os.path.exists('reports'):
            os.makedirs('reports')
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"reports/{algorithm_name}_report_{timestamp}.pdf"
        
        pdf = FPDF()
        pdf.add_page()
        
        # Title
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, f'{algorithm_name} Pathfinding Report', 0, 1, 'C')
        pdf.ln(10)
        
        # Results summary
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Results Summary:', 0, 1)
        pdf.set_font('Arial', '', 12)
        
        result_text = "Path Found: Yes" if self.found else "Path Found: No"
        pdf.cell(0, 10, result_text, 0, 1)
        pdf.cell(0, 10, f"Total Time: {self.end_time - self.start_time:.4f} seconds", 0, 1)
        pdf.cell(0, 10, f"Nodes Explored: {self.nodes_explored}", 0, 1)
        pdf.cell(0, 10, f"Path Length: {self.path_length}", 0, 1)
        pdf.ln(10)
        
        # Algorithm steps
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Algorithm Steps:', 0, 1)
        pdf.set_font('Arial', '', 10)
        
        for i, step in enumerate(self.steps[:50]):  # Limit to first 50 steps
            node_str = f" at {step['node']}" if step['node'] else ""
            pdf.cell(0, 8, f"Step {i+1}: {step['description']}{node_str} (Time: {step['timestamp']:.2f}s, Nodes: {step['nodes_explored']})", 0, 1)
        
        if len(self.steps) > 50:
            pdf.cell(0, 8, f"... and {len(self.steps) - 50} more steps", 0, 1)
        
        pdf.ln(10)
        
        # Grid information
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Grid Information:', 0, 1)
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f"Grid Size: {self.grid.rows} x {self.grid.cols}", 0, 1)
        pdf.cell(0, 10, f"Start Position: {self.grid.start_pos}", 0, 1)
        pdf.cell(0, 10, f"Goal Position: {self.grid.goal_pos}", 0, 1)
        
        pdf.output(filename)
        return filename

class BFS(AlgorithmBase):
    def __init__(self, grid):
        super().__init__(grid)
        self.visited = set()
        self.queue = deque()
        self.parent = {}
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
        self.nodes_explored += 1
        
        self.add_step("Visited node", (row, col))
        
        # Check if we reached the goal
        if (row, col) == self.grid.goal_pos:
            self.found = True
            self.add_step("Goal reached!", (row, col))
            self.reconstruct_path()
            return True
        
        # Explore neighbors
        neighbors = self.grid.get_neighbors(row, col)
        self.add_step(f"Exploring {len(neighbors)} neighbors", (row, col))
        
        for neighbor in neighbors:
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
        path_steps = []
        while current != self.grid.start_pos:
            self.path.append(current)
            path_steps.append(current)
            current = self.parent[current]
        
        self.path_length = len(self.path)
        self.add_step(f"Path reconstructed with {self.path_length} steps")
        
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
        self.steps.clear()
        self.nodes_explored = 0
        self.path_length = 0
        
        self.start_time = time.time()
        self.add_step("BFS algorithm started")
        self.add_step(f"Start position: {self.grid.start_pos}")
        self.add_step(f"Goal position: {self.grid.goal_pos}")
        
        # Start from the start position
        self.queue.append(self.grid.start_pos)
        self.parent[self.grid.start_pos] = None
        
        return True

class AStar(AlgorithmBase):
    def __init__(self, grid):
        super().__init__(grid)
        self.open_set = []
        self.closed_set = set()
        self.g_score = {}
        self.f_score = {}
        self.parent = {}
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
        self.nodes_explored += 1
        
        self.add_step("Visited node", (row, col))
        
        # Check if we reached the goal
        if current == self.grid.goal_pos:
            self.found = True
            self.add_step("Goal reached!", (row, col))
            self.reconstruct_path()
            return True
        
        # Explore neighbors
        neighbors = self.grid.get_neighbors(row, col)
        self.add_step(f"Exploring {len(neighbors)} neighbors", (row, col))
        
        for neighbor in neighbors:
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
                    self.add_step("Added to frontier", neighbor)
        
        return False
    
    def reconstruct_path(self):
        """Reconstruct the path from goal to start"""
        if not self.found:
            return
        
        # Backtrack from goal to start
        current = self.grid.goal_pos
        path_steps = []
        while current != self.grid.start_pos:
            self.path.append(current)
            path_steps.append(current)
            current = self.parent[current]
        
        self.path_length = len(self.path)
        self.add_step(f"Path reconstructed with {self.path_length} steps")
        
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
        self.steps.clear()
        self.nodes_explored = 0
        self.path_length = 0
        
        self.start_time = time.time()
        self.add_step("A* algorithm started")
        self.add_step(f"Start position: {self.grid.start_pos}")
        self.add_step(f"Goal position: {self.grid.goal_pos}")
        
        # Initialize scores
        self.g_score[self.grid.start_pos] = 0
        self.f_score[self.grid.start_pos] = self.heuristic(self.grid.start_pos, self.grid.goal_pos)
        self.add_step(f"Initial heuristic score: {self.f_score[self.grid.start_pos]}")
        
        # Start from the start position
        heapq.heappush(self.open_set, (self.f_score[self.grid.start_pos], self.grid.start_pos))
        
        return True