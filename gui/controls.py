import pygame
import numpy as np
from OpenGL.GL import *

class ControlPanel:
    #control panel for the simulation interface.
    
    def __init__(self, settings, physics_engine, renderer, simulator_instance):
        self.settings = settings
        self.physics_engine = physics_engine
        self.renderer = renderer
        self.simulator_instance = simulator_instance

        self.width = 230 
        self.height = 0 
        self.x = 0      
        self.y = 0      
        
        # Modern Dark Theme
        self.bg_color = (45, 45, 55, 230)    #dark charcoal blue, mostly opaque
        self.text_color = (220, 220, 225)    #light grey/off-white
        self.title_text_color = (150, 200, 255) #lighter blue for titles
        self.highlight_color = (20, 150, 255)  #accent blue for selections/highlights
        self.button_bg_color = (60, 65, 75, 240) #darker grey for buttons
        self.button_border_color = (80, 85, 95)  
        self.slider_track_color = (80, 85, 95)
        self.slider_handle_color = self.highlight_color

        self.surface = None 