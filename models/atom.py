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
        
    @property
    def nucleus_position(self):
        #Get the current position of the nucleus.
        return self.position
    
    @property
    def charge(self):
        #Calculate the net charge of the atom.
        return len(self.protons) - len(self.electrons)
    
    def update(self, dt):
        #Update the atom and all its particles.
        # Update nucleus position
        self.position += self.velocity * dt
        
        #Update nucleons (simplified as in reality they have much more complex interactions)
        for proton in self.protons:
            proton.position = self.position + np.random.normal(0, self.nucleus_radius / 3, 3)
            proton.update_position(dt)
            
        for neutron in self.neutrons:
            neutron.position = self.position + np.random.normal(0, self.nucleus_radius / 3, 3)
            neutron.update_position(dt)
        
        #Update electrons with quantum mechanical model
        for electron in self.electrons:
            electron.update_position(dt)
            
            #Apply nuclear attraction
            r = electron.position - self.position
            distance = np.linalg.norm(r)
            if distance > 0:
                #Coulomb force: F = k*q1*q2/r^2
                force_magnitude = self.settings.COULOMB_CONSTANT * electron.charge * self.atomic_number / (distance * distance)
                force_direction = -r / distance  # Toward nucleus
                force = force_magnitude * force_direction
                electron.apply_force(force)
                
                #Add small random variation to simulate quantum effects
                quantum_fluctuation = np.random.normal(0, self.settings.QUANTUM_FLUCTUATION, 3)
                electron.apply_force(quantum_fluctuation)
    
    def add_proton(self):
        #Add a proton to the nucleus.
        proton = Proton(position=self.position + np.random.normal(0, 0.01, 3), settings=self.settings)
        self.protons.append(proton)
        self.atomic_number += 1
        self.mass_number += 1
        self.update_element_info()
        self.update_nucleus_radius()
        return proton
    
    def add_neutron(self):
        #Add a neutron to the nucleus.
        neutron = Neutron(position=self.position + np.random.normal(0, 0.01, 3), settings=self.settings)
        self.neutrons.append(neutron)
        self.mass_number += 1
        self.update_nucleus_radius()
        return neutron
    
    def add_electron(self, n=1, l=0, m=0, spin=0.5):
        #Add an electron to the atom in specified orbital.
        electron = Electron.create_for_orbital(n, l, m, spin, self.position, self.settings)
        self.electrons.append(electron)
        return electron