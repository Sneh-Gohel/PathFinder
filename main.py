# main.py

import pygame
import sys
import time
from grid import Grid
from algorithms import BFS, AStar
from ui import UI
from constants import *

def main():
    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Pathfinding AI with Custom Maze Builder")
    
    # Create game objects
    grid = Grid()
    ui = UI()
    
    # Initialize algorithms
    algorithms = {
        "BFS": BFS(grid),
        "A*": AStar(grid)
    }
    
    # Main game loop
    clock = pygame.time.Clock()
    running = True
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Handle UI events
            ui_handled = ui.handle_event(event, grid, algorithms)
            
            # Handle grid interactions if UI didn't handle the event
            if not ui_handled and event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION):
                # Handle mouse clicks on grid
                if event.type == pygame.MOUSEBUTTONDOWN:
                    ui.handle_grid_click(event, grid)
                
                # Handle mouse drag for drawing walls
                elif event.type == pygame.MOUSEMOTION and pygame.mouse.get_pressed()[0]:
                    if ui.mode == "draw":
                        cell = grid.get_cell(event.pos)
                        if cell and not cell.start and not cell.goal:
                            cell.wall = True
        
        # Run algorithm step if an algorithm is running
        if ui.algorithm_running and ui.current_algorithm:
            finished = ui.current_algorithm.run_step()
            if finished:
                # Algorithm finished - show result and generate PDF
                ui.algorithm_running = False
                ui.current_algorithm.end_time = time.time()
                
                if ui.current_algorithm.found:
                    ui.message.show(f"Path found! Length: {ui.current_algorithm.path_length}", GREEN)
                    # Generate PDF report
                    pdf_filename = ui.current_algorithm.generate_pdf_report(type(ui.current_algorithm).__name__)
                    ui.message.show(f"PDF report generated: {pdf_filename}", LIGHT_BLUE, 5000)
                else:
                    ui.message.show("No path found!", RED)
                    # Generate PDF report even if no path found
                    pdf_filename = ui.current_algorithm.generate_pdf_report(type(ui.current_algorithm).__name__)
                    ui.message.show(f"PDF report generated: {pdf_filename}", LIGHT_BLUE, 5000)
                
                ui.clear_algorithm_buttons()
        
        # Draw everything
        screen.fill(WHITE)
        grid.draw(screen)
        ui.draw(screen)
        
        # Update display
        pygame.display.flip()
        clock.tick(60)  # Limit to 60 FPS
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()