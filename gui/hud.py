import pygame
from OpenGL.GL import *
from OpenGL.GLU import gluProject
import numpy as np

class HUD:
    """Heads-up display for showing simulation information."""
    
    def __init__(self, settings):
        self.settings = settings
        pygame.font.init() 
        self.font = pygame.font.SysFont('Arial', 14)
        self.title_font = pygame.font.SysFont('Arial', 16, bold=True)
        self.molecule_font = pygame.font.SysFont('Arial', 13, bold=True) # Smaller for 3D labels
        
        self.surface = None # Will be created in render
        
        self.text_color = (220, 220, 220)
        self.highlight_color = (100, 180, 255)
        self.background_color = (20, 20, 30, 190) # Slightly more opaque
        self.molecule_colors = { 
            "H2": (180, 180, 255), "O2": (255, 180, 180), "N2": (180, 180, 255),
            "H2O": (150, 220, 255), "CH4": (180, 255, 180), "NH3": (180, 220, 255),
            "CO2": (220, 220, 220), "LiH": (220, 150, 250) 
        }
    
    def render(self, physics_engine, selected_atom=None):
        current_window_width, current_window_height = pygame.display.get_surface().get_size()
        if self.surface is None or self.surface.get_size() != (current_window_width, current_window_height):
            self.surface = pygame.Surface((current_window_width, current_window_height), pygame.SRCALPHA)
        
        self.surface.fill((0, 0, 0, 0)) # Clear before drawing
        
        self.render_simulation_stats(physics_engine)
        if selected_atom is not None:
            self.render_atom_info(selected_atom)
        self.render_molecule_info(physics_engine)
        self.render_help_text()
        self.blit_to_screen()
    
    def render_simulation_stats(self, physics_engine):
        """Render simulation statistics."""
        # Background for stats box
        stats_rect = pygame.Rect(10, 10, 200, 100)
        pygame.draw.rect(self.surface, self.background_color, stats_rect)
        pygame.draw.rect(self.surface, self.text_color, stats_rect, 1)
        
        # Title
        title = self.title_font.render("Simulation Stats", True, self.highlight_color)
        self.surface.blit(title, (20, 15))
        
        # Stats
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
        """Render information about the selected atom."""
        # Background for atom info box
        info_rect = pygame.Rect(10, 120, 250, 180)
        pygame.draw.rect(self.surface, self.background_color, info_rect)
        pygame.draw.rect(self.surface, self.text_color, info_rect, 1)
        
        # Title with element name
        title_text = f"Selected: {atom.element_name} ({atom.element_symbol})"
        title = self.title_font.render(title_text, True, self.highlight_color)
        self.surface.blit(title, (20, 125))
        
        # Atom information
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
        """Render information about molecules in the simulation."""
        # Identify molecules
        molecules = physics_engine.identify_common_molecules()
        
        if not molecules:
            return
        
        # Background for molecule info box
        info_rect = pygame.Rect(self.settings.WINDOW_WIDTH - 260, 10, 250, 30 + len(molecules) * 20)
        pygame.draw.rect(self.surface, self.background_color, info_rect)
        pygame.draw.rect(self.surface, self.text_color, info_rect, 1)
        
        # Title
        title = self.title_font.render("Molecules Detected", True, self.highlight_color)
        self.surface.blit(title, (self.settings.WINDOW_WIDTH - 250, 15))
        
        # List molecules
        y = 40
        for molecule in molecules:
            formula = molecule["formula"]
            name = molecule["name"]
            
            # Choose color for molecule
            if formula in self.molecule_colors:
                color = self.molecule_colors[formula]
            else:
                color = self.text_color
            
            text = self.font.render(name, True, color)
            self.surface.blit(text, (self.settings.WINDOW_WIDTH - 250, y))
            y += 20
            
            # Also render formula near the molecule in 3D space
            if hasattr(self.settings, 'SHOW_MOLECULE_LABELS') and self.settings.SHOW_MOLECULE_LABELS:
                self.render_molecule_label(molecule)
    
    def render_molecule_label(self, molecule):
        """Render a label in 3D space for the molecule."""
        # Get molecule center
        center = molecule["center"]
        name = molecule["name"]
        
        # Project 3D position to screen coordinates
        modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
        projection = glGetDoublev(GL_PROJECTION_MATRIX)
        viewport = glGetIntegerv(GL_VIEWPORT)
        
        # Add offset for label (above the molecule)
        label_pos = center + np.array([0, 1.0, 0])  # Raise label above molecule
        
        screen_x, screen_y, screen_z = gluProject(
            label_pos[0], label_pos[1], label_pos[2],
            modelview, projection, viewport
        )
        
        # Only render if in front of camera
        if screen_z < 1.0:
            # Create label surface
            label_surface = self.molecule_font.render(name, True, (255, 255, 255))
            
            # Position the label centered above the molecule
            label_x = int(screen_x - label_surface.get_width() / 2)
            label_y = int(self.settings.WINDOW_HEIGHT - screen_y - label_surface.get_height() / 2)
            
            # Create background for better visibility
            padding = 4
            bg_rect = pygame.Rect(
                label_x - padding, 
                label_y - padding,
                label_surface.get_width() + padding * 2,
                label_surface.get_height() + padding * 2
            )
            pygame.draw.rect(self.surface, (0, 0, 0, 150), bg_rect)
            
            # Draw the label
            self.surface.blit(label_surface, (label_x, label_y))
    
    def render_help_text(self):
        hud_width, hud_height = self.surface.get_size()
        # Position help text to avoid the control panel on the right
        # Control panel width is self.settings.WINDOW_WIDTH - control_panel.width (but control_panel is not directly known here)
        # Let's assume control panel takes about 220px on the right.
        control_panel_width_approx = 220 
        help_box_max_width = hud_width - control_panel_width_approx - 20 # 10px margin on each side
        help_box_height = 28

        help_rect_actual_width = min(680, help_box_max_width) # Cap width of help text box
        help_rect = pygame.Rect(10, hud_height - help_box_height - 10, help_rect_actual_width, help_box_height)
        
        pygame.draw.rect(self.surface, self.background_color, help_rect, border_radius=3)
        pygame.draw.rect(self.surface, self.text_color, help_rect, 1, border_radius=3)
        
        help_str = ("Cam:LMB-Drag,Scroll|Atom:SHIFT+LMB-Drag|1-6:Add|X:ResetSim|R:ResetCam|SPACE:Pause|P,E,O,B,F:Toggles")
        text_surface = self.font.render(help_str, True, self.text_color)
        
        text_x = help_rect.x + (help_rect.width - text_surface.get_width()) // 2
        text_y = help_rect.y + (help_rect.height - text_surface.get_height()) // 2
        if text_surface.get_width() > help_rect.width - 10 : # If text is too long, left align
             text_x = help_rect.x + 5
        self.surface.blit(text_surface, (text_x, text_y))
    
    def blit_to_screen(self):
        """Blit the HUD surface (which is a Pygame surface) to the OpenGL screen as a texture."""
        hud_width, hud_height = self.surface.get_size()
        
        # Convert Pygame surface to texture data
        texture_data = pygame.image.tostring(self.surface, "RGBA", True) # Use RGBA, flip vertically for OpenGL
        
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, hud_width, hud_height, 0,
                       GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
        
        # Save OpenGL state
        glPushAttrib(GL_DEPTH_BUFFER_BIT | GL_LIGHTING_BIT | GL_ENABLE_BIT | GL_TRANSFORM_BIT | GL_VIEWPORT_BIT)
        
        glDisable(GL_DEPTH_TEST) # HUD should always be on top
        glDisable(GL_LIGHTING)   # No lighting for HUD
        glEnable(GL_BLEND)       # Ensure blending is enabled for HUD transparency
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_TEXTURE_2D)

        # Set up orthographic projection for 2D HUD rendering
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, hud_width, hud_height, 0, -1, 1) # Y is 0 at top, hud_height at bottom

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        # Draw a textured quad covering the screen
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glColor4f(1,1,1,1) # Ensure texture is drawn without color modulation from current glColor state
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex2f(0, 0)
        glTexCoord2f(1, 0); glVertex2f(hud_width, 0)
        glTexCoord2f(1, 1); glVertex2f(hud_width, hud_height)
        glTexCoord2f(0, 1); glVertex2f(0, hud_height)
        glEnd()

        # Restore OpenGL state
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

        glPopAttrib() # Restore all saved attributes
        
        # Corrected line:
        glDeleteTextures([texture_id])