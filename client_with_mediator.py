#!/usr/bin/env python3
"""
Remote Control Client with Mediator Support
This runs on the machine that will be controlled.
It connects to the mediator server to request help and manage control sessions.
"""

import socket
import threading
import time
import pickle
import base64
import io
import logging
import sys
import json
import pyautogui
from PIL import Image, ImageGrab
import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import ttk
import ssl_utils

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("client_log.txt"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("RemoteControlClient")

# Disable PyAutoGUI fail-safe
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0  # ADD THIS LINE - remove pause between operations

# Configuration
REMOTE_CONTROL_PORT = 5555  # Port for direct connection with technician
MEDIATOR_PORT = 5556       # Port for mediator server
SCREENSHOT_INTERVAL = 0.1
BUFFER_SIZE = 8192

class RemoteControlClientWithMediator:
    def __init__(self, username=None):
        # Remote control server (for technician direct connection)
        self.control_server_socket = None
        self.control_running = False
        self.technician_socket = None
        self.technician_address = None
        
        # Mediator connection
        self.mediator_socket = None
        self.mediator_connected = False
        self.client_id = None
        self.help_requested = False
        self.current_session_id = None
        
        # Store username from login
        self.username = username
        
        self.setup_gui()
        
    def setup_gui(self):
        """Set up the modern client GUI."""
        self.root = tk.Tk()
        self.root.title("🖥️ Remote Control Client")
        self.root.geometry("700x800")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Modern color scheme
        self.colors = {
            'primary': '#1a1a2e',
            'secondary': '#16213e',
            'accent': '#e94560',
            'accent_hover': '#ff6b7a',
            'success': '#00d4aa',
            'warning': '#ffa726',
            'error': '#f44336',
            'text_light': '#ffffff',
            'text_secondary': '#a0a0a0',
            'card_bg': '#1e1e3a',
            'input_bg': '#2a2a3e',
            'border': '#3a3a5c'
        }
        
        # Configure main window
        self.root.configure(bg=self.colors['primary'])
        
        # Create scrollable main frame
        self.create_scrollable_frame()
        
        # Header section
        self.create_header()
        
        # Connection section
        self.create_connection_section()
        
        # Status dashboard
        self.create_status_dashboard()
        
        # Help request section
        self.create_help_section()
        
        # Auto-start control server
        self.start_control_server()
        
    def create_scrollable_frame(self):
        """Create a scrollable main frame."""
        # Create canvas and scrollbar
        self.canvas = tk.Canvas(self.root, bg=self.colors['primary'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.colors['primary'])
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
    def create_header(self):
        """Create the header section."""
        header_frame = tk.Frame(self.scrollable_frame, bg=self.colors['primary'])
        header_frame.pack(fill=tk.X, padx=30, pady=(30, 20))
        
        # Title with gradient background effect
        title_bg = tk.Frame(header_frame, bg=self.colors['accent'], height=80)
        title_bg.pack(fill=tk.X)
        title_bg.pack_propagate(False)
        
        title_content = tk.Frame(title_bg, bg=self.colors['accent'])
        title_content.place(relx=0.5, rely=0.5, anchor='center')
        
        # Icon and title
        tk.Label(
            title_content,
            text="🖥️",
            font=('Segoe UI', 24),
            bg=self.colors['accent'],
            fg=self.colors['text_light']
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Label(
            title_content,
            text="Remote Control Client",
            font=('Segoe UI', 20, 'bold'),
            bg=self.colors['accent'],
            fg=self.colors['text_light']
        ).pack(side=tk.LEFT)
        
        # Subtitle
        subtitle_frame = tk.Frame(header_frame, bg=self.colors['primary'])
        subtitle_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Label(
            subtitle_frame,
            text="Ready to receive remote assistance",
            font=('Segoe UI', 12),
            bg=self.colors['primary'],
            fg=self.colors['text_secondary']
        ).pack()
        
    def create_connection_section(self):
        """Create the mediator connection section."""
        section_frame = self.create_section_frame("🔗 Mediator Server Connection")
        
        # Connection grid
        grid_frame = tk.Frame(section_frame, bg=self.colors['card_bg'])
        grid_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Mediator IP input
        tk.Label(
            grid_frame,
            text="🌐 Server IP Address:",
            font=('Segoe UI', 11, 'bold'),
            bg=self.colors['card_bg'],
            fg=self.colors['text_light']
        ).grid(row=0, column=0, sticky='w', pady=(0, 5))
        
        ip_frame = tk.Frame(grid_frame, bg=self.colors['accent'], height=35)
        ip_frame.grid(row=1, column=0, sticky='ew', pady=(0, 15), padx=(0, 20))
        ip_frame.grid_propagate(False)
        
        self.mediator_ip_entry = tk.Entry(
            ip_frame,
            font=('Segoe UI', 11),
            bg=self.colors['input_bg'],
            fg=self.colors['text_light'],
            relief='flat',
            borderwidth=0,
            insertbackground=self.colors['text_light']
        )
        self.mediator_ip_entry.place(x=2, y=2, relwidth=1, relheight=1, width=-4, height=-4)
        self.mediator_ip_entry.insert(0, "127.0.0.1")
        
        # Client name input
        tk.Label(
            grid_frame,
            text="👤 Your Display Name:",
            font=('Segoe UI', 11, 'bold'),
            bg=self.colors['card_bg'],
            fg=self.colors['text_light']
        ).grid(row=0, column=1, sticky='w', pady=(0, 5))
        
        name_frame = tk.Frame(grid_frame, bg=self.colors['accent'], height=35)
        name_frame.grid(row=1, column=1, sticky='ew', pady=(0, 15))
        name_frame.grid_propagate(False)
        
        self.client_name_entry = tk.Entry(
            name_frame,
            font=('Segoe UI', 11),
            bg=self.colors['input_bg'],
            fg=self.colors['text_light'],
            relief='flat',
            borderwidth=0,
            insertbackground=self.colors['text_light']
        )
        self.client_name_entry.place(x=2, y=2, relwidth=1, relheight=1, width=-4, height=-4)
        
        # Set default name
        if self.username:
            default_name = f"{self.username}-{self.get_local_ip()}"
        else:
            default_name = f"Client-{self.get_local_ip()}"
        self.client_name_entry.insert(0, default_name)
        
        # Configure grid weights
        grid_frame.grid_columnconfigure(0, weight=1)
        grid_frame.grid_columnconfigure(1, weight=1)
        
        # Connection buttons
        button_frame = tk.Frame(section_frame, bg=self.colors['card_bg'])
        button_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        self.connect_mediator_button = self.create_modern_button(
            button_frame,
            "🚀 Connect to Server",
            self.connect_to_mediator,
            self.colors['success'],
            side=tk.LEFT
        )
        
        self.disconnect_mediator_button = self.create_modern_button(
            button_frame,
            "🔌 Disconnect",
            self.disconnect_from_mediator,
            self.colors['error'],
            side=tk.LEFT,
            state=tk.DISABLED
        )
        
    def create_status_dashboard(self):
        """Create the status dashboard."""
        section_frame = self.create_section_frame("📊 System Status")
        
        # Status grid
        status_grid = tk.Frame(section_frame, bg=self.colors['card_bg'])
        status_grid.pack(fill=tk.X, padx=20, pady=10)
        
        # Status items - removed control server status
        status_items = [
            ("🔗 Mediator Connection:", "mediator_status_label", "Disconnected", self.colors['error']),
            ("🌐 Your IP Address:", "ip_label", self.get_local_ip(), self.colors['success']),
            ("🔌 Control Port:", "port_label", f"{REMOTE_CONTROL_PORT}", self.colors['text_secondary']),
            ("👨‍💻 Connected Technician:", "technician_label", "None", self.colors['text_secondary'])
        ]
        
        for i, (label_text, attr_name, initial_value, color) in enumerate(status_items):
            row = i // 2
            col = (i % 2) * 2
            
            # Status item frame
            item_frame = tk.Frame(status_grid, bg=self.colors['input_bg'])
            item_frame.grid(row=row, column=col, columnspan=2, sticky='ew', padx=5, pady=5)
            
            # Label
            tk.Label(
                item_frame,
                text=label_text,
                font=('Segoe UI', 10, 'bold'),
                bg=self.colors['input_bg'],
                fg=self.colors['text_light']
            ).pack(side=tk.LEFT, padx=15, pady=10)
            
            # Value
            value_label = tk.Label(
                item_frame,
                text=initial_value,
                font=('Segoe UI', 10),
                bg=self.colors['input_bg'],
                fg=color
            )
            value_label.pack(side=tk.RIGHT, padx=15, pady=10)
            setattr(self, attr_name, value_label)
        
        # Configure grid
        for i in range(4):
            status_grid.grid_columnconfigure(i, weight=1)
            
    def create_help_section(self):
        """Create the help request section."""
        section_frame = self.create_section_frame("🆘 Request Help")
        
        # Help content
        content_frame = tk.Frame(section_frame, bg=self.colors['card_bg'])
        content_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Description
        desc_text = (
            "Need technical assistance? Click the button below to request help from available technicians. "
            "They will be notified and can request to take control of your computer."
        )
        
        tk.Label(
            content_frame,
            text=desc_text,
            font=('Segoe UI', 10),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary'],
            wraplength=600,
            justify=tk.LEFT
        ).pack(anchor='w', pady=(0, 20))
        
        # Help buttons
        button_frame = tk.Frame(content_frame, bg=self.colors['card_bg'])
        button_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.help_button = self.create_modern_button(
            button_frame,
            "🆘 Request Help Now",
            self.request_help,
            self.colors['warning'],
            font_size=12,
            height=45,
            state=tk.DISABLED
        )
        
        self.cancel_help_button = self.create_modern_button(
            button_frame,
            "❌ Cancel Request",
            self.cancel_help,
            self.colors['text_secondary'],
            side=tk.LEFT,
            state=tk.DISABLED
        )
        
        self.end_session_button = self.create_modern_button(
            button_frame,
            "🔚 End Session",
            self.end_session,
            self.colors['error'],
            side=tk.LEFT,
            state=tk.DISABLED
        )
        

        
    def create_section_frame(self, title):
        """Create a styled section frame."""
        # Section container
        section_container = tk.Frame(self.scrollable_frame, bg=self.colors['primary'])
        section_container.pack(fill=tk.X, padx=30, pady=(0, 20))
        
        # Section header
        header_frame = tk.Frame(section_container, bg=self.colors['secondary'], height=50)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text=title,
            font=('Segoe UI', 14, 'bold'),
            bg=self.colors['secondary'],
            fg=self.colors['text_light']
        ).place(relx=0.02, rely=0.5, anchor='w')
        
        # Section content
        content_frame = tk.Frame(section_container, bg=self.colors['card_bg'])
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        return content_frame
        
    def create_modern_button(self, parent, text, command, color, side=None, font_size=11, height=35, state=tk.NORMAL):
        """Create a modern styled button."""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=('Segoe UI', font_size, 'bold'),
            bg=color,
            fg=self.colors['text_light'],
            relief='flat',
            borderwidth=0,
            padx=20,
            pady=8,
            cursor='hand2',
            state=state
        )
        
        if side:
            btn.pack(side=side, padx=5)
        else:
            btn.pack(fill=tk.X)
            
        # Configure button height
        if height != 35:
            btn.configure(pady=int((height-35)/2))
        
        # Hover effects
        def on_enter(e):
            if btn['state'] != 'disabled':
                if color == self.colors['success']:
                    btn.configure(bg='#00f0cc')
                elif color == self.colors['error']:
                    btn.configure(bg='#ff6b6b')
                elif color == self.colors['warning']:
                    btn.configure(bg='#ffb74d')
                elif color == self.colors['accent']:
                    btn.configure(bg=self.colors['accent_hover'])
                else:
                    btn.configure(bg=self.colors['secondary'])
                    
        def on_leave(e):
            if btn['state'] != 'disabled':
                btn.configure(bg=color)
                
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn
        
    def get_local_ip(self):
        """Get the local IP address."""
        try:
            # Connect to a remote server to determine local IP
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except Exception:
            return "127.0.0.1"
            
    def log(self, message):
        """Add a message to the log."""
        timestamp = time.strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        logger.info(message)
        
        # Update GUI log
        self.root.after(0, lambda: self._update_log_gui(log_message))
        
    def _update_log_gui(self, message):
        """Update the GUI log in the main thread."""
        # Log widget removed - only console logging now
        pass
        
    def connect_to_mediator(self):
        """Connect to the mediator server."""
        if self.mediator_connected:
            return
            
        mediator_ip = self.mediator_ip_entry.get().strip()
        client_name = self.client_name_entry.get().strip()
        
        if not mediator_ip:
            messagebox.showerror("Error", "Please enter mediator IP address")
            return
            
        if not client_name:
            messagebox.showerror("Error", "Please enter your name")
            return
            
        self.log(f"Connecting to mediator server at {mediator_ip}:{MEDIATOR_PORT}...")
        
        try:
            # Create secure connection to mediator
            self.mediator_socket = ssl_utils.create_secure_client_socket()
            self.mediator_socket = ssl_utils.connect_secure_client(self.mediator_socket, mediator_ip, MEDIATOR_PORT)
            
            # Send identification message
            connect_message = {
                'type': 'client_connect',
                'name': client_name,
                'ip': self.get_local_ip()
            }
            
            self.mediator_socket.send(json.dumps(connect_message).encode('utf-8'))
            
            # Wait for welcome message
            response = self.mediator_socket.recv(BUFFER_SIZE)
            welcome_msg = json.loads(response.decode('utf-8'))
            
            if welcome_msg['type'] == 'welcome':
                self.client_id = welcome_msg['client_id']
                self.mediator_connected = True
                
                # Update UI
                self.mediator_status_label.config(text="Connected", fg="green")
                self.connect_mediator_button.config(state=tk.DISABLED)
                self.disconnect_mediator_button.config(state=tk.NORMAL)
                self.help_button.config(state=tk.NORMAL)
                
                self.log(f"Connected to mediator server (Client ID: {self.client_id})")
                
                # Start handling mediator messages
                threading.Thread(target=self.handle_mediator_messages, daemon=True).start()
                
            else:
                raise Exception("Invalid welcome message")
                
        except Exception as e:
            self.log(f"Failed to connect to mediator: {str(e)}")
            messagebox.showerror("Connection Error", f"Failed to connect to mediator server:\n{str(e)}")
            if self.mediator_socket:
                try:
                    self.mediator_socket.close()
                except:
                    pass
                self.mediator_socket = None
                
    def disconnect_from_mediator(self):
        """Disconnect from the mediator server."""
        self.mediator_connected = False
        
        if self.mediator_socket:
            try:
                self.mediator_socket.close()
            except:
                pass
            self.mediator_socket = None
            
        # Update UI
        self.mediator_status_label.config(text="Disconnected", fg="red")
        self.connect_mediator_button.config(state=tk.NORMAL)
        self.disconnect_mediator_button.config(state=tk.DISABLED)
        self.help_button.config(state=tk.DISABLED)
        self.cancel_help_button.config(state=tk.DISABLED)
        self.end_session_button.config(state=tk.DISABLED)
        
        self.help_requested = False
        self.client_id = None
        self.current_session_id = None
        
        self.log("Disconnected from mediator server")
        
    def handle_mediator_messages(self):
        """Handle messages from the mediator server."""
        try:
            while self.mediator_connected and self.mediator_socket:
                try:
                    data = self.mediator_socket.recv(BUFFER_SIZE)
                    if not data:
                        break
                        
                    message = json.loads(data.decode('utf-8'))
                    self.process_mediator_message(message)
                    
                except ConnectionError:
                    break
                except Exception as e:
                    self.log(f"Error handling mediator message: {str(e)}")
                    break
                    
        except Exception as e:
            self.log(f"Error in mediator message handler: {str(e)}")
        finally:
            self.disconnect_from_mediator()
            
    def process_mediator_message(self, message):
        """Process a message from the mediator server."""
        msg_type = message.get('type')
        
        if msg_type == 'help_confirmed':
            self.log("Help request confirmed - waiting for technician...")
            self.root.after(0, lambda: self.help_button.config(state=tk.DISABLED))
            self.root.after(0, lambda: self.cancel_help_button.config(state=tk.NORMAL))
            
        elif msg_type == 'control_request':
            self.handle_control_request(message)
            
        elif msg_type == 'heartbeat':
            # Respond to heartbeat
            response = {'type': 'heartbeat_response'}
            try:
                self.mediator_socket.send(json.dumps(response).encode('utf-8'))
            except:
                pass
                
        else:
            self.log(f"Unknown message type from mediator: {msg_type}")
            
    def handle_control_request(self, message):
        """Handle a control request from a technician."""
        tech_name = message.get('technician_name', 'Unknown')
        tech_ip = message.get('technician_ip', 'Unknown')
        tech_id = message.get('tech_id')
        
        self.log(f"Control request from technician: {tech_name} ({tech_ip})")
        
        # Show approval dialog
        result = messagebox.askyesno(
            "Control Request", 
            f"Technician '{tech_name}' ({tech_ip}) wants to control your computer.\n\n"
            "Do you approve this request?",
            icon='question'
        )
        
        # Send response to mediator
        response = {
            'type': 'control_response',
            'tech_id': tech_id,
            'approved': result
        }
        
        try:
            self.mediator_socket.send(json.dumps(response).encode('utf-8'))
            
            if result:
                self.log(f"Approved control request from {tech_name}")
                self.help_requested = False
                self.root.after(0, lambda: self.help_button.config(state=tk.DISABLED))
                self.root.after(0, lambda: self.cancel_help_button.config(state=tk.DISABLED))
            else:
                self.log(f"Denied control request from {tech_name}")
                
        except Exception as e:
            self.log(f"Error sending control response: {str(e)}")
            
    def request_help(self):
        """Request help from technicians."""
        if not self.mediator_connected or self.help_requested:
            return
            
        try:
            help_request = {'type': 'help_request'}
            self.mediator_socket.send(json.dumps(help_request).encode('utf-8'))
            self.help_requested = True
            self.log("Help request sent to mediator server")
            
        except Exception as e:
            self.log(f"Error sending help request: {str(e)}")
            messagebox.showerror("Error", f"Failed to send help request:\n{str(e)}")
            
    def cancel_help(self):
        """Cancel help request."""
        if not self.mediator_connected or not self.help_requested:
            return
            
        try:
            cancel_request = {'type': 'cancel_help'}
            self.mediator_socket.send(json.dumps(cancel_request).encode('utf-8'))
            self.help_requested = False
            
            # Update UI
            self.help_button.config(state=tk.NORMAL)
            self.cancel_help_button.config(state=tk.DISABLED)
            
            self.log("Help request cancelled")
            
        except Exception as e:
            self.log(f"Error cancelling help request: {str(e)}")
            
    def end_session(self):
        """End the current control session."""
        if not self.technician_socket:
            return
            
        # Show confirmation dialog
        result = messagebox.askyesno(
            "End Session", 
            "Are you sure you want to end the current control session?\n\n"
            "The technician will be disconnected.",
            icon='question'
        )
        
        if result:
            self.log("Session ended by client")
            
            # Notify mediator if we have a session ID
            if self.mediator_connected and self.current_session_id:
                try:
                    end_session_msg = {
                        'type': 'end_session',
                        'session_id': self.current_session_id
                    }
                    self.mediator_socket.send(json.dumps(end_session_msg).encode('utf-8'))
                except Exception as e:
                    self.log(f"Error notifying mediator about session end: {str(e)}")
            
            # Disconnect the technician
            self.disconnect_technician()
            
            # Reset session state
            self.current_session_id = None
            
    def start_control_server(self):
        """Start the control server for direct technician connection."""
        if self.control_running:
            return
            
        try:
            # Create secure control server
            self.control_server_socket = ssl_utils.create_secure_server_socket("0.0.0.0", REMOTE_CONTROL_PORT)
            self.control_server_socket.listen(1)
            
            self.control_running = True
            
            self.log(f"🔐 Secure control server started on {self.get_local_ip()}:{REMOTE_CONTROL_PORT} with SSL encryption")
            
            # Start accepting connections in a separate thread
            threading.Thread(target=self.accept_control_connections, daemon=True).start()
            
        except Exception as e:
            self.log(f"❌ Error starting secure control server: {str(e)}")
            messagebox.showerror("Error", f"Failed to start secure control server: {str(e)}")
            
    def stop_control_server(self):
        """Stop the control server."""
        self.control_running = False
        
        if self.technician_socket:
            try:
                self.technician_socket.close()
            except:
                pass
            self.technician_socket = None
            self.technician_address = None
            
        if self.control_server_socket:
            try:
                self.control_server_socket.close()
            except:
                pass
            self.control_server_socket = None
            
        self.log("Control server stopped")
        
    def accept_control_connections(self):
        """Accept incoming control connections from technicians."""
        try:
            while self.control_running:
                try:
                    tech_socket, tech_address = self.control_server_socket.accept()
                    self.log(f"Control connection from {tech_address[0]}:{tech_address[1]}")
                    
                    # Only allow one technician at a time
                    if self.technician_socket:
                        self.log("Rejecting control connection - technician already connected")
                        tech_socket.close()
                        continue
                        
                    self.technician_socket = tech_socket
                    self.technician_address = tech_address
                    
                    self.root.after(0, lambda: self.technician_label.config(
                        text=f"{tech_address[0]}:{tech_address[1]}", fg="green"))
                    
                    # Enable end session button when technician connects
                    self.root.after(0, lambda: self.end_session_button.config(state=tk.NORMAL))
                    self.root.after(0, lambda: self.help_button.config(state=tk.DISABLED))
                    
                    # Start handling this technician
                    threading.Thread(target=self.handle_technician, daemon=True).start()
                    threading.Thread(target=self.send_screenshots, daemon=True).start()
                    
                except socket.error:
                    if self.control_running:
                        self.log("Error accepting control connection")
                    break
                    
        except Exception as e:
            if self.control_running:
                self.log(f"Error in accept_control_connections: {str(e)}")
                
    def handle_technician(self):
        """Handle commands from the connected technician."""
        try:
            while self.control_running and self.technician_socket:
                try:
                    data = self.technician_socket.recv(BUFFER_SIZE)
                    if not data:
                        break
                        
                    command = pickle.loads(data)
                    self.process_command(command)
                    
                except ConnectionError:
                    break
                except Exception as e:
                    self.log(f"Error handling technician command: {str(e)}")
                    break
                    
        except Exception as e:
            self.log(f"Error in handle_technician: {str(e)}")
        finally:
            self.disconnect_technician()
            
    def process_command(self, command):
        """Process a command from the technician."""
        try:
            command_type = command.get('type')
            
            if command_type == 'mouse_move':
                x, y = command['x'], command['y']
                pyautogui.moveTo(x, y)
                
            elif command_type == 'mouse_click':
                x, y = command['x'], command['y']
                button = command.get('button', 'left')
                pyautogui.click(x, y, button=button)
                
            elif command_type == 'key_press':
                key = command['key']
                # Handle special characters and keys
                if len(key) == 1:
                    pyautogui.press(key)
                else:
                    # Handle special key names
                    pyautogui.press(key)
                
            elif command_type == 'key_combination':
                keys = command['keys']
                pyautogui.hotkey(*keys)
                
            elif command_type == 'write':
                text = command['text']
                # Use typewrite for better text input handling
                pyautogui.typewrite(text, interval=0.01)
                
            elif command_type == 'ping':
                # Keep-alive ping, no action needed
                pass
                
        except Exception as e:
            self.log(f"Error processing command: {str(e)}")
            
    def send_screenshots(self):
        """Send screenshots to the connected technician with improved error handling."""
        consecutive_failures = 0
        max_failures = 5
        
        try:
            while self.control_running and self.technician_socket:
                try:
                    # Capture screenshot
                    screenshot = ImageGrab.grab()
                    
                    # Get cursor position
                    cursor_x, cursor_y = pyautogui.position()
                    
                    # Convert to bytes with optimized quality
                    img_byte_arr = io.BytesIO()
                    screenshot.save(img_byte_arr, format='JPEG', quality=60, optimize=True)
                    img_bytes = img_byte_arr.getvalue()
                    
                    # Prepare data packet
                    data_packet = {
                        'image': base64.b64encode(img_bytes),
                        'cursor_x': cursor_x,
                        'cursor_y': cursor_y
                    }
                    
                    # Serialize and send
                    data = pickle.dumps(data_packet)
                    size = len(data)
                    
                    # Send size first, then data
                    size_bytes = size.to_bytes(4, byteorder='big')
                    
                    # Set shorter timeout for sending
                    original_timeout = self.technician_socket.gettimeout()
                    self.technician_socket.settimeout(10.0)
                    
                    self.technician_socket.sendall(size_bytes)
                    self.technician_socket.sendall(data)
                    
                    # Restore timeout
                    if original_timeout:
                        self.technician_socket.settimeout(original_timeout)
                    
                    # Reset failure counter on success
                    consecutive_failures = 0
                    
                    time.sleep(SCREENSHOT_INTERVAL)
                    
                except ConnectionError:
                    self.log("Screenshot: Connection lost")
                    break
                except socket.timeout:
                    consecutive_failures += 1
                    self.log(f"Screenshot timeout ({consecutive_failures}/{max_failures})")
                    if consecutive_failures >= max_failures:
                        self.log("Too many screenshot timeouts - disconnecting")
                        break
                except Exception as e:
                    consecutive_failures += 1
                    self.log(f"Error sending screenshot: {str(e)}")
                    if consecutive_failures >= max_failures:
                        self.log("Too many screenshot errors - disconnecting")
                        break
                    time.sleep(0.5)  # Brief pause before retry
                    
        except Exception as e:
            self.log(f"Error in send_screenshots: {str(e)}")
        finally:
            self.disconnect_technician()
            
    def disconnect_technician(self):
        """Disconnect the current technician."""
        if self.technician_socket:
            try:
                self.technician_socket.close()
            except:
                pass
            self.technician_socket = None
            self.technician_address = None
            
            self.root.after(0, lambda: self.technician_label.config(text="None", fg="gray"))
            
            # Disable end session button when technician disconnects
            self.root.after(0, lambda: self.end_session_button.config(state=tk.DISABLED))
            
            # Re-enable help button if connected to mediator
            if self.mediator_connected and not self.help_requested:
                self.root.after(0, lambda: self.help_button.config(state=tk.NORMAL))
            
            self.log("Technician disconnected")
            
    def on_close(self):
        """Handle window close event."""
        self.disconnect_from_mediator()
        self.stop_control_server()
        self.root.destroy()
        
    def run(self):
        """Run the client application."""
        self.root.mainloop()

def main():
    """Main function to run the client application."""
    # Get username from command line argument if provided
    username = None
    if len(sys.argv) > 1:
        username = sys.argv[1]
    
    try:
        app = RemoteControlClientWithMediator(username)
        app.run()
    except Exception as e:
        print(f"Error starting client: {str(e)}")
        logging.error(f"Error starting client: {str(e)}")

if __name__ == "__main__":
    main() 