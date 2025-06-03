import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from gui.controls import ControlPanel
from gui.hud import HUD

class SimulationWindow:
    #this is the main window for the 3D atomic simulation.
    
    def __init__(self, settings, physics_engine, renderer):
        #initialize the simulation window.
        self.settings = settings
        self.physics_engine = physics_engine
        self.renderer = renderer
        
        # initialize control panel
        self.control_panel = ControlPanel(settings, physics_engine, renderer)
        
        # initialize HUD
        self.hud = HUD(settings)
        
        # input handling
        self.mouse_prev_pos = (0, 0)
        self.is_dragging = False
        self.selected_atom = None
        
        #Clock for frame timing
        self.clock = pygame.time.Clock()
        self.running = True