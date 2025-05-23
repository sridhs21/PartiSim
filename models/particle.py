import numpy as np
from uuid import uuid4

class Particle:
    #Base class for all quantum particles.
    
    def __init__(self, position=None, velocity=None, mass=0, charge=0, spin=0, settings=None):
        #Initialize a quantum particle with physical properties.
        self.id = uuid4()  # Unique identifier
        self.settings = settings
        
        #position and motion (3D vectors)
        self.position = np.array(position if position is not None else [0.0, 0.0, 0.0], dtype=np.float32)
        self.velocity = np.array(velocity if velocity is not None else [0.0, 0.0, 0.0], dtype=np.float32)
        self.acceleration = np.zeros(3, dtype=np.float32)
        
        #physical properties
        self.mass = mass
        self.charge = charge  # Electric charge
        self.spin = spin      # Quantum spin
        
        #Visualization properties
        self.radius = 0.0
        self.color = (1.0, 1.0, 1.0)
        
        #Track forces acting on this particle
        self.forces = []
        
        #quantum state
        self.quantum_state = {
            "energy_level": 0,
            "orbital": None,
            "probability_density": None
        }