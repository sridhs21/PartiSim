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
    
    def build_electron_configuration(self):
        #Build electron configuration based on atomic number.
        #Clear existing electrons
        self.electrons = []
        
        #Simplified electron configuration according to aufbau principle
        shells = [
            {"n": 1, "orbitals": [(0, 0, 0.5), (0, 0, -0.5)]},  # 1s (2 electrons)
            {"n": 2, "orbitals": [(0, 0, 0.5), (0, 0, -0.5),    # 2s (2 electrons)
                                 (1, -1, 0.5), (1, -1, -0.5),   # 2p (6 electrons)
                                 (1, 0, 0.5), (1, 0, -0.5),
                                 (1, 1, 0.5), (1, 1, -0.5)]},
            {"n": 3, "orbitals": [(0, 0, 0.5), (0, 0, -0.5),    # 3s (2 electrons)
                                 (1, -1, 0.5), (1, -1, -0.5),   # 3p (6 electrons)
                                 (1, 0, 0.5), (1, 0, -0.5),
                                 (1, 1, 0.5), (1, 1, -0.5)]},   # 3d would follow
            #more shells could be added
        ]
        
        electrons_to_add = self.atomic_number
        for shell in shells:
            for orbital in shell["orbitals"]:
                if electrons_to_add <= 0:
                    break
                self.add_electron(shell["n"], orbital[0], orbital[1], orbital[2])
                electrons_to_add -= 1
            if electrons_to_add <= 0:
                break
    
    def update_element_info(self):
        #Update element name and symbol based on atomic number.
        elements = {
            1: ("Hydrogen", "H"),
            2: ("Helium", "He"),
            3: ("Lithium", "Li"),
            4: ("Beryllium", "Be"),
            5: ("Boron", "B"),
            6: ("Carbon", "C"),
            7: ("Nitrogen", "N"),
            8: ("Oxygen", "O"),
            #Add more elements as needed
        }
        
        if self.atomic_number in elements:
            self.element_name, self.element_symbol = elements[self.atomic_number]
        else:
            self.element_name = f"Element-{self.atomic_number}"
            self.element_symbol = f"E{self.atomic_number}"
    
    def update_nucleus_radius(self):
        #Update the nucleus radius based on mass number.
        #Empirical formula: R = r0 * A^(1/3)
        r0 = self.settings.NUCLEUS_RADIUS_CONSTANT
        self.nucleus_radius = r0 * (self.mass_number ** (1/3))
    
    @staticmethod
    def create_element(atomic_number, neutron_count=None, position=None, settings=None):
        #Create an atom of a specified element.
        atom = Atom(position=position, settings=settings)
        
        #Add protons
        for _ in range(atomic_number):
            atom.add_proton()
        
        #Add neutrons (default to stable isotope)
        if neutron_count is None:
            #Simple approximation for stable isotopes
            if atomic_number <= 20:
                neutron_count = atomic_number
            else:
                neutron_count = int(1.5 * atomic_number)
        
        for _ in range(neutron_count):
            atom.add_neutron()
        
        #Build electron configuration
        atom.build_electron_configuration()
        
        return atom
    
    @staticmethod
    def create_random(settings):
        #Create a random atom within parameters.
        atomic_number = random.randint(1, 8)  #Keep it simple for visualization
        position = np.array([
            random.uniform(-settings.SIMULATION_BOUNDS, settings.SIMULATION_BOUNDS),
            random.uniform(-settings.SIMULATION_BOUNDS, settings.SIMULATION_BOUNDS),
            random.uniform(-settings.SIMULATION_BOUNDS, settings.SIMULATION_BOUNDS)
        ])
        
        return Atom.create_element(atomic_number, position=position, settings=settings)