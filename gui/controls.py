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
        
        pygame.font.init()
        try:
            self.font = pygame.font.SysFont('Verdana', 12) 
            self.title_font = pygame.font.SysFont('Verdana', 14, bold=True)
        except Exception:
            print("Verdana font not found, using Pygame default.")
            self.font = pygame.font.Font(None, 18) 
            self.title_font = pygame.font.Font(None, 20)

        default_renderer_show_state = True

        self.controls = [
            {'name': 'Simulation Controls', 'type': 'title'},
            {'name': 'Toggle Nuclei (P)', 'type': 'toggle', 'value': getattr(self.renderer, 'show_nucleus', default_renderer_show_state), 'action': self.toggle_show_nucleus},
            {'name': 'Toggle Electrons (E)', 'type': 'toggle', 'value': getattr(self.renderer, 'show_electrons', default_renderer_show_state), 'action': self.toggle_show_electrons},
            {'name': 'Toggle Orbitals (O)', 'type': 'toggle', 'value': getattr(self.renderer, 'show_orbitals', default_renderer_show_state), 'action': self.toggle_show_orbitals},
            {'name': 'Toggle Bonds (B)', 'type': 'toggle', 'value': getattr(self.renderer, 'show_bonds', default_renderer_show_state), 'action': self.toggle_show_bonds},
            {'name': 'Toggle Forces (F)', 'type': 'toggle', 'value': getattr(self.renderer, 'show_forces', False), 'action': self.toggle_show_forces},
            {'name': 'Simulation State', 'type': 'title'},
            {'name': 'Pause/Resume (SPACE)', 'type': 'button', 'get_text': lambda: "Resume Sim" if self.physics_engine.paused else "Pause Sim", 'action': self.toggle_pause_resume_sim},
            {'name': 'Simulation Speed', 'type': 'slider', 'value': self.physics_engine.time_scale, 'min': 0.1, 'max': 3.0, 'action': self.set_sim_speed},
            {'name': 'Reset Simulation (X)', 'type': 'button', 'action': lambda: self.simulator_instance.reset_simulation()},
            {'name': 'Reset Camera (R)', 'type': 'button', 'action': lambda: self.simulator_instance.reset_camera_view()},
            {'name': 'Clear All Atoms', 'type': 'button', 'action': self.clear_all_atoms_panel},
            {'name': 'Add Elements', 'type': 'title'},
            {'name': 'Add Hydrogen (1)', 'type': 'button', 'action': lambda: self.simulator_instance.add_element(1)},
            {'name': 'Add Helium (2)', 'type': 'button', 'action': lambda: self.simulator_instance.add_element(2)},
            {'name': 'Add Lithium (3)', 'type': 'button', 'action': lambda: self.simulator_instance.add_element(3)},
            {'name': 'Add Carbon (4)', 'type': 'button', 'action': lambda: self.simulator_instance.add_element(6)},
            {'name': 'Add Nitrogen (5)', 'type': 'button', 'action': lambda: self.simulator_instance.add_element(7)},
            {'name': 'Add Oxygen (6)', 'type': 'button', 'action': lambda: self.simulator_instance.add_element(8)},
        ]
        
        self.active_control = None
        self.scroll_offset_y = 0
        self.max_scroll = 0 
        self.content_height = self._calculate_content_height() #calculate once initially

    def _calculate_content_height(self):
        height = 15 
        title_h = 28 
        item_h = 24  
        slider_h = 35 
        spacing = 4 

        for control in self.controls:
            if control['type'] == 'title': height += title_h
            elif control['type'] == 'slider': height += slider_h
            else: height += item_h
            height += spacing
        height += 15 
        return height

    def update_control_value(self, name, new_value):
        for control in self.controls:
            if control.get('name') == name and 'value' in control:
                control['value'] = new_value; return
    def toggle_show_nucleus(self): self.renderer.show_nucleus = not self.renderer.show_nucleus; self.update_control_value('Toggle Nuclei (P)', self.renderer.show_nucleus)
    def toggle_show_electrons(self): self.renderer.show_electrons = not self.renderer.show_electrons; self.update_control_value('Toggle Electrons (E)', self.renderer.show_electrons)
    def toggle_show_orbitals(self): self.renderer.show_orbitals = not self.renderer.show_orbitals; self.update_control_value('Toggle Orbitals (O)', self.renderer.show_orbitals)
    def toggle_show_bonds(self): self.renderer.show_bonds = not self.renderer.show_bonds; self.update_control_value('Toggle Bonds (B)', self.renderer.show_bonds)
    def toggle_show_forces(self): self.renderer.show_forces = not self.renderer.show_forces; self.update_control_value('Toggle Forces (F)', self.renderer.show_forces)
    def toggle_pause_resume_sim(self): self.physics_engine.paused = not self.physics_engine.paused
    def set_sim_speed(self, value): self.physics_engine.time_scale = round(value,1); self.update_control_value('Simulation Speed', self.physics_engine.time_scale)
    def clear_all_atoms_panel(self): self.physics_engine.atoms.clear(); self.simulator_instance.selected_atom = None


    def handle_scroll(self, event_button, panel_rect_abs):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if panel_rect_abs.collidepoint(mouse_x, mouse_y) and self.max_scroll > 0:
            scroll_amount = 35 
            if event_button == 4: self.scroll_offset_y = max(0, self.scroll_offset_y - scroll_amount)
            elif event_button == 5: self.scroll_offset_y = min(self.max_scroll, self.scroll_offset_y + scroll_amount)
            return True
        return False

    def handle_click(self, pos):
        local_pos = (pos[0] - self.x, pos[1] - self.y)
        if not (0 <= local_pos[0] <= self.width and 0 <= local_pos[1] <= self.height): return False
        
        content_y = 15 
        title_h = 28; item_h = 24; slider_h = 35; spacing = 4
        clicked_y_on_content = local_pos[1] + self.scroll_offset_y

        for ctrl_idx, control in enumerate(self.controls):
            ctrl_top_on_content = content_y
            current_item_h = 0
            if control['type'] == 'title': current_item_h = title_h
            elif control['type'] == 'slider': current_item_h = slider_h
            else: current_item_h = item_h
            ctrl_bottom_on_content = ctrl_top_on_content + current_item_h

            #check if click is within this control's Y bounds on the virtual (scrolled) surface
            if ctrl_top_on_content <= clicked_y_on_content < ctrl_bottom_on_content:
                #now check X bounds on the panel (local_pos[0])
                # assuming controls are mostly full width with some padding
                if 10 <= local_pos[0] <= self.width - 10:
                    if control['type'] == 'toggle' or control['type'] == 'button':
                        if 'action' in control: control['action']()
                        return True
                    elif control['type'] == 'slider':
                        # More precise slider click detection
                        #Slider track usually takes a portion of the width
                        slider_label_width_approx = self.width * 0.4
                        slider_value_width_approx = self.width * 0.2
                        track_x_start = slider_label_width_approx 
                        track_width = self.width - slider_label_width_approx - slider_value_width_approx - 20
                        
                        if track_x_start <= local_pos[0] < track_x_start + track_width:
                            slider_pos_ratio = (local_pos[0] - track_x_start) / float(track_width)
                            slider_pos_ratio = max(0.0, min(1.0, slider_pos_ratio)) 
                            value = control['min'] + (control['max'] - control['min']) * slider_pos_ratio
                            if 'action' in control: control['action'](value)
                            self.active_control = control 
                            return True
            content_y += current_item_h + spacing
        return False

    def handle_drag(self, pos): #similar logic for slider drag
        if self.active_control and self.active_control['type'] == 'slider':
            local_x = pos[0] - self.x
            control = self.active_control
            slider_label_width_approx = self.width * 0.4 
            slider_value_width_approx = self.width * 0.2
            track_x_start = slider_label_width_approx
            track_width = self.width - slider_label_width_approx - slider_value_width_approx - 20
            
            slider_pos_ratio = (local_x - track_x_start) / float(track_width if track_width > 0 else 1)
            slider_pos_ratio = max(0.0, min(1.0, slider_pos_ratio))
            value = control['min'] + (control['max'] - control['min']) * slider_pos_ratio
            if 'action' in control: control['action'](value)
            return True
        return False

    def handle_release(self):
        released_active = self.active_control is not None
        self.active_control = None
        return released_active

    def render(self):
        current_window_width, current_window_height = pygame.display.get_surface().get_size()
        self.height = current_window_height
        self.x = current_window_width - self.width 
        self.y = 0 

        if self.surface is None or \
           self.surface.get_width() != self.width or \
           self.surface.get_height() != self.height:
            self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        self.surface.fill(self.bg_color) 
        
        self.content_height = self._calculate_content_height() #recalculate in case controls change
        self.max_scroll = max(0, self.content_height - self.height)
        self.scroll_offset_y = max(0, min(self.scroll_offset_y, self.max_scroll))

        y_on_surface_content = 15 #starting Y for content on the virtual surface area
        title_h = 28; item_h = 24; slider_h = 35; spacing = 4
        padding_x = 10 #Horizontal padding for items

        print(f"--- Panel Render Cycle (Scroll: {self.scroll_offset_y}/{self.max_scroll}) ---")

        for ctrl_idx, control in enumerate(self.controls):
            y_draw = y_on_surface_content - self.scroll_offset_y
            current_item_h = 0 
            if control['type'] == 'title': current_item_h = title_h
            elif control['type'] == 'slider': current_item_h = slider_h
            else: current_item_h = item_h 
            
            #culling
            if (y_draw + current_item_h) < 0 or y_draw > self.height :
                print(f"  Culled: {control.get('name', 'N/A')} at y_draw={y_draw}")
                y_on_surface_content += current_item_h + spacing
                continue
            
            print(f"  Drawing: {control.get('name', 'N/A')} at y_draw={y_draw}, Type: {control['type']}")

            if control['type'] == 'title':
                title_surf = self.title_font.render(control['name'], True, self.title_text_color)
                self.surface.blit(title_surf, (padding_x, y_draw + (current_item_h - title_surf.get_height()) // 2))
            
            elif control['type'] == 'toggle':
                label_surf = self.font.render(control['name'], True, self.text_color)
                self.surface.blit(label_surf, (padding_x + 5, y_draw + (current_item_h - label_surf.get_height()) // 2))
                
                box_size = 16
                box_rect = pygame.Rect(self.width - padding_x - box_size, y_draw + (current_item_h - box_size) // 2, box_size, box_size)
                pygame.draw.rect(self.surface, self.button_border_color, box_rect, 1, border_radius=2)
                if control.get('value', False):
                    inner_rect = box_rect.inflate(-6, -6) # Make inner check smaller
                    pygame.draw.rect(self.surface, self.highlight_color, inner_rect, border_radius=2)

            elif control['type'] == 'button':
                button_rect = pygame.Rect(padding_x, y_draw, self.width - 2*padding_x, current_item_h)
                pygame.draw.rect(self.surface, self.button_bg_color, button_rect, border_radius=3)
                pygame.draw.rect(self.surface, self.button_border_color, button_rect, 1, border_radius=3)
                
                text_to_render = control['name']
                if 'get_text' in control: text_to_render = control['get_text']()
                label_surf = self.font.render(text_to_render, True, self.text_color)
                label_rect = label_surf.get_rect(center=button_rect.center)
                self.surface.blit(label_surf, label_rect)

            elif control['type'] == 'slider':
                label_text = control['name']
                value_text = f"{control.get('value', 0.0):.1f}" #one decimal for speed

                label_surf = self.font.render(label_text, True, self.text_color)
                value_surf = self.font.render(value_text, True, self.highlight_color)
                
                #layout: Label [Track] Value
                label_y = y_draw + 5
                self.surface.blit(label_surf, (padding_x, label_y))
                
                value_width_approx = value_surf.get_width()
                value_x_pos = self.width - padding_x - value_width_approx
                self.surface.blit(value_surf, (value_x_pos, label_y))

                track_y_pos = y_draw + item_h + 5 # item_h used for text lines, slider_h for total
                track_x_start = padding_x + label_surf.get_width() + 5
                track_width_available = value_x_pos - track_x_start - 5
                track_rect = pygame.Rect(track_x_start, track_y_pos, track_width_available, 8) 
                pygame.draw.rect(self.surface, self.slider_track_color, track_rect, border_radius=4)
                
                handle_val = control.get('value', control['min'])
                min_val, max_val = control['min'], control['max']
                handle_ratio = 0.0
                if (max_val - min_val) != 0: #to avoid division by zero
                    handle_ratio = (handle_val - min_val) / (max_val - min_val)
                handle_ratio = max(0.0, min(1.0, handle_ratio)) #clamp

                handle_x = track_rect.left + (track_rect.width * handle_ratio)
                handle_rect_shape = pygame.Rect(0, 0, 10, 18) 
                handle_rect_shape.center = (int(handle_x), track_rect.centery)
                pygame.draw.rect(self.surface, self.slider_handle_color, handle_rect_shape, border_radius=3)
            
            y_on_surface_content += current_item_h + spacing
        
        try:
            pygame.image.save(self.surface, "debug_control_panel_surface_final.png")
        except Exception as e: print(f"Error saving final debug surface: {e}")

        #blit panel surface to screen using OpenGL
        push_mask = (GL_DEPTH_BUFFER_BIT | GL_LIGHTING_BIT | GL_ENABLE_BIT | 
                     GL_TRANSFORM_BIT | GL_VIEWPORT_BIT | GL_TEXTURE_BIT | 
                     GL_COLOR_BUFFER_BIT | GL_POLYGON_BIT)
        glPushAttrib(push_mask) 

        glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
        glOrtho(0, current_window_width, current_window_height, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()

        glDisable(GL_DEPTH_TEST); glDisable(GL_LIGHTING); glDisable(GL_CULL_FACE) 
        glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA); 
        glEnable(GL_TEXTURE_2D)
        
        texture_data = pygame.image.tostring(self.surface, "RGBA", True) 
        texture_id = glGenTextures(1)
        if texture_id == 0:
            print("Error: glGenTextures returned 0 for ControlPanel!"); glPopAttrib(); return

        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR) # Smoother if scaled
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.width, self.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
        
        glColor4f(1.0, 1.0, 1.0, 1.0) 
        glBegin(GL_QUADS)
        glTexCoord2f(0, 1); glVertex2f(self.x, self.y) 
        glTexCoord2f(1, 1); glVertex2f(self.x + self.width, self.y) 
        glTexCoord2f(1, 0); glVertex2f(self.x + self.width, self.y + self.height) 
        glTexCoord2f(0, 0); glVertex2f(self.x, self.y + self.height) 
        glEnd()
        
        glBindTexture(GL_TEXTURE_2D, 0) 
        glDeleteTextures([texture_id])

        glMatrixMode(GL_PROJECTION); glPopMatrix()
        glMatrixMode(GL_MODELVIEW); glPopMatrix()
        glPopAttrib()