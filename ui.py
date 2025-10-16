# ui.py

import pygame
import time
from constants import *

class Button:
    def __init__(self, x, y, width, height, text, color=BUTTON_COLOR, hover_color=BUTTON_HOVER, 
                 active_color=BUTTON_ACTIVE, text_color=WHITE, icon=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.active_color = active_color
        self.text_color = text_color
        self.is_hovered = False
        self.is_active = False
        self.font = pygame.font.SysFont('Arial', 14, bold=True)
        self.icon = icon
    
    def draw(self, screen):
        # Determine button color based on state
        if self.is_active:
            color = self.active_color
        elif self.is_hovered:
            color = self.hover_color
        else:
            color = self.color
        
        # Draw button with subtle gradient effect
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        
        # Add highlight at top
        highlight_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, 3)
        pygame.draw.rect(screen, (255, 255, 255, 50), highlight_rect, border_radius=8)
        
        # Draw text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
        # Draw active indicator
        if self.is_active:
            indicator_rect = pygame.Rect(self.rect.x + 5, self.rect.y + 5, 4, self.rect.height - 10)
            pygame.draw.rect(screen, LIGHT_BLUE, indicator_rect, border_radius=2)
    
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
    
    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

class Section:
    def __init__(self, x, y, width, title):
        self.rect = pygame.Rect(x, y, width, 0)
        self.title = title
        self.buttons = []
        self.height = 0
    
    def add_button(self, button):
        self.buttons.append(button)
        self.height = len(self.buttons) * (BUTTON_HEIGHT + BUTTON_MARGIN) + 40
    
    def draw(self, screen):
        # Draw section background
        section_bg = pygame.Rect(self.rect.x - 10, self.rect.y - 10, self.rect.width + 20, self.height)
        pygame.draw.rect(screen, (60, 60, 70), section_bg, border_radius=10)
        
        # Draw section title
        font = pygame.font.SysFont('Arial', 16, bold=True)
        title_surface = font.render(self.title, True, LIGHT_BLUE)
        screen.blit(title_surface, (self.rect.x, self.rect.y - 5))
        
        # Draw buttons
        for button in self.buttons:
            button.draw(screen)

class Message:
    def __init__(self):
        self.text = ""
        self.color = WHITE
        self.start_time = 0
        self.duration = 0
        self.visible = False
    
    def show(self, text, color=WHITE, duration=3000):
        self.text = text
        self.color = color
        self.start_time = time.time()
        self.duration = duration
        self.visible = True
    
    def update(self):
        if self.visible and time.time() - self.start_time > self.duration:
            self.visible = False
    
    def draw(self, screen):
        if self.visible:
            font = pygame.font.SysFont('Arial', 14, bold=True)
            text_surface = font.render(self.text, True, self.color)
            
            # Draw background for message
            text_rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, UI_HEIGHT // 2))
            bg_rect = text_rect.inflate(20, 10)
            pygame.draw.rect(screen, (40, 40, 40), bg_rect, border_radius=5)
            pygame.draw.rect(screen, self.color, bg_rect, 2, border_radius=5)
            
            screen.blit(text_surface, text_rect)

class UI:
    def __init__(self):
        self.sections = []
        self.mode = "draw"
        self.algorithm_running = False
        self.current_algorithm = None
        self.message = Message()
        self.create_ui()
    
    def create_ui(self):
        sidebar_x = WINDOW_WIDTH - SIDEBAR_WIDTH
        
        # Section 1: Setup Tools
        setup_section = Section(sidebar_x + 20, 60, BUTTON_WIDTH, "SETUP TOOLS")
        
        setup_buttons = [
            Button(sidebar_x + 20, 90, BUTTON_WIDTH, BUTTON_HEIGHT, "Set Start Position", LIGHT_GREEN, (100, 200, 100), (120, 220, 120)),
            Button(sidebar_x + 20, 90 + BUTTON_HEIGHT + BUTTON_MARGIN, BUTTON_WIDTH, BUTTON_HEIGHT, "Set Goal Position", LIGHT_RED, (200, 100, 100), (220, 120, 120)),
            Button(sidebar_x + 20, 90 + 2*(BUTTON_HEIGHT + BUTTON_MARGIN), BUTTON_WIDTH, BUTTON_HEIGHT, "Draw Walls", BUTTON_COLOR, BUTTON_HOVER, BUTTON_ACTIVE)
        ]
        
        for button in setup_buttons:
            setup_section.add_button(button)
        
        self.sections.append(setup_section)
        
        # Section 2: Maze Generation
        maze_section = Section(sidebar_x + 20, 90 + 3*(BUTTON_HEIGHT + BUTTON_MARGIN) + 20, BUTTON_WIDTH, "MAZE GENERATION")
        
        maze_buttons = [
            Button(sidebar_x + 20, 90 + 3*(BUTTON_HEIGHT + BUTTON_MARGIN) + 50, BUTTON_WIDTH, BUTTON_HEIGHT, "Generate Random Maze", (100, 150, 255), (120, 170, 255), (140, 190, 255)),
            Button(sidebar_x + 20, 90 + 3*(BUTTON_HEIGHT + BUTTON_MARGIN) + 50 + BUTTON_HEIGHT + BUTTON_MARGIN, BUTTON_WIDTH, BUTTON_HEIGHT, "Clear Entire Grid", (255, 180, 100), (255, 200, 120), (255, 220, 140))
        ]
        
        for button in maze_buttons:
            maze_section.add_button(button)
        
        self.sections.append(maze_section)
        
        # Section 3: Algorithms
        algo_section = Section(sidebar_x + 20, 90 + 3*(BUTTON_HEIGHT + BUTTON_MARGIN) + 50 + 2*(BUTTON_HEIGHT + BUTTON_MARGIN) + 40, BUTTON_WIDTH, "PATHFINDING ALGORITHMS")
        
        algo_buttons = [
            Button(sidebar_x + 20, 90 + 3*(BUTTON_HEIGHT + BUTTON_MARGIN) + 50 + 2*(BUTTON_HEIGHT + BUTTON_MARGIN) + 70, BUTTON_WIDTH, BUTTON_HEIGHT, "Run Breadth-First Search (BFS)", (150, 200, 255), (170, 220, 255), (190, 240, 255)),
            Button(sidebar_x + 20, 90 + 3*(BUTTON_HEIGHT + BUTTON_MARGIN) + 50 + 2*(BUTTON_HEIGHT + BUTTON_MARGIN) + 70 + BUTTON_HEIGHT + BUTTON_MARGIN, BUTTON_WIDTH, BUTTON_HEIGHT, "Run A* Algorithm", (200, 150, 255), (220, 170, 255), (240, 190, 255)),
            Button(sidebar_x + 20, 90 + 3*(BUTTON_HEIGHT + BUTTON_MARGIN) + 50 + 2*(BUTTON_HEIGHT + BUTTON_MARGIN) + 70 + 2*(BUTTON_HEIGHT + BUTTON_MARGIN), BUTTON_WIDTH, BUTTON_HEIGHT, "Reset Visualization", (150, 150, 150), (170, 170, 170), (190, 190, 190))
        ]
        
        for button in algo_buttons:
            algo_section.add_button(button)
        
        self.sections.append(algo_section)
        
        # Set initial active state for Draw Walls button
        setup_buttons[2].is_active = True
    
    def draw(self, screen):
        # Draw sidebar background with gradient
        sidebar_rect = pygame.Rect(WINDOW_WIDTH - SIDEBAR_WIDTH, 0, SIDEBAR_WIDTH, WINDOW_HEIGHT)
        pygame.draw.rect(screen, SIDEBAR_COLOR, sidebar_rect)
        
        # Add subtle pattern to sidebar
        for i in range(0, SIDEBAR_WIDTH, 4):
            pygame.draw.line(screen, (60, 60, 70), 
                           (WINDOW_WIDTH - SIDEBAR_WIDTH + i, 0),
                           (WINDOW_WIDTH - SIDEBAR_WIDTH + i, WINDOW_HEIGHT), 1)
        
        # Draw top bar
        top_bar = pygame.Rect(0, 0, WINDOW_WIDTH - SIDEBAR_WIDTH, UI_HEIGHT)
        pygame.draw.rect(screen, (40, 40, 50), top_bar)
        
        # Draw app title
        title_font = pygame.font.SysFont('Arial', 24, bold=True)
        title_surface = title_font.render("Pathfinding AI Visualizer", True, LIGHT_BLUE)
        screen.blit(title_surface, (20, 10))
        
        # Draw current status
        status_font = pygame.font.SysFont('Arial', 14)
        
        mode_text = f"Mode: {self.mode.replace('_', ' ').title()}"
        mode_surface = status_font.render(mode_text, True, WHITE)
        screen.blit(mode_surface, (WINDOW_WIDTH - SIDEBAR_WIDTH - 200, 15))
        
        if self.algorithm_running:
            status_text = f"Running: {type(self.current_algorithm).__name__}"
            status_surface = status_font.render(status_text, True, GREEN)
            screen.blit(status_surface, (WINDOW_WIDTH - SIDEBAR_WIDTH - 200, 35))
        
        # Draw instructions in top bar
        instruction_font = pygame.font.SysFont('Arial', 12)
        instructions = [
            "Left-click: Draw Walls | Right-click: Erase Walls",
            "Set Start & Goal positions, then run an algorithm"
        ]
        
        for i, instruction in enumerate(instructions):
            instr_surface = instruction_font.render(instruction, True, LIGHT_GRAY)
            screen.blit(instr_surface, (250, 10 + i * 15))
        
        # Draw sections
        for section in self.sections:
            section.draw(screen)
        
        # Draw legend in sidebar bottom
        self.draw_legend(screen)
        
        # Draw message
        self.message.draw(screen)
    
    def draw_legend(self, screen):
        legend_y = WINDOW_HEIGHT - 180
        legend_x = WINDOW_WIDTH - SIDEBAR_WIDTH + 20
        
        legend_font = pygame.font.SysFont('Arial', 14, bold=True)
        item_font = pygame.font.SysFont('Arial', 12)
        
        # Legend title
        title_surface = legend_font.render("LEGEND", True, LIGHT_BLUE)
        screen.blit(title_surface, (legend_x, legend_y))
        
        legend_items = [
            (RED, "Start Position"),
            (YELLOW, "Goal Position"),
            (BLACK, "Wall/Obstacle"),
            (LIGHT_BLUE, "Visited Nodes"),
            (ORANGE, "Frontier Nodes"),
            (GREEN, "Shortest Path")
        ]
        
        for i, (color, text) in enumerate(legend_items):
            # Color box
            pygame.draw.rect(screen, color, (legend_x, legend_y + 30 + i * 25, 15, 15))
            pygame.draw.rect(screen, WHITE, (legend_x, legend_y + 30 + i * 25, 15, 15), 1)
            
            # Text
            text_surface = item_font.render(text, True, WHITE)
            screen.blit(text_surface, (legend_x + 25, legend_y + 30 + i * 25))
    
    def handle_event(self, event, grid, algorithms):
        pos = pygame.mouse.get_pos()
        
        # Update message
        self.message.update()
        
        # Check if click is in sidebar
        if pos[0] > WINDOW_WIDTH - SIDEBAR_WIDTH:
            # Check button hovers in all sections
            for section in self.sections:
                for button in section.buttons:
                    button.check_hover(pos)
            
            # Handle button clicks
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for section in self.sections:
                    for i, button in enumerate(section.buttons):
                        if button.is_clicked(pos, event):
                            self.handle_button_click(button.text, grid, algorithms)
                            return True
            return True  # Event was in sidebar
        return False  # Event was in grid area
    
    def handle_button_click(self, button_text, grid, algorithms):
        # Handle Setup Tools
        if button_text == "Set Start Position":
            self.mode = "set_start"
            self.update_mode_buttons(button_text)
        elif button_text == "Set Goal Position":
            self.mode = "set_goal"
            self.update_mode_buttons(button_text)
        elif button_text == "Draw Walls":
            self.mode = "draw"
            self.update_mode_buttons(button_text)
        
        # Handle Maze Generation
        elif button_text == "Generate Random Maze":
            grid.generate_maze_prim()
            self.algorithm_running = False
            self.current_algorithm = None
            self.message.show("Random maze generated!", GREEN)
        elif button_text == "Clear Entire Grid":
            grid.clear_grid()
            self.algorithm_running = False
            self.current_algorithm = None
            self.message.show("Grid cleared!", ORANGE)
        
        # Handle Algorithms
        elif button_text == "Run Breadth-First Search (BFS)":
            if not grid.start_pos:
                self.message.show("Error: Please set a start position first!", RED)
            elif not grid.goal_pos:
                self.message.show("Error: Please set a goal position first!", RED)
            else:
                self.current_algorithm = algorithms["BFS"]
                if self.current_algorithm.start():
                    self.algorithm_running = True
                    self.update_algorithm_buttons(button_text)
                    self.message.show("BFS algorithm started...", BLUE)
        elif button_text == "Run A* Algorithm":
            if not grid.start_pos:
                self.message.show("Error: Please set a start position first!", RED)
            elif not grid.goal_pos:
                self.message.show("Error: Please set a goal position first!", RED)
            else:
                self.current_algorithm = algorithms["A*"]
                if self.current_algorithm.start():
                    self.algorithm_running = True
                    self.update_algorithm_buttons(button_text)
                    self.message.show("A* algorithm started...", BLUE)
        elif button_text == "Reset Visualization":
            grid.reset_algorithm()
            self.algorithm_running = False
            self.current_algorithm = None
            self.clear_algorithm_buttons()
            self.message.show("Visualization reset!", LIGHT_BLUE)
    
    def update_mode_buttons(self, active_button_text):
        """Update active state for mode buttons"""
        for section in self.sections:
            for button in section.buttons:
                if button.text in ["Set Start Position", "Set Goal Position", "Draw Walls"]:
                    button.is_active = (button.text == active_button_text)
    
    def update_algorithm_buttons(self, active_button_text):
        """Update active state for algorithm buttons"""
        for section in self.sections:
            for button in section.buttons:
                if button.text in ["Run Breadth-First Search (BFS)", "Run A* Algorithm"]:
                    button.is_active = (button.text == active_button_text)
    
    def clear_algorithm_buttons(self):
        """Clear active state from algorithm buttons"""
        for section in self.sections:
            for button in section.buttons:
                if button.text in ["Run Breadth-First Search (BFS)", "Run A* Algorithm"]:
                    button.is_active = False
    
    def handle_grid_click(self, event, grid):
        if self.algorithm_running:
            self.message.show("Please reset visualization first!", RED)
            return
        
        cell = grid.get_cell(event.pos)
        if not cell:
            return
        
        if event.button == 1:  # Left click
            if self.mode == "draw":
                grid.toggle_wall(cell)
            elif self.mode == "set_start":
                if grid.set_start(cell):
                    # Switch back to draw mode after setting start
                    self.mode = "draw"
                    self.update_mode_buttons("Draw Walls")
                    self.message.show("Start position set!", GREEN)
                else:
                    self.message.show("Cannot set start on wall or goal!", RED)
            elif self.mode == "set_goal":
                if grid.set_goal(cell):
                    # Switch back to draw mode after setting goal
                    self.mode = "draw"
                    self.update_mode_buttons("Draw Walls")
                    self.message.show("Goal position set!", YELLOW)
                else:
                    self.message.show("Cannot set goal on wall or start!", RED)
        elif event.button == 3:  # Right click
            grid.toggle_wall(cell)