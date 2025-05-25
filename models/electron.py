import numpy as np
from models.particle import Particle
import random

class Electron(Particle):
    #Represents an electron in the atomic simulation.
    
    def __init__(self, position=None, velocity=None, settings=None):
        #Initialize an electron with standard electron properties.
        super().__init__(
            position=position, 
            velocity=velocity,
            mass=settings.ELECTRON_MASS if settings else 9.1e-31,  #Electron mass in kg
            charge=-1,  #Elementary negative charge
            spin=0.5,   #Electron spin
            settings=settings
        )
        
        #Electron visualization properties
        self.radius = settings.ELECTRON_RADIUS if settings else 0.05
        self.color = settings.ELECTRON_COLOR if settings else (0.3, 0.3, 1.0)
        
        #Electron quantum properties
        self.principal_quantum_number = 1  #default to ground state
        self.angular_momentum_quantum_number = 0  #s orbital
        self.magnetic_quantum_number = 0
        self.spin_quantum_number = 0.5  # or -0.5
        
        #for visualization, track orbital path
        self.orbital_path = []
        self.max_path_points = settings.ORBITAL_PATH_POINTS if settings else 100
        
    def update_position(self, dt):
        #Update electron position based on quantum mechanics.
        super().update_position(dt)
        
        #Add current position to orbital path
        self.orbital_path.append(np.copy(self.position))
        if len(self.orbital_path) > self.max_path_points:
            self.orbital_path.pop(0)
    
    @staticmethod
    def create_for_orbital(n, l, m, spin, nucleus_position, settings):
        #Create an electron configured for a specific orbital.
        electron = Electron(settings=settings)
        
        #set quantum numbers
        electron.principal_quantum_number = n
        electron.angular_momentum_quantum_number = l
        electron.magnetic_quantum_number = m
        electron.spin_quantum_number = spin
        
        #Calculate orbital radius (simplified Bohr model)
        orbital_radius = n * n * settings.ORBITAL_SCALE_FACTOR
        
        #Calculate initial position based on quantum numbers
        #This is simplified model, in reality, electron positions follow probability distributions
        if l == 0:  # s orbital
            #Random position on sphere
            theta = random.uniform(0, 2 * np.pi)
            phi = random.uniform(0, np.pi)
            x = orbital_radius * np.sin(phi) * np.cos(theta)
            y = orbital_radius * np.sin(phi) * np.sin(theta)
            z = orbital_radius * np.cos(phi)
            electron.position = np.array([x, y, z]) + nucleus_position
            
            #Velocity perpendicular to radius vector for circular motion
            velocity_magnitude = settings.ORBITAL_VELOCITY_FACTOR / np.sqrt(n)
            v_theta = velocity_magnitude * np.array([
                -np.sin(theta), 
                np.cos(theta), 
                0
            ])
            v_phi = velocity_magnitude * np.array([
                np.cos(phi) * np.cos(theta),
                np.cos(phi) * np.sin(theta),
                -np.sin(phi)
            ])
            electron.velocity = v_theta + v_phi
            
        elif l == 1:  #p orbital
            #for p orbitals, align with x, y, or z axis based on m
            if m == -1:
                axis = np.array([1, 0, 0])
            elif m == 0:
                axis = np.array([0, 1, 0])
            else:  # m == 1
                axis = np.array([0, 0, 1])
                
            #create dumbbell-shaped orbital
            distance_along_axis = orbital_radius * (2 * random.random() - 1)
            electron.position = nucleus_position + axis * distance_along_axis
            
            #perpendicular velocity for wobbling motion
            perpendicular_axes = [np.array([1, 0, 0]), np.array([0, 1, 0]), np.array([0, 0, 1])]
            
            #Find an axis that's not aligned with our current axis
            perpendicular_axis = None
            for potential_axis in perpendicular_axes:
                if not np.array_equal(potential_axis, axis):
                    perpendicular_axis = potential_axis
                    break
                    
            electron.velocity = perpendicular_axis * settings.ORBITAL_VELOCITY_FACTOR / np.sqrt(n)
            
        #could add more orbitals for implementation (d, f, etc.)
        
        return electron