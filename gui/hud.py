import pygame
from OpenGL.GL import *
from OpenGL.GLU import gluProject
import numpy as np

class HUD:
    #Heads-up display for showing simulation information.
    
    def __init__(self, settings):
        self.settings = settings
        pygame.font.init() 
        self.font = pygame.font.SysFont('Arial', 14)
        self.title_font = pygame.font.SysFont('Arial', 16, bold=True)
        self.molecule_font = pygame.font.SysFont('Arial', 13, bold=True) # Smaller for 3D labels
        
        self.surface = None
        
        self.text_color = (220, 220, 220)
        self.highlight_color = (100, 180, 255)
        self.background_color = (20, 20, 30, 190)
        self.molecule_colors = { 
            "H2": (180, 180, 255), "O2": (255, 180, 180), "N2": (180, 180, 255),
            "H2O": (150, 220, 255), "CH4": (180, 255, 180), "NH3": (180, 220, 255),
            "CO2": (220, 220, 220), "LiH": (220, 150, 250) 
        }
    
    def render(self, physics_engine, selected_atom=None):
        current_window_width, current_window_height = pygame.display.get_surface().get_size()
        if self.surface is None or self.surface.get_size() != (current_window_width, current_window_height):
            self.surface = pygame.Surface((current_window_width, current_window_height), pygame.SRCALPHA)
        
        self.surface.fill((0, 0, 0, 0)) 
        
        self.render_simulation_stats(physics_engine)
        if selected_atom is not None:
            self.render_atom_info(selected_atom)
        self.render_molecule_info(physics_engine)
        self.render_help_text()
        self.blit_to_screen()
    
    def render_simulation_stats(self, physics_engine):
        #Render simulation statistics.
        #background for stats box
        stats_rect = pygame.Rect(10, 10, 200, 100)
        pygame.draw.rect(self.surface, self.background_color, stats_rect)
        pygame.draw.rect(self.surface, self.text_color, stats_rect, 1)
        
        title = self.title_font.render("Simulation Stats", True, self.highlight_color)
        self.surface.blit(title, (20, 15))
        
        y = 40
        stats = [
            f"Atoms: {len(physics_engine.atoms)}",
            f"Time: {physics_engine.time:.2f} s",
            f"Status: {'Paused' if physics_engine.paused else 'Running'}",
            f"Speed: {physics_engine.time_scale:.1f}x",
            f"Molecules: {len(physics_engine.identify_molecules())}"
        ]
        
        for stat in stats:
            text = self.font.render(stat, True, self.text_color)
            self.surface.blit(text, (20, y))
            y += 20
    
    def render_atom_info(self, atom):
        #render information about the selected atom.
        #background for atom info box
        info_rect = pygame.Rect(10, 120, 250, 180)
        pygame.draw.rect(self.surface, self.background_color, info_rect)
        pygame.draw.rect(self.surface, self.text_color, info_rect, 1)
        
        title_text = f"Selected: {atom.element_name} ({atom.element_symbol})"
        title = self.title_font.render(title_text, True, self.highlight_color)
        self.surface.blit(title, (20, 125))
        
        #atom info
        y = 150
        info = [
            f"Atomic Number: {atom.atomic_number}",
            f"Protons: {len(atom.protons)}",
            f"Neutrons: {len(atom.neutrons)}",
            f"Electrons: {len(atom.electrons)}",
            f"Position: ({atom.position[0]:.2f}, {atom.position[1]:.2f}, {atom.position[2]:.2f})",
            f"Velocity: ({atom.velocity[0]:.2f}, {atom.velocity[1]:.2f}, {atom.velocity[2]:.2f})",
            f"Bonds: {len(atom.bonds)}"
        ]
        
        for line in info:
            text = self.font.render(line, True, self.text_color)
            self.surface.blit(text, (20, y))
            y += 20
    
    def render_molecule_info(self, physics_engine):
        #Render information about molecules in the simulation.
        #identify molecules
        molecules = physics_engine.identify_common_molecules()
        if not molecules:
            return
        
        #background for molecule info box
        info_rect = pygame.Rect(self.settings.WINDOW_WIDTH - 260, 10, 250, 30 + len(molecules) * 20)
        pygame.draw.rect(self.surface, self.background_color, info_rect)
        pygame.draw.rect(self.surface, self.text_color, info_rect, 1)
        
        title = self.title_font.render("Molecules Detected", True, self.highlight_color)
        self.surface.blit(title, (self.settings.WINDOW_WIDTH - 250, 15))
        
        #list molecules
        y = 40
        for molecule in molecules:
            formula = molecule["formula"]
            name = molecule["name"]
            
            #choose color for molecule
            if formula in self.molecule_colors:
                color = self.molecule_colors[formula]
            else:
                color = self.text_color
            
            text = self.font.render(name, True, color)
            self.surface.blit(text, (self.settings.WINDOW_WIDTH - 250, y))
            y += 20
            
            #also render formula near the molecule in 3D space
            if hasattr(self.settings, 'SHOW_MOLECULE_LABELS') and self.settings.SHOW_MOLECULE_LABELS:
                self.render_molecule_label(molecule)