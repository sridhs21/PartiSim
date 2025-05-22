import numpy as np
import random
from models.electron import Electron
from models.proton import Proton
from models.neutron import Neutron

class Atom:
    #Represents an atom with nucleus and electrons.
    
    def __init__(self, position=None, settings=None):
        #Initialize an atom at a given position.
        self.settings = settings
        self.position = np.array(position if position is not None else [0.0, 0.0, 0.0], dtype=np.float32)
        self.velocity = np.zeros(3, dtype=np.float32)
        
        #Particles
        self.protons = []
        self.neutrons = []
        self.electrons = []
        
        #Atomic properties
        self.atomic_number = 0  #Number of protons
        self.mass_number = 0    #Protons + neutrons
        self.element_name = ""
        self.element_symbol = ""
        
        #Energy state
        self.energy = 0.0
        self.temperature = 0.0
        
        #For visualization
        self.nucleus_radius = 0.0
        self.electron_shell_radii = []
        self.color = (0.0, 0.0, 0.0)
        
        #For interactions
        self.bonds = []