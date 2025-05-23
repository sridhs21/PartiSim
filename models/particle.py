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
        
    def update_position(self, dt):
        #Update the particle position based on velocity and acceleration.
        self.velocity += self.acceleration * dt
        self.position += self.velocity * dt
        
        #reset acceleration for next frame
        self.acceleration = np.zeros(3, dtype=np.float32)
    
    def apply_force(self, force_vector):
        #Apply a force to the particle.
        if self.mass > 0:
            self.acceleration += force_vector / self.mass
        self.forces.append(force_vector)
    
    def clear_forces(self):
        #Clear all accumulated forces.
        self.forces = []
        self.acceleration = np.zeros(3, dtype=np.float32)
    
    def distance_to(self, other_particle):
        #Calculate distance to another particle.
        return np.linalg.norm(self.position - other_particle.position)
    
    def set_quantum_state(self, energy_level, orbital=None):
        #Set the quantum state of the particle.
        self.quantum_state["energy_level"] = energy_level
        self.quantum_state["orbital"] = orbital
        #calculate probability density based on quantum state
        self.update_probability_density()
    
    def update_probability_density(self):
        #Update the probability density based on quantum state.
        #In a real simulation, we would implement quantum mechanical wavefunctions.
        #for this simulation, we'll use simplified models.
        pass