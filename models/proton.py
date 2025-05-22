import numpy as np
from models.particle import Particle

class Proton(Particle):
    """Represents a proton in the atomic simulation."""
    
    def __init__(self, position=None, velocity=None, settings=None):
        """Initialize a proton with standard proton properties."""
        super().__init__(
            position=position, 
            velocity=velocity,
            mass=settings.PROTON_MASS if settings else 1.673e-27,  # Proton mass in kg
            charge=1,   # Elementary positive charge
            spin=0.5,   # Proton spin
            settings=settings
        )
        
        # Proton visualization properties
        self.radius = settings.PROTON_RADIUS if settings else 0.1
        self.color = settings.PROTON_COLOR if settings else (1.0, 0.3, 0.3)
        
        # Quark composition (for advanced simulations)
        self.quarks = {
            "up": 2,
            "down": 1
        }