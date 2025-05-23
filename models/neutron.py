import numpy as np
from models.particle import Particle

class Neutron(Particle):
    #Represents a neutron in the atomic simulation.
    
    def __init__(self, position=None, velocity=None, settings=None):
        #Initialize a neutron with standard neutron properties.
        super().__init__(
            position=position, 
            velocity=velocity,
            mass=settings.NEUTRON_MASS if settings else 1.675e-27,  #Neutron mass in kg
            charge=0,   #Neutrons have no charge
            spin=0.5,   #Neutron spin
            settings=settings
        )
        
        #Neutron visualization properties
        self.radius = settings.NEUTRON_RADIUS if settings else 0.1
        self.color = settings.NEUTRON_COLOR if settings else (0.7, 0.7, 0.7)
        
        #quark composition (for advanced simulations)
        self.quarks = {
            "up": 1,
            "down": 2
        }
        
        #Track decay probability (neutrons can decay into protons)
        self.decay_probability = 0.0
        self.decay_timer = 0.0