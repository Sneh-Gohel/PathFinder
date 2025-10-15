# ui.py

import pygame
from constants import *

class Button:
    def __init__(self, x, y, width, height, text, color=LIGHT_GRAY, hover_color=GRAY, text_color=BLACK):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
        self.is_active = False
        self.font = pygame.font.SysFont('Arial', 16)
    
    def draw(self, screen):
        # Draw button with rounded corners
        color = self.hover_color if self.is_hovered else self.color
        
        # Draw shadow for 3D effect
        shadow_rect = self.rect.copy()
        shadow_rect.x += 2
        shadow_rect.y += 2
        pygame.draw.rect(screen, DARK_GRAY, shadow_rect, border_radius=5)
        
        # Draw button
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        
        # Draw border
        border_color = BLUE if self.is_active else BLACK
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=5)
        
        # Draw text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
    
    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

class UI:
    def __init__(self):
        self.buttons = []
        self.mode = "draw"  # Modes: draw, set_start, set_goal
        self.algorithm_running = False
        self.current_algorithm = None
        self.create_buttons()
    
    def create_buttons(self):
        x = BUTTON_MARGIN
        y = BUTTON_MARGIN
        
        buttons_data = [
            ("Set Start", "set_start"),
            ("Set Goal", "set_goal"),
            ("Draw Wall", "draw"),
            ("Clear Grid", "clear_grid"),
            ("Generate Maze", "generate_maze"),
            ("Run BFS", "run_bfs"),
            ("Run A*", "run_astar"),
            ("Reset", "reset")
        ]
        
        for text, action in buttons_data:
            self.buttons.append(Button(x, y, BUTTON_WIDTH, BUTTON_HEIGHT, text))
            x += BUTTON_WIDTH + BUTTON_MARGIN
    
    def draw(self, screen):
        # Draw UI background
        pygame.draw.rect(screen, LIGHT_GRAY, (0, 0, WINDOW_WIDTH, UI_HEIGHT))
        
        # Draw buttons
        for button in self.buttons:
            button.draw(screen)
        
        # Draw instructions
        font = pygame.font.SysFont('Arial', 14)
        instructions = [
            "Left-click: Draw/Erase Walls | Right-click: Erase Walls",
            "Select an algorithm and click Run to find the path"
        ]
        
        y_pos = UI_HEIGHT - 35
        for instruction in instructions:
            text_surface = font.render(instruction, True, DARK_GRAY)
            screen.blit(text_surface, (10, y_pos))
            y_pos += 15
    
    def handle_event(self, event, grid, algorithms):
        pos = pygame.mouse.get_pos()
        
        # Check button hovers
        for button in self.buttons:
            button.check_hover(pos)
        
        # Handle button clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            for i, button in enumerate(self.buttons):
                if button.is_clicked(pos, event):
                    self.handle_button_click(i, grid, algorithms)
                    return True
        
        return False
    
    def handle_button_click(self, button_index, grid, algorithms):
        # Reset active state for all buttons
        for button in self.buttons:
            button.is_active = False
        
        # Get the clicked button
        button = self.buttons[button_index]
        button.is_active = True
        
        # Handle different button actions
        if button_index == 0:  # Set Start
            self.mode = "set_start"
        elif button_index == 1:  # Set Goal
            self.mode = "set_goal"
        elif button_index == 2:  # Draw Wall
            self.mode = "draw"
        elif button_index == 3:  # Clear Grid
            grid.clear_grid()
            self.algorithm_running = False
            self.current_algorithm = None
        elif button_index == 4:  # Generate Maze
            grid.generate_maze_prim()
            self.algorithm_running = False
            self.current_algorithm = None
        elif button_index == 5:  # Run BFS
            if grid.start_pos and grid.goal_pos:
                self.current_algorithm = algorithms["BFS"]
                self.current_algorithm.start()
                self.algorithm_running = True
        elif button_index == 6:  # Run A*
            if grid.start_pos and grid.goal_pos:
                self.current_algorithm = algorithms["A*"]
                self.current_algorithm.start()
                self.algorithm_running = True
        elif button_index == 7:  # Reset
            grid.reset_algorithm()
            self.algorithm_running = False
            self.current_algorithm = None
    
    def handle_grid_click(self, event, grid):
        if self.algorithm_running:
            return
        
        cell = grid.get_cell(event.pos)
        if not cell:
            return
        
        if event.button == 1:  # Left click
            if self.mode == "draw":
                grid.toggle_wall(cell)
            elif self.mode == "set_start":
                grid.set_start(cell)
            elif self.mode == "set_goal":
                grid.set_goal(cell)
        elif event.button == 3:  # Right click
            grid.toggle_wall(cell)