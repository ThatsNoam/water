#!/usr/bin/env python3
"""
Remote Control Technician with Mediator Support
This runs on the technician's machine.
It connects to the mediator server to see help requests and manage control sessions.
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
from PIL import Image, ImageTk, ImageDraw
import tkinter as tk
from tkinter import messagebox, simpledialog, scrolledtext, ttk
import ssl_utils

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("technician_log.txt"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("RemoteControlTechnician")

# Configuration
MEDIATOR_PORT = 5556
REMOTE_CONTROL_PORT = 5555
BUFFER_SIZE = 8192
SOCKET_TIMEOUT = 30

class RemoteControlTechnicianWithMediator:
    def __init__(self, username=None):
        # Mediator connection
        self.mediator_socket = None
        self.mediator_connected = False
        self.technician_id = None
        
        # Direct control connection
        self.control_socket = None
        self.control_connected = False
        self.control_running = False
        self.current_client_ip = None
        self.current_session_id = None
        
        # Screen control variables
        self.scale_factor_x = 1.0
        self.scale_factor_y = 1.0
        self.cursor_x = 0
        self.cursor_y = 0
        self.keyboard_focus = False
        
        # Help requests list
        self.help_requests = {}  # client_id: {name, ip, timestamp}
        
        # Store username from login
        self.username = username
        
        self.setup_gui()

    def setup_gui(self):
        """Set up the modern technician GUI."""
        self.root = tk.Tk()
        self.root.title("🔧 Remote Control Technician")
        self.root.geometry("1600x1000")
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
            'info': '#2196f3',
            'text_light': '#ffffff',
            'text_secondary': '#a0a0a0',
            'card_bg': '#1e1e3a',
            'input_bg': '#2a2a3e',
            'border': '#3a3a5c'
        }
        
        # Configure main window
        self.root.configure(bg=self.colors['primary'])
        
        # Create main layout
        self.create_main_layout()
        
        # Bind keyboard events
        self.root.bind("<KeyPress>", self.on_key_press)
        self.root.bind("<KeyRelease>", self.on_key_release)
        
    def create_main_layout(self):
        """Create the main layout with modern design."""
        # Header
        self.create_header()
        
        # Main content area
        main_content = tk.Frame(self.root, bg=self.colors['primary'])
        main_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Create horizontal paned window
        paned_window = ttk.PanedWindow(main_content, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Left panel (350px width)
        self.left_panel = tk.Frame(paned_window, bg=self.colors['card_bg'], width=350)
        paned_window.add(self.left_panel, weight=0)
        
        # Right panel (remaining space)
        self.right_panel = tk.Frame(paned_window, bg=self.colors['card_bg'])
        paned_window.add(self.right_panel, weight=1)
        
        # Setup panels
        self.setup_left_panel()
        self.setup_right_panel()
        
    def create_header(self):
        """Create the header section."""
        header_frame = tk.Frame(self.root, bg=self.colors['accent'], height=70)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Header content
        header_content = tk.Frame(header_frame, bg=self.colors['accent'])
        header_content.place(relx=0.02, rely=0.5, anchor='w')
        
        # Icon and title
        tk.Label(
            header_content,
            text="🔧",
            font=('Segoe UI', 24),
            bg=self.colors['accent'],
            fg=self.colors['text_light']
        ).pack(side=tk.LEFT, padx=(0, 15))
        
        title_frame = tk.Frame(header_content, bg=self.colors['accent'])
        title_frame.pack(side=tk.LEFT)
        
        tk.Label(
            title_frame,
            text="Remote Control Technician",
            font=('Segoe UI', 18, 'bold'),
            bg=self.colors['accent'],
            fg=self.colors['text_light']
        ).pack(anchor='w')
        
        tk.Label(
            title_frame,
            text="Provide remote assistance and support",
            font=('Segoe UI', 11),
            bg=self.colors['accent'],
            fg='#ffccd5'
        ).pack(anchor='w')
        
    def setup_left_panel(self):
        """Set up the left panel with connection and requests."""
        # Left panel header
        left_header = tk.Frame(self.left_panel, bg=self.colors['secondary'], height=50)
        left_header.pack(fill=tk.X)
        left_header.pack_propagate(False)
        
        tk.Label(
            left_header,
            text="🎛️ Control Panel",
            font=('Segoe UI', 14, 'bold'),
            bg=self.colors['secondary'],
            fg=self.colors['text_light']
        ).place(relx=0.05, rely=0.5, anchor='w')
        
        # Scrollable content
        content_frame = tk.Frame(self.left_panel, bg=self.colors['card_bg'])
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Connection section
        self.create_connection_card(content_frame)
        
        # Status section
        self.create_status_card(content_frame)
        
        # Help requests section
        self.create_requests_card(content_frame)
        
    def create_connection_card(self, parent):
        """Create the connection card."""
        card = self.create_card(parent, "🔗 Server Connection", padding=15)
        
        # Server IP input
        tk.Label(
            card,
            text="🌐 Server IP:",
            font=('Segoe UI', 10, 'bold'),
            bg=self.colors['card_bg'],
            fg=self.colors['text_light']
        ).pack(anchor='w', pady=(0, 5))
        
        ip_frame = tk.Frame(card, bg=self.colors['accent'], height=30)
        ip_frame.pack(fill=tk.X, pady=(0, 10))
        ip_frame.pack_propagate(False)
        
        self.mediator_ip_entry = tk.Entry(
            ip_frame,
            font=('Segoe UI', 10),
            bg=self.colors['input_bg'],
            fg=self.colors['text_light'],
            relief='flat',
            borderwidth=0,
            insertbackground=self.colors['text_light']
        )
        self.mediator_ip_entry.place(x=2, y=2, relwidth=1, relheight=1, width=-4, height=-4)
        self.mediator_ip_entry.insert(0, "127.0.0.1")
        
        # Technician name input
        tk.Label(
            card,
            text="👤 Your Name:",
            font=('Segoe UI', 10, 'bold'),
            bg=self.colors['card_bg'],
            fg=self.colors['text_light']
        ).pack(anchor='w', pady=(0, 5))
        
        name_frame = tk.Frame(card, bg=self.colors['accent'], height=30)
        name_frame.pack(fill=tk.X, pady=(0, 15))
        name_frame.pack_propagate(False)
        
        self.technician_name_entry = tk.Entry(
            name_frame,
            font=('Segoe UI', 10),
            bg=self.colors['input_bg'],
            fg=self.colors['text_light'],
            relief='flat',
            borderwidth=0,
            insertbackground=self.colors['text_light']
        )
        self.technician_name_entry.place(x=2, y=2, relwidth=1, relheight=1, width=-4, height=-4)
        
        # Set default name
        if self.username:
            default_name = f"{self.username}-{self.get_local_ip()}"
        else:
            default_name = f"Tech-{self.get_local_ip()}"
        self.technician_name_entry.insert(0, default_name)
        
        # Connection buttons
        self.connect_mediator_button = self.create_compact_button(
            card, "🚀 Connect", self.connect_to_mediator, self.colors['success']
        )
        
        self.disconnect_mediator_button = self.create_compact_button(
            card, "🔌 Disconnect", self.disconnect_from_mediator, 
            self.colors['error'], state=tk.DISABLED
        )
        
    def create_status_card(self, parent):
        """Create the status card."""
        card = self.create_card(parent, "📊 Status", padding=15)
        
        # Status items
        status_items = [
            ("🔗 Server:", "mediator_status_label", "Disconnected", self.colors['error']),
            ("⚡ Control:", "control_status_label", "Disconnected", self.colors['error']),
            ("👥 Client:", "current_client_label", "None", self.colors['text_secondary'])
        ]
        
        for label_text, attr_name, initial_value, color in status_items:
            item_frame = tk.Frame(card, bg=self.colors['input_bg'])
            item_frame.pack(fill=tk.X, pady=2)
            
            tk.Label(
                item_frame,
                text=label_text,
                font=('Segoe UI', 9, 'bold'),
                bg=self.colors['input_bg'],
                fg=self.colors['text_light']
            ).pack(side=tk.LEFT, padx=10, pady=5)
            
            value_label = tk.Label(
                item_frame,
                text=initial_value,
                font=('Segoe UI', 9),
                bg=self.colors['input_bg'],
                fg=color
            )
            value_label.pack(side=tk.RIGHT, padx=10, pady=5)
            setattr(self, attr_name, value_label)
            
    def create_requests_card(self, parent):
        """Create the help requests card."""
        card = self.create_card(parent, "🆘 Help Requests", padding=10)
        
        # Requests tree
        tree_frame = tk.Frame(card, bg=self.colors['border'], height=200)
        tree_frame.pack(fill=tk.X, pady=(0, 10))
        tree_frame.pack_propagate(False)
        
        columns = ("Name", "IP")
        self.requests_tree = ttk.Treeview(
            tree_frame, 
            columns=columns, 
            show="tree headings", 
            height=8
        )
        self.requests_tree.heading("#0", text="ID")
        self.requests_tree.heading("Name", text="Name")
        self.requests_tree.heading("IP", text="IP Address")
        
        # Configure column widths
        self.requests_tree.column("#0", width=50)
        self.requests_tree.column("Name", width=120)
        self.requests_tree.column("IP", width=100)
        
        self.requests_tree.place(x=2, y=2, relwidth=1, relheight=1, width=-4, height=-4)
        
        # Control button
        self.request_control_button = self.create_compact_button(
            card, "🎮 Request Control", self.request_control, 
            self.colors['info'], state=tk.DISABLED
        )
        

        
    def setup_right_panel(self):
        """Set up the right panel for remote control."""
        # Right panel header
        right_header = tk.Frame(self.right_panel, bg=self.colors['secondary'], height=50)
        right_header.pack(fill=tk.X)
        right_header.pack_propagate(False)
        
        # Header left side
        header_left = tk.Frame(right_header, bg=self.colors['secondary'])
        header_left.pack(side=tk.LEFT, fill=tk.Y, padx=20)
        
        tk.Label(
            header_left,
            text="🖥️ Remote Screen",
            font=('Segoe UI', 14, 'bold'),
            bg=self.colors['secondary'],
            fg=self.colors['text_light']
        ).pack(side=tk.LEFT, pady=15)
        
        # Header right side - control info
        header_right = tk.Frame(right_header, bg=self.colors['secondary'])
        header_right.pack(side=tk.RIGHT, fill=tk.Y, padx=20)
        
        info_grid = tk.Frame(header_right, bg=self.colors['secondary'])
        info_grid.pack(pady=10)
        
        # Session status
        tk.Label(
            info_grid,
            text="Session:",
            font=('Segoe UI', 10, 'bold'),
            bg=self.colors['secondary'],
            fg=self.colors['text_light']
        ).grid(row=0, column=0, sticky='w', padx=(0, 10))
        
        self.session_status_label = tk.Label(
            info_grid,
            text="No Session",
            font=('Segoe UI', 10),
            bg=self.colors['secondary'],
            fg=self.colors['error']
        )
        self.session_status_label.grid(row=0, column=1, sticky='w')
        
        # Mouse position
        tk.Label(
            info_grid,
            text="Mouse:",
            font=('Segoe UI', 10, 'bold'),
            bg=self.colors['secondary'],
            fg=self.colors['text_light']
        ).grid(row=0, column=2, sticky='w', padx=(20, 10))
        
        self.mouse_pos_label = tk.Label(
            info_grid,
            text="(0, 0)",
            font=('Segoe UI', 10),
            bg=self.colors['secondary'],
            fg=self.colors['text_secondary']
        )
        self.mouse_pos_label.grid(row=0, column=3, sticky='w')
        

        
        # Main screen area
        screen_frame = tk.Frame(self.right_panel, bg=self.colors['card_bg'])
        screen_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Canvas for remote screen
        canvas_frame = tk.Frame(screen_frame, bg=self.colors['border'])
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.canvas = tk.Canvas(
            canvas_frame,
            bg='#000000',
            highlightthickness=0,
            takefocus=True
        )
        self.canvas.place(x=2, y=2, relwidth=1, relheight=1, width=-4, height=-4)
        
        # Bind canvas events
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Motion>", self.on_canvas_motion)
        self.canvas.bind("<Button-3>", self.on_canvas_right_click)
        self.canvas.bind("<FocusIn>", self.on_canvas_focus_in)
        self.canvas.bind("<FocusOut>", self.on_canvas_focus_out)
        self.canvas.bind("<KeyPress>", self.on_key_press)
        self.canvas.bind("<KeyRelease>", self.on_key_release)
        self.canvas.configure(highlightthickness=2)
        
        # Bottom control panel
        self.create_bottom_controls(screen_frame)
        
    def create_bottom_controls(self, parent):
        """Create the bottom control panel."""
        controls_frame = tk.Frame(parent, bg=self.colors['secondary'], height=70)
        controls_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        controls_frame.pack_propagate(False)
        
        # Session controls
        controls_container = tk.Frame(controls_frame, bg=self.colors['secondary'])
        controls_container.pack(expand=True, fill=tk.BOTH, padx=15, pady=10)
        
        self.end_session_button = self.create_control_button(
            controls_container, "🔚 End Session", self.end_session,
            self.colors['error'], state=tk.DISABLED
        )
        
    def create_card(self, parent, title, padding=10, expand=False):
        """Create a styled card widget."""
        # Card container
        card_container = tk.Frame(parent, bg=self.colors['card_bg'])
        if expand:
            card_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        else:
            card_container.pack(fill=tk.X, padx=5, pady=5)
        
        # Card header
        header = tk.Frame(card_container, bg=self.colors['input_bg'], height=30)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text=title,
            font=('Segoe UI', 11, 'bold'),
            bg=self.colors['input_bg'],
            fg=self.colors['text_light']
        ).place(relx=0.05, rely=0.5, anchor='w')
        
        # Card content
        content = tk.Frame(card_container, bg=self.colors['card_bg'])
        content.pack(fill=tk.BOTH, expand=True, padx=padding, pady=padding)
        
        return content
        
    def create_compact_button(self, parent, text, command, color, state=tk.NORMAL):
        """Create a compact button."""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=('Segoe UI', 9, 'bold'),
            bg=color,
            fg=self.colors['text_light'],
            relief='flat',
            borderwidth=0,
            pady=6,
            cursor='hand2',
            state=state
        )
        btn.pack(fill=tk.X, pady=2)
        
        # Hover effects
        def on_enter(e):
            if btn['state'] != 'disabled':
                if color == self.colors['success']:
                    btn.configure(bg='#00f0cc')
                elif color == self.colors['error']:
                    btn.configure(bg='#ff6b6b')
                elif color == self.colors['info']:
                    btn.configure(bg='#42a5f5')
                    
        def on_leave(e):
            if btn['state'] != 'disabled':
                btn.configure(bg=color)
                
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn
        
    def create_control_button(self, parent, text, command, color, state=tk.NORMAL):
        """Create a control button."""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=('Segoe UI', 10, 'bold'),
            bg=color,
            fg=self.colors['text_light'],
            relief='flat',
            borderwidth=0,
            padx=15,
            pady=8,
            cursor='hand2',
            state=state
        )
        btn.pack(side=tk.LEFT, padx=5)
        
        return btn
        
    def get_local_ip(self):
        """Get the local IP address."""
        try:
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
        technician_name = self.technician_name_entry.get().strip()
        
        if not mediator_ip:
            messagebox.showerror("Error", "Please enter mediator IP address")
            return
            
        if not technician_name:
            messagebox.showerror("Error", "Please enter your name")
            return
            
        self.log(f"Connecting to mediator server at {mediator_ip}:{MEDIATOR_PORT}...")
        
        try:
            # Create secure connection to mediator
            self.mediator_socket = ssl_utils.create_secure_client_socket()
            self.mediator_socket = ssl_utils.connect_secure_client(self.mediator_socket, mediator_ip, MEDIATOR_PORT)
            
            # Send identification message
            connect_message = {
                'type': 'technician_connect',
                'name': technician_name,
                'ip': self.get_local_ip()
            }
            
            self.mediator_socket.send(json.dumps(connect_message).encode('utf-8'))
            
            # Wait for welcome message
            response = self.mediator_socket.recv(BUFFER_SIZE)
            welcome_msg = json.loads(response.decode('utf-8'))
            
            if welcome_msg['type'] == 'welcome':
                self.technician_id = welcome_msg['technician_id']
                self.mediator_connected = True
                
                # Update help requests
                help_requests = welcome_msg.get('help_requests', [])
                self.update_help_requests(help_requests)
                
                # Update UI
                self.mediator_status_label.config(text="Connected", fg="green")
                self.connect_mediator_button.config(state=tk.DISABLED)
                self.disconnect_mediator_button.config(state=tk.NORMAL)
                self.request_control_button.config(state=tk.NORMAL)
                
                self.log(f"Connected to mediator server (Technician ID: {self.technician_id})")
                
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
        self.request_control_button.config(state=tk.DISABLED)
        
        self.technician_id = None
        self.help_requests.clear()
        self.update_help_requests([])
        
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
        
        if msg_type == 'new_help_request':
            self.add_help_request(message)
            
        elif msg_type == 'help_cancelled':
            self.remove_help_request(message.get('client_id'))
            
        elif msg_type == 'client_disconnected':
            self.remove_help_request(message.get('client_id'))
            
        elif msg_type == 'client_unavailable':
            self.remove_help_request(message.get('client_id'))
            
        elif msg_type == 'control_approved':
            self.handle_control_approved(message)
            
        elif msg_type == 'control_denied':
            self.handle_control_denied(message)
            
        elif msg_type == 'heartbeat':
            # Respond to heartbeat
            response = {'type': 'heartbeat_response'}
            try:
                self.mediator_socket.send(json.dumps(response).encode('utf-8'))
            except:
                pass
                
        else:
            self.log(f"Unknown message type from mediator: {msg_type}")
            
    def add_help_request(self, request):
        """Add a new help request to the list."""
        client_id = request['client_id']
        self.help_requests[client_id] = {
            'name': request['name'],
            'ip': request['ip'],
            'timestamp': request['timestamp']
        }
        
        self.root.after(0, self.refresh_help_requests_ui)
        self.log(f"New help request from {request['name']} ({request['ip']})")
        
    def remove_help_request(self, client_id):
        """Remove a help request from the list."""
        if client_id in self.help_requests:
            client_info = self.help_requests[client_id]
            del self.help_requests[client_id]
            self.root.after(0, self.refresh_help_requests_ui)
            self.log(f"Help request removed: {client_info['name']}")
            
    def update_help_requests(self, requests_list):
        """Update the help requests list."""
        self.help_requests.clear()
        for request in requests_list:
            client_id = request['client_id']
            self.help_requests[client_id] = {
                'name': request['name'],
                'ip': request['ip'],
                'timestamp': request['timestamp']
            }
        
        self.root.after(0, self.refresh_help_requests_ui)
        
    def refresh_help_requests_ui(self):
        """Refresh the help requests UI."""
        # Clear existing items
        for item in self.requests_tree.get_children():
            self.requests_tree.delete(item)
            
        # Add current help requests
        for client_id, request in self.help_requests.items():
            self.requests_tree.insert("", "end", iid=client_id, text=client_id,
                                    values=(request['name'], request['ip']))
                                    
    def request_control(self):
        """Request control of the selected client."""
        selected = self.requests_tree.selection()
        if not selected or not self.mediator_connected:
            messagebox.showwarning("Warning", "Please select a client from the help requests list")
            return
            
        client_id = selected[0]
        client_info = self.help_requests.get(client_id)
        
        if not client_info:
            messagebox.showerror("Error", "Selected client is no longer available")
            return
            
        try:
            control_request = {
                'type': 'request_control',
                'client_id': client_id
            }
            
            self.mediator_socket.send(json.dumps(control_request).encode('utf-8'))
            self.log(f"Requesting control of client: {client_info['name']} ({client_info['ip']})")
            
        except Exception as e:
            self.log(f"Error requesting control: {str(e)}")
            messagebox.showerror("Error", f"Failed to request control:\n{str(e)}")
            
    def handle_control_approved(self, message):
        """Handle control approval from client."""
        client_ip = message['client_ip']
        client_name = message['client_name']
        session_id = message['session_id']
        
        self.current_client_ip = client_ip
        self.current_session_id = session_id
        
        self.log(f"Control approved by {client_name} - connecting to {client_ip}...")
        
        # Connect to client directly
        threading.Thread(target=self.connect_to_client, args=(client_ip,), daemon=True).start()
        
    def handle_control_denied(self, message):
        """Handle control denial from client."""
        client_name = message['client_name']
        self.log(f"Control request denied by {client_name}")
        messagebox.showinfo("Control Denied", f"Client '{client_name}' denied your control request.")
        
    def connect_to_client(self, client_ip):
        """Connect directly to the client for control."""
        try:
            # Create secure connection to client
            self.control_socket = ssl_utils.create_secure_client_socket()
            self.control_socket = ssl_utils.connect_secure_client(self.control_socket, client_ip, REMOTE_CONTROL_PORT)
            self.control_socket.settimeout(SOCKET_TIMEOUT)
            
            self.control_connected = True
            self.control_running = True
            
            self.log(f"🔐 Securely connected to client at {client_ip}:{REMOTE_CONTROL_PORT} with SSL encryption")
            
            # Update UI
            self.root.after(0, self._update_ui_connected)
            
            # Start receiving screenshots
            threading.Thread(target=self._receive_screenshots, daemon=True).start()
            
            # Start ping thread
            threading.Thread(target=self._ping_thread, daemon=True).start()
            
        except Exception as e:
            self.log(f"❌ Failed to establish secure connection to client {client_ip}: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror("Connection Error", 
                f"Failed to establish secure connection to client:\n{str(e)}"))
            
    def _update_ui_connected(self):
        """Update UI when connected to client."""
        self.control_status_label.config(text="Connected", fg="green")
        self.session_status_label.config(text="Active Session", fg="green")
        self.current_client_label.config(text=self.current_client_ip, fg="green")
        self.enable_keyboard_button.config(state=tk.NORMAL)
        self.end_session_button.config(state=tk.NORMAL)
        self.keyboard_focus = True
        self.keyboard_label.config(text="Enabled", fg="green")
        self.canvas.focus_set()
        
        self.log("Connected to client successfully!")
        
    def _update_ui_disconnected(self):
        """Update UI when disconnected from client."""
        self.control_status_label.config(text="Disconnected", fg="red")
        self.session_status_label.config(text="No Session", fg="red")
        self.current_client_label.config(text="None", fg="gray")
        self.enable_keyboard_button.config(state=tk.DISABLED)
        self.end_session_button.config(state=tk.DISABLED)
        self.keyboard_focus = False
        self.keyboard_label.config(text="Disabled", fg="red")
        self.mouse_pos_label.config(text="(0, 0)")
        self.canvas.delete("all")
        
    def _ping_thread(self):
        """Send ping messages to keep connection alive."""
        consecutive_failures = 0
        max_failures = 3
        
        while self.control_running and self.control_connected:
            try:
                success = self.send_command({'type': 'ping'})
                if success:
                    consecutive_failures = 0
                else:
                    consecutive_failures += 1
                    self.log(f"Ping failed ({consecutive_failures}/{max_failures})")
                    if consecutive_failures >= max_failures:
                        self.log("Too many ping failures - disconnecting")
                        break
                    
                time.sleep(3)
                
            except Exception as e:
                self.log(f"Ping error: {str(e)}")
                break
                
        if self.control_connected:
            self.disconnect_from_client()
            
    def _receive_screenshots(self):
        """Receive and display screenshots from the client."""
        try:
            while self.control_running and self.control_connected:
                try:
                    # Receive size first (4 bytes)
                    size_bytes = self._recv_all(4)
                    if not size_bytes:
                        break
                        
                    size = int.from_bytes(size_bytes, byteorder='big')
                    
                    # Receive data
                    data = self._recv_all(size)
                    if not data:
                        break
                        
                    # Process data
                    data_packet = pickle.loads(data)
                    
                    # Extract image and cursor position
                    img_b64 = data_packet['image']
                    self.cursor_x = data_packet['cursor_x']
                    self.cursor_y = data_packet['cursor_y']
                    
                    # Update mouse position
                    self.root.after(0, lambda: self.mouse_pos_label.config(
                        text=f"({self.cursor_x}, {self.cursor_y})"))
                    
                    # Convert and display image
                    img_bytes = base64.b64decode(img_b64)
                    image = Image.open(io.BytesIO(img_bytes))
                    
                    # Calculate scaling
                    canvas_width = self.canvas.winfo_width()
                    canvas_height = self.canvas.winfo_height()
                    
                    if canvas_width > 1 and canvas_height > 1:
                        img_width, img_height = image.size
                        self.scale_factor_x = canvas_width / img_width
                        self.scale_factor_y = canvas_height / img_height
                        scale = min(self.scale_factor_x, self.scale_factor_y)
                        
                        if scale < 1:
                            new_width = int(img_width * scale)
                            new_height = int(img_height * scale)
                            image = image.resize((new_width, new_height), Image.LANCZOS)
                            self.scale_factor_x = scale
                            self.scale_factor_y = scale
                    
                    # Draw cursor
                    draw = ImageDraw.Draw(image)
                    cursor_x_scaled = int(self.cursor_x * self.scale_factor_x)
                    cursor_y_scaled = int(self.cursor_y * self.scale_factor_y)
                    
                    cursor_size = 10
                    draw.line((cursor_x_scaled - cursor_size, cursor_y_scaled, 
                              cursor_x_scaled + cursor_size, cursor_y_scaled), 
                              fill="red", width=2)
                    draw.line((cursor_x_scaled, cursor_y_scaled - cursor_size, 
                              cursor_x_scaled, cursor_y_scaled + cursor_size), 
                              fill="red", width=2)
                    
                    # Display image
                    photo = ImageTk.PhotoImage(image)
                    self.canvas.delete("all")
                    self.canvas.create_image(0, 0, image=photo, anchor=tk.NW)
                    self.canvas.image = photo
                    
                except ConnectionError:
                    break
                except Exception as e:
                    self.log(f"Error receiving screenshot: {str(e)}")
                    break
                    
        except Exception as e:
            self.log(f"Error in screenshot thread: {str(e)}")
        finally:
            self.disconnect_from_client()
            
    def _recv_all(self, n):
        """Receive exactly n bytes."""
        data = bytearray()
        while len(data) < n:
            try:
                packet = self.control_socket.recv(n - len(data))
                if not packet:
                    return None
                data.extend(packet)
            except socket.timeout:
                return None
            except ConnectionError:
                return None
        return data
        
    def send_command(self, command):
        """Send a command to the connected client with improved error handling."""
        if not self.control_connected or not self.control_socket:
            return False
            
        try:
            command_data = pickle.dumps(command)
            
            # Set a shorter timeout for sending commands
            original_timeout = self.control_socket.gettimeout()
            self.control_socket.settimeout(10.0)
            
            self.control_socket.sendall(command_data)
            
            # Restore original timeout
            self.control_socket.settimeout(original_timeout)
            
            return True
            
        except socket.timeout:
            self.log("Command send timeout")
            return False
        except ConnectionError as e:
            if self.control_connected:
                self.log(f"Connection lost while sending command")
                threading.Timer(2.0, self.disconnect_from_client).start()
            return False
        except Exception as e:
            if self.control_connected:
                self.log(f"Error sending command: {str(e)}")
                threading.Timer(2.0, self.disconnect_from_client).start()
            return False
            
    def disconnect_from_client(self):
        """Disconnect from the current client."""
        self.control_running = False
        self.control_connected = False
        
        if self.control_socket:
            try:
                self.control_socket.close()
            except:
                pass
            self.control_socket = None
            
        # Notify mediator about session end
        if self.mediator_connected and self.current_session_id:
            try:
                end_session_msg = {
                    'type': 'end_session',
                    'session_id': self.current_session_id
                }
                self.mediator_socket.send(json.dumps(end_session_msg).encode('utf-8'))
            except:
                pass
                
        self.current_client_ip = None
        self.current_session_id = None
        
        self.root.after(0, self._update_ui_disconnected)
        self.log("Disconnected from client")
        
    def end_session(self):
        """End the current control session."""
        if messagebox.askyesno("End Session", "Are you sure you want to end the current control session?"):
            self.disconnect_from_client()
            

            
    def on_canvas_click(self, event):
        """Handle left mouse clicks."""
        if not self.control_connected:
            return
            
        remote_x = int(event.x / self.scale_factor_x)
        remote_y = int(event.y / self.scale_factor_y)
        
        self.send_command({
            'type': 'mouse_click',
            'x': remote_x,
            'y': remote_y,
            'button': 'left'
        })
        
    def on_canvas_right_click(self, event):
        """Handle right mouse clicks."""
        if not self.control_connected:
            return
            
        remote_x = int(event.x / self.scale_factor_x)
        remote_y = int(event.y / self.scale_factor_y)
        
        self.send_command({
            'type': 'mouse_click',
            'x': remote_x,
            'y': remote_y,
            'button': 'right'
        })
        
    def on_canvas_motion(self, event):
        """Handle mouse movement with throttling."""
        if not self.control_connected:
            return
        
        # ADD THROTTLING - only send mouse move every 50ms
        current_time = time.time()
        if not hasattr(self, '_last_mouse_move_time'):
            self._last_mouse_move_time = 0
        
        if current_time - self._last_mouse_move_time < 0.05:  # 50ms throttle
            return
        
        self._last_mouse_move_time = current_time
        
        remote_x = int(event.x / self.scale_factor_x)
        remote_y = int(event.y / self.scale_factor_y)
        
        self.send_command({
            'type': 'mouse_move',
            'x': remote_x,
            'y': remote_y
        })
        

            
    def on_key_press(self, event):
        """Handle key press events."""
        if not self.keyboard_focus or not self.control_connected:
            return
            
        # Handle special keys
        key_map = {
            'Return': 'enter',
            'Tab': 'tab',
            'BackSpace': 'backspace',
            'Delete': 'delete',
            'Escape': 'escape',
            'space': 'space',
            'Up': 'up',
            'Down': 'down',
            'Left': 'left',
            'Right': 'right',
            'Home': 'home',
            'End': 'end',
            'Page_Up': 'pageup',
            'Page_Down': 'pagedown',
            'F1': 'f1', 'F2': 'f2', 'F3': 'f3', 'F4': 'f4',
            'F5': 'f5', 'F6': 'f6', 'F7': 'f7', 'F8': 'f8',
            'F9': 'f9', 'F10': 'f10', 'F11': 'f11', 'F12': 'f12'
        }
        
        # Get the key to send
        if event.keysym in key_map:
            key_to_send = key_map[event.keysym]
        elif event.char and event.char.isprintable():
            key_to_send = event.char
        elif event.keysym.lower() in ['control_l', 'control_r']:
            key_to_send = 'ctrl'
        elif event.keysym.lower() in ['alt_l', 'alt_r']:
            key_to_send = 'alt'
        elif event.keysym.lower() in ['shift_l', 'shift_r']:
            key_to_send = 'shift'
        elif event.keysym.lower() in ['super_l', 'super_r', 'win_l', 'win_r']:
            key_to_send = 'win'
        else:
            key_to_send = event.keysym.lower()
        
        if key_to_send:
            success = self.send_command({
                'type': 'key_press',
                'key': key_to_send
            })

    def on_key_release(self, event):
        """Handle key release events."""
        pass
        
    def on_canvas_focus_in(self, event):
        """Handle canvas focus in."""
        if self.control_connected:
            self.keyboard_focus = True
            self.canvas.focus_set()

    def on_canvas_focus_out(self, event):
        """Handle canvas focus out."""
        pass
        
    def on_close(self):
        """Handle window close."""
        self.disconnect_from_client()
        self.disconnect_from_mediator()
        self.root.destroy()
        
    def run(self):
        """Run the technician application."""
        self.root.mainloop()

def main():
    """Main function to run the technician application."""
    # Get username from command line argument if provided
    username = None
    if len(sys.argv) > 1:
        username = sys.argv[1]
    
    try:
        app = RemoteControlTechnicianWithMediator(username)
        app.run()
    except Exception as e:
        print(f"Error starting technician: {str(e)}")
        logging.error(f"Error starting technician: {str(e)}")

if __name__ == "__main__":
    main() 