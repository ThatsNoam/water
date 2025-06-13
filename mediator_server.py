#!/usr/bin/env python3
"""
Mediator Server - Remote Control System
This server manages communication between clients and technicians.
It handles help requests, control requests, and session management.
"""

import socket
import threading
import time
import json
import logging
import sys
import uuid
from datetime import datetime
import tkinter as tk
from tkinter import scrolledtext, ttk
import ssl_utils

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("mediator_log.txt"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("MediatorServer")

# Configuration
MEDIATOR_PORT = 5556
BUFFER_SIZE = 8192
HEARTBEAT_INTERVAL = 30

class MediatorServer:
    def __init__(self):
        self.running = False
        self.server_socket = None
        
        # Connected entities
        self.clients = {}  # client_id: {socket, ip, name, help_requested, session_id}
        self.technicians = {}  # tech_id: {socket, ip, name, assigned_client}
        
        # Help requests and active sessions
        self.help_requests = {}  # client_id: {timestamp, status}
        self.active_sessions = {}  # session_id: {client_id, tech_id, start_time}
        
        self.setup_gui()
        
    def setup_gui(self):
        """Set up the modern mediator server GUI."""
        self.root = tk.Tk()
        self.root.title("🛡️ Mediator Server - Fix It System")
        self.root.geometry("1200x800")
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
        
        # Create header
        self.create_header()
        
        # Create main content
        self.create_main_content()
        
        # Update GUI periodically
        self.update_gui()
        
    def create_header(self):
        """Create the modern header section."""
        header_frame = tk.Frame(self.root, bg=self.colors['accent'], height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Header content
        header_content = tk.Frame(header_frame, bg=self.colors['accent'])
        header_content.place(relx=0.02, rely=0.5, anchor='w')
        
        # Icon and title
        tk.Label(
            header_content,
            text="🛡️",
            font=('Segoe UI', 28),
            bg=self.colors['accent'],
            fg=self.colors['text_light']
        ).pack(side=tk.LEFT, padx=(0, 15))
        
        title_frame = tk.Frame(header_content, bg=self.colors['accent'])
        title_frame.pack(side=tk.LEFT)
        
        tk.Label(
            title_frame,
            text="Mediator Server",
            font=('Segoe UI', 22, 'bold'),
            bg=self.colors['accent'],
            fg=self.colors['text_light']
        ).pack(anchor='w')
        
        tk.Label(
            title_frame,
            text="Central Command & Control System",
            font=('Segoe UI', 12),
            bg=self.colors['accent'],
            fg='#ffccd5'
        ).pack(anchor='w')
        
        # Status and controls in header
        controls_frame = tk.Frame(header_frame, bg=self.colors['accent'])
        controls_frame.place(relx=0.98, rely=0.5, anchor='e', x=-20)
        
        # Status indicator
        status_frame = tk.Frame(controls_frame, bg=self.colors['accent'])
        status_frame.pack(side=tk.TOP)
        
        tk.Label(
            status_frame,
            text="Status:",
            font=('Segoe UI', 11, 'bold'),
            bg=self.colors['accent'],
            fg=self.colors['text_light']
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.status_label = tk.Label(
            status_frame,
            text="⭕ Stopped",
            font=('Segoe UI', 11, 'bold'),
            bg=self.colors['accent'],
            fg='#ffccd5'
        )
        self.status_label.pack(side=tk.LEFT)
        
        # Control buttons
        buttons_frame = tk.Frame(controls_frame, bg=self.colors['accent'])
        buttons_frame.pack(side=tk.BOTTOM, pady=(10, 0))
        
        self.start_button = self.create_header_button(
            buttons_frame, "🚀 Start Server", self.start_server, 
            self.colors['success']
        )
        
        self.stop_button = self.create_header_button(
            buttons_frame, "⏹️ Stop Server", self.stop_server, 
            self.colors['error'], state=tk.DISABLED
        )
        
    def create_header_button(self, parent, text, command, color, state=tk.NORMAL):
        """Create a modern header button."""
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
        
        # Hover effects
        def on_enter(e):
            if btn['state'] != 'disabled':
                if color == self.colors['success']:
                    btn.configure(bg='#00f0cc')
                elif color == self.colors['error']:
                    btn.configure(bg='#ff6b6b')
                    
        def on_leave(e):
            if btn['state'] != 'disabled':
                btn.configure(bg=color)
                
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn
        
    def create_main_content(self):
        """Create the main content area."""
        main_frame = tk.Frame(self.root, bg=self.colors['primary'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Statistics dashboard
        self.create_stats_dashboard(main_frame)
        
        # Main content with modern tabs
        self.create_modern_tabs(main_frame)
        
    def create_stats_dashboard(self, parent):
        """Create the statistics dashboard."""
        stats_frame = tk.Frame(parent, bg=self.colors['card_bg'], height=100)
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        stats_frame.pack_propagate(False)
        
        # Dashboard header
        header = tk.Frame(stats_frame, bg=self.colors['secondary'], height=35)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="📊 Live Statistics",
            font=('Segoe UI', 14, 'bold'),
            bg=self.colors['secondary'],
            fg=self.colors['text_light']
        ).place(relx=0.02, rely=0.5, anchor='w')
        
        # Stats grid
        stats_content = tk.Frame(stats_frame, bg=self.colors['card_bg'])
        stats_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Create stat cards
        self.create_stat_card(stats_content, "👥 Clients", "clients_count_label", self.colors['info'], 0)
        self.create_stat_card(stats_content, "🔧 Technicians", "techs_count_label", self.colors['success'], 1)
        self.create_stat_card(stats_content, "🆘 Help Requests", "requests_count_label", self.colors['warning'], 2)
        self.create_stat_card(stats_content, "⚡ Active Sessions", "sessions_count_label", self.colors['accent'], 3)
        
    def create_stat_card(self, parent, title, label_attr, color, column):
        """Create a modern stat card."""
        card = tk.Frame(parent, bg=color, width=200, height=60)
        card.grid(row=0, column=column, padx=10, sticky='ew')
        card.grid_propagate(False)
        parent.grid_columnconfigure(column, weight=1)
        
        # Card content
        content = tk.Frame(card, bg=color)
        content.place(relx=0.5, rely=0.5, anchor='center')
        
        tk.Label(
            content,
            text=title,
            font=('Segoe UI', 11, 'bold'),
            bg=color,
            fg=self.colors['text_light']
        ).pack()
        
        label = tk.Label(
            content,
            text="0",
            font=('Segoe UI', 18, 'bold'),
            bg=color,
            fg=self.colors['text_light']
        )
        label.pack()
        setattr(self, label_attr, label)
        
    def create_modern_tabs(self, parent):
        """Create modern tabbed interface."""
        # Configure ttk style for dark theme
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure notebook style
        style.configure(
            "TNotebook",
            background=self.colors['card_bg'],
            borderwidth=0
        )
        
        style.configure(
            "TNotebook.Tab",
            background=self.colors['input_bg'],
            foreground=self.colors['text_light'],
            padding=[20, 10],
            font=('Segoe UI', 11, 'bold')
        )
        
        style.map(
            "TNotebook.Tab",
            background=[('selected', self.colors['accent'])],
            foreground=[('selected', self.colors['text_light'])]
        )
        
        # Create notebook
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs with modern styling
        self.create_clients_tab()
        self.create_technicians_tab()
        self.create_sessions_tab()
        self.create_log_tab()
        
    def create_clients_tab(self):
        """Create the clients tab."""
        frame = tk.Frame(self.notebook, bg=self.colors['card_bg'])
        self.notebook.add(frame, text="👥 Connected Clients")
        
        # Create modern treeview
        self.clients_tree = self.create_modern_treeview(
            frame, 
            ("IP", "Name", "Status", "Connected"),
            ["Client ID", "IP Address", "Name", "Status", "Connected Time"]
        )
        
    def create_technicians_tab(self):
        """Create the technicians tab."""
        frame = tk.Frame(self.notebook, bg=self.colors['card_bg'])
        self.notebook.add(frame, text="🔧 Connected Technicians")
        
        self.techs_tree = self.create_modern_treeview(
            frame,
            ("IP", "Name", "Status", "Connected"),
            ["Technician ID", "IP Address", "Name", "Status", "Connected Time"]
        )
        
    def create_sessions_tab(self):
        """Create the sessions tab."""
        frame = tk.Frame(self.notebook, bg=self.colors['card_bg'])
        self.notebook.add(frame, text="⚡ Active Sessions")
        
        self.sessions_tree = self.create_modern_treeview(
            frame,
            ("Client", "Technician", "Started", "Duration"),
            ["Session ID", "Client", "Technician", "Started", "Duration"]
        )
        
    def create_log_tab(self):
        """Create the log tab."""
        frame = tk.Frame(self.notebook, bg=self.colors['card_bg'])
        self.notebook.add(frame, text="📝 Server Log")
        
        # Log container
        log_container = tk.Frame(frame, bg=self.colors['border'])
        log_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(
            log_container,
            font=('Consolas', 10),
            bg=self.colors['input_bg'],
            fg=self.colors['text_light'],
            relief='flat',
            borderwidth=0,
            insertbackground=self.colors['text_light']
        )
        self.log_text.place(x=2, y=2, relwidth=1, relheight=1, width=-4, height=-4)
        
    def create_modern_treeview(self, parent, columns, headings):
        """Create a modern styled treeview."""
        # Configure treeview style
        style = ttk.Style()
        
        style.configure(
            "Modern.Treeview",
            background=self.colors['input_bg'],
            foreground=self.colors['text_light'],
            fieldbackground=self.colors['input_bg'],
            borderwidth=0,
            font=('Segoe UI', 10)
        )
        
        style.configure(
            "Modern.Treeview.Heading",
            background=self.colors['secondary'],
            foreground=self.colors['text_light'],
            font=('Segoe UI', 11, 'bold'),
            relief='flat'
        )
        
        # Create container
        container = tk.Frame(parent, bg=self.colors['border'])
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create treeview
        tree = ttk.Treeview(
            container, 
            columns=columns, 
            show="tree headings",
            style="Modern.Treeview"
        )
        
        # Configure headings
        for i, heading in enumerate(headings):
            if i == 0:
                tree.heading("#0", text=heading)
                tree.column("#0", width=120, minwidth=100)
            else:
                col = columns[i-1]
                tree.heading(col, text=heading)
                tree.column(col, width=150, minwidth=100)
        
        # Position treeview
        tree.place(x=2, y=2, relwidth=1, relheight=1, width=-4, height=-4)
        
        return tree
        
    def log(self, message):
        """Add a message to the log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        logger.info(message)
        
        # Update GUI log
        self.root.after(0, lambda: self._update_log_gui(log_message))
        
    def _update_log_gui(self, message):
        """Update the GUI log in the main thread."""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        
    def start_server(self):
        """Start the mediator server with SSL encryption."""
        if self.running:
            return
            
        try:
            # Initialize SSL certificates
            if not ssl_utils.initialize_ssl():
                self.log("❌ Failed to initialize SSL certificates")
                return
                
            # Create secure server socket
            self.server_socket = ssl_utils.create_secure_server_socket("0.0.0.0", MEDIATOR_PORT)
            self.server_socket.listen(50)  # Allow many connections
            
            self.running = True
            self.status_label.config(text="🔐 Running (SSL)", fg='#90ff90')
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            
            self.log(f"🔐 Secure mediator server started on port {MEDIATOR_PORT} with SSL/TLS encryption")
            
            # Start accepting connections
            threading.Thread(target=self.accept_connections, daemon=True).start()
            
            # Start heartbeat checker
            threading.Thread(target=self.heartbeat_checker, daemon=True).start()
            
        except Exception as e:
            self.log(f"❌ Error starting secure server: {str(e)}")
            
    def stop_server(self):
        """Stop the mediator server."""
        self.running = False
        
        # Close all client connections
        for client_id, client_info in list(self.clients.items()):
            try:
                client_info['socket'].close()
            except:
                pass
                
        # Close all technician connections
        for tech_id, tech_info in list(self.technicians.items()):
            try:
                tech_info['socket'].close()
            except:
                pass
                
        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
                
        self.clients.clear()
        self.technicians.clear()
        self.help_requests.clear()
        self.active_sessions.clear()
        
        self.status_label.config(text="⭕ Stopped", fg="#ffccd5")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        self.log("🛑 Mediator server stopped")
        
    def accept_connections(self):
        """Accept incoming connections from clients and technicians."""
        while self.running:
            try:
                client_socket, client_address = self.server_socket.accept()
                self.log(f"New connection from {client_address[0]}:{client_address[1]}")
                
                # Handle connection in separate thread
                threading.Thread(target=self.handle_connection, 
                               args=(client_socket, client_address), daemon=True).start()
                               
            except socket.error:
                if self.running:
                    self.log("Error accepting connection")
                break
                
    def handle_connection(self, client_socket, client_address):
        """Handle a new connection (client or technician)."""
        try:
            client_socket.settimeout(60)  # 1 minute timeout for initial handshake
            
            # Wait for identification message
            data = client_socket.recv(BUFFER_SIZE)
            if not data:
                return
                
            message = json.loads(data.decode('utf-8'))
            
            if message['type'] == 'client_connect':
                self.handle_client_connection(client_socket, client_address, message)
            elif message['type'] == 'technician_connect':
                self.handle_technician_connection(client_socket, client_address, message)
            else:
                self.log(f"Unknown connection type from {client_address[0]}")
                client_socket.close()
                
        except Exception as e:
            self.log(f"Error handling connection from {client_address[0]}: {str(e)}")
            try:
                client_socket.close()
            except:
                pass
                
    def handle_client_connection(self, client_socket, client_address, message):
        """Handle a client connection."""
        client_id = str(uuid.uuid4())[:8]
        client_name = message.get('name', f"Client-{client_address[0]}")
        
        # Store client info
        self.clients[client_id] = {
            'socket': client_socket,
            'ip': client_address[0],
            'name': client_name,
            'help_requested': False,
            'session_id': None,
            'connected_time': datetime.now()
        }
        
        # Send welcome message
        response = {
            'type': 'welcome',
            'client_id': client_id,
            'status': 'connected'
        }
        
        try:
            client_socket.send(json.dumps(response).encode('utf-8'))
            self.log(f"Client '{client_name}' connected with ID: {client_id}")
            
            # Handle client messages
            threading.Thread(target=self.handle_client_messages, 
                           args=(client_id,), daemon=True).start()
                           
        except Exception as e:
            self.log(f"Error welcoming client: {str(e)}")
            self.disconnect_client(client_id)
            
    def handle_technician_connection(self, tech_socket, tech_address, message):
        """Handle a technician connection."""
        tech_id = str(uuid.uuid4())[:8]
        tech_name = message.get('name', f"Tech-{tech_address[0]}")
        
        # Store technician info
        self.technicians[tech_id] = {
            'socket': tech_socket,
            'ip': tech_address[0],
            'name': tech_name,
            'assigned_client': None,
            'connected_time': datetime.now()
        }
        
        # Send welcome message with current help requests
        help_list = []
        for client_id, client_info in self.clients.items():
            if client_info['help_requested'] and not client_info['session_id']:
                help_list.append({
                    'client_id': client_id,
                    'name': client_info['name'],
                    'ip': client_info['ip'],
                    'timestamp': self.help_requests.get(client_id, {}).get('timestamp', '')
                })
                
        response = {
            'type': 'welcome',
            'technician_id': tech_id,
            'status': 'connected',
            'help_requests': help_list
        }
        
        try:
            tech_socket.send(json.dumps(response).encode('utf-8'))
            self.log(f"Technician '{tech_name}' connected with ID: {tech_id}")
            
            # Handle technician messages
            threading.Thread(target=self.handle_technician_messages, 
                           args=(tech_id,), daemon=True).start()
                           
        except Exception as e:
            self.log(f"Error welcoming technician: {str(e)}")
            self.disconnect_technician(tech_id)
            
    def handle_client_messages(self, client_id):
        """Handle messages from a specific client."""
        if client_id not in self.clients:
            return
            
        client_socket = self.clients[client_id]['socket']
        
        try:
            while self.running and client_id in self.clients:
                try:
                    client_socket.settimeout(HEARTBEAT_INTERVAL + 10)
                    data = client_socket.recv(BUFFER_SIZE)
                    
                    if not data:
                        break
                        
                    message = json.loads(data.decode('utf-8'))
                    self.process_client_message(client_id, message)
                    
                except socket.timeout:
                    # Send heartbeat
                    heartbeat = {'type': 'heartbeat'}
                    client_socket.send(json.dumps(heartbeat).encode('utf-8'))
                    
                except ConnectionError:
                    break
                except Exception as e:
                    self.log(f"Error handling client {client_id} message: {str(e)}")
                    break
                    
        except Exception as e:
            self.log(f"Error in client {client_id} message handler: {str(e)}")
        finally:
            self.disconnect_client(client_id)
            
    def handle_technician_messages(self, tech_id):
        """Handle messages from a specific technician."""
        if tech_id not in self.technicians:
            return
            
        tech_socket = self.technicians[tech_id]['socket']
        
        try:
            while self.running and tech_id in self.technicians:
                try:
                    tech_socket.settimeout(HEARTBEAT_INTERVAL + 10)
                    data = tech_socket.recv(BUFFER_SIZE)
                    
                    if not data:
                        break
                        
                    message = json.loads(data.decode('utf-8'))
                    self.process_technician_message(tech_id, message)
                    
                except socket.timeout:
                    # Send heartbeat
                    heartbeat = {'type': 'heartbeat'}
                    tech_socket.send(json.dumps(heartbeat).encode('utf-8'))
                    
                except ConnectionError:
                    break
                except Exception as e:
                    self.log(f"Error handling technician {tech_id} message: {str(e)}")
                    break
                    
        except Exception as e:
            self.log(f"Error in technician {tech_id} message handler: {str(e)}")
        finally:
            self.disconnect_technician(tech_id)
            
    def process_client_message(self, client_id, message):
        """Process a message from a client."""
        msg_type = message.get('type')
        
        if msg_type == 'help_request':
            self.handle_help_request(client_id)
            
        elif msg_type == 'cancel_help':
            self.handle_cancel_help(client_id)
            
        elif msg_type == 'control_response':
            self.handle_control_response(client_id, message)
            
        elif msg_type == 'heartbeat_response':
            pass  # Client is alive
            
        else:
            self.log(f"Unknown message type from client {client_id}: {msg_type}")
            
    def process_technician_message(self, tech_id, message):
        """Process a message from a technician."""
        msg_type = message.get('type')
        
        if msg_type == 'request_control':
            self.handle_control_request(tech_id, message)
            
        elif msg_type == 'end_session':
            self.handle_end_session(tech_id, message)
            
        elif msg_type == 'heartbeat_response':
            pass  # Technician is alive
            
        else:
            self.log(f"Unknown message type from technician {tech_id}: {msg_type}")
            
    def handle_help_request(self, client_id):
        """Handle a help request from a client."""
        if client_id not in self.clients:
            return
            
        # Mark client as requesting help
        self.clients[client_id]['help_requested'] = True
        self.help_requests[client_id] = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'status': 'pending'
        }
        
        client_info = self.clients[client_id]
        self.log(f"Help request from client '{client_info['name']}' ({client_info['ip']})")
        
        # Notify all technicians
        help_notification = {
            'type': 'new_help_request',
            'client_id': client_id,
            'name': client_info['name'],
            'ip': client_info['ip'],
            'timestamp': self.help_requests[client_id]['timestamp']
        }
        
        self.broadcast_to_technicians(help_notification)
        
        # Confirm to client
        response = {
            'type': 'help_confirmed',
            'message': 'Your help request has been sent to available technicians'
        }
        
        try:
            self.clients[client_id]['socket'].send(json.dumps(response).encode('utf-8'))
        except Exception as e:
            self.log(f"Error confirming help request to client {client_id}: {str(e)}")
            
    def handle_cancel_help(self, client_id):
        """Handle help cancellation from a client."""
        if client_id not in self.clients:
            return
            
        self.clients[client_id]['help_requested'] = False
        if client_id in self.help_requests:
            del self.help_requests[client_id]
            
        client_info = self.clients[client_id]
        self.log(f"Help request cancelled by client '{client_info['name']}'")
        
        # Notify technicians
        cancel_notification = {
            'type': 'help_cancelled',
            'client_id': client_id
        }
        
        self.broadcast_to_technicians(cancel_notification)
        
    def handle_control_request(self, tech_id, message):
        """Handle a control request from a technician."""
        client_id = message.get('client_id')
        
        if client_id not in self.clients or tech_id not in self.technicians:
            return
            
        client_info = self.clients[client_id]
        tech_info = self.technicians[tech_id]
        
        self.log(f"Control request: Technician '{tech_info['name']}' -> Client '{client_info['name']}'")
        
        # Send control request to client
        control_request = {
            'type': 'control_request',
            'technician_name': tech_info['name'],
            'technician_ip': tech_info['ip'],
            'tech_id': tech_id
        }
        
        try:
            client_info['socket'].send(json.dumps(control_request).encode('utf-8'))
        except Exception as e:
            self.log(f"Error sending control request to client {client_id}: {str(e)}")
            
    def handle_control_response(self, client_id, message):
        """Handle control response from a client."""
        approved = message.get('approved', False)
        tech_id = message.get('tech_id')
        
        if tech_id not in self.technicians or client_id not in self.clients:
            return
            
        client_info = self.clients[client_id]
        tech_info = self.technicians[tech_id]
        
        if approved:
            # Create session
            session_id = str(uuid.uuid4())[:8]
            self.active_sessions[session_id] = {
                'client_id': client_id,
                'tech_id': tech_id,
                'start_time': datetime.now()
            }
            
            # Update client and technician status
            self.clients[client_id]['session_id'] = session_id
            self.clients[client_id]['help_requested'] = False
            self.technicians[tech_id]['assigned_client'] = client_id
            
            # Remove from help requests
            if client_id in self.help_requests:
                del self.help_requests[client_id]
                
            self.log(f"Control session started: {tech_info['name']} -> {client_info['name']} (Session: {session_id})")
            
            # Notify technician - include client IP for direct connection
            response = {
                'type': 'control_approved',
                'client_id': client_id,
                'client_ip': client_info['ip'],
                'client_name': client_info['name'],
                'session_id': session_id
            }
            
        else:
            self.log(f"Control request denied: {client_info['name']} denied {tech_info['name']}")
            response = {
                'type': 'control_denied',
                'client_id': client_id,
                'client_name': client_info['name']
            }
            
        try:
            tech_info['socket'].send(json.dumps(response).encode('utf-8'))
        except Exception as e:
            self.log(f"Error sending control response to technician {tech_id}: {str(e)}")
            
        # Notify other technicians that this client is no longer available
        if approved:
            unavailable_notification = {
                'type': 'client_unavailable',
                'client_id': client_id
            }
            self.broadcast_to_technicians(unavailable_notification, exclude_tech=tech_id)
            
    def handle_end_session(self, tech_id, message):
        """Handle session end from technician."""
        session_id = message.get('session_id')
        
        if session_id not in self.active_sessions:
            return
            
        session = self.active_sessions[session_id]
        client_id = session['client_id']
        
        # Clean up session
        del self.active_sessions[session_id]
        
        if client_id in self.clients:
            self.clients[client_id]['session_id'] = None
            
        if tech_id in self.technicians:
            self.technicians[tech_id]['assigned_client'] = None
            
        self.log(f"Session {session_id} ended by technician")
        
    def broadcast_to_technicians(self, message, exclude_tech=None):
        """Broadcast a message to all connected technicians."""
        for tech_id, tech_info in list(self.technicians.items()):
            if exclude_tech and tech_id == exclude_tech:
                continue
                
            try:
                tech_info['socket'].send(json.dumps(message).encode('utf-8'))
            except Exception as e:
                self.log(f"Error broadcasting to technician {tech_id}: {str(e)}")
                self.disconnect_technician(tech_id)
                
    def disconnect_client(self, client_id):
        """Disconnect a client."""
        if client_id not in self.clients:
            return
            
        client_info = self.clients[client_id]
        
        # End any active session
        session_id = client_info.get('session_id')
        if session_id and session_id in self.active_sessions:
            del self.active_sessions[session_id]
            
            # Notify technician
            session = self.active_sessions.get(session_id, {})
            tech_id = session.get('tech_id')
            if tech_id in self.technicians:
                self.technicians[tech_id]['assigned_client'] = None
                
        # Remove help request
        if client_id in self.help_requests:
            del self.help_requests[client_id]
            
        # Close socket
        try:
            client_info['socket'].close()
        except:
            pass
            
        # Remove from clients
        del self.clients[client_id]
        
        self.log(f"Client '{client_info['name']}' disconnected")
        
        # Notify technicians
        disconnect_notification = {
            'type': 'client_disconnected',
            'client_id': client_id
        }
        self.broadcast_to_technicians(disconnect_notification)
        
    def disconnect_technician(self, tech_id):
        """Disconnect a technician."""
        if tech_id not in self.technicians:
            return
            
        tech_info = self.technicians[tech_id]
        
        # End any active session
        assigned_client = tech_info.get('assigned_client')
        if assigned_client and assigned_client in self.clients:
            # Find and end session
            for session_id, session in list(self.active_sessions.items()):
                if session['tech_id'] == tech_id:
                    del self.active_sessions[session_id]
                    self.clients[assigned_client]['session_id'] = None
                    break
                    
        # Close socket
        try:
            tech_info['socket'].close()
        except:
            pass
            
        # Remove from technicians
        del self.technicians[tech_id]
        
        self.log(f"Technician '{tech_info['name']}' disconnected")
        
    def heartbeat_checker(self):
        """Check for disconnected clients and technicians."""
        while self.running:
            time.sleep(HEARTBEAT_INTERVAL)
            
            # Check clients
            for client_id in list(self.clients.keys()):
                try:
                    heartbeat = {'type': 'heartbeat'}
                    self.clients[client_id]['socket'].send(json.dumps(heartbeat).encode('utf-8'))
                except:
                    self.disconnect_client(client_id)
                    
            # Check technicians
            for tech_id in list(self.technicians.keys()):
                try:
                    heartbeat = {'type': 'heartbeat'}
                    self.technicians[tech_id]['socket'].send(json.dumps(heartbeat).encode('utf-8'))
                except:
                    self.disconnect_technician(tech_id)
                    
    def update_gui(self):
        """Update the GUI with current status."""
        if not self.running:
            self.root.after(5000, self.update_gui)
            return
            
        # Update statistics
        self.clients_count_label.config(text=str(len(self.clients)))
        self.techs_count_label.config(text=str(len(self.technicians)))
        self.requests_count_label.config(text=str(len(self.help_requests)))
        self.sessions_count_label.config(text=str(len(self.active_sessions)))
        
        # Update clients tree
        for item in self.clients_tree.get_children():
            self.clients_tree.delete(item)
            
        for client_id, client_info in self.clients.items():
            status = "Requesting Help" if client_info['help_requested'] else "In Session" if client_info['session_id'] else "Connected"
            connected_time = client_info['connected_time'].strftime("%H:%M:%S")
            
            self.clients_tree.insert("", "end", iid=client_id, text=client_id,
                                   values=(client_info['ip'], client_info['name'], status, connected_time))
                                   
        # Update technicians tree
        for item in self.techs_tree.get_children():
            self.techs_tree.delete(item)
            
        for tech_id, tech_info in self.technicians.items():
            status = "In Session" if tech_info['assigned_client'] else "Available"
            connected_time = tech_info['connected_time'].strftime("%H:%M:%S")
            
            self.techs_tree.insert("", "end", iid=tech_id, text=tech_id,
                                 values=(tech_info['ip'], tech_info['name'], status, connected_time))
                                 
        # Update sessions tree
        for item in self.sessions_tree.get_children():
            self.sessions_tree.delete(item)
            
        for session_id, session in self.active_sessions.items():
            client_name = self.clients.get(session['client_id'], {}).get('name', 'Unknown')
            tech_name = self.technicians.get(session['tech_id'], {}).get('name', 'Unknown')
            start_time = session['start_time'].strftime("%H:%M:%S")
            duration = str(datetime.now() - session['start_time']).split('.')[0]
            
            self.sessions_tree.insert("", "end", iid=session_id, text=session_id,
                                    values=(client_name, tech_name, start_time, duration))
                                    
        # Schedule next update
        self.root.after(2000, self.update_gui)
        
    def on_close(self):
        """Handle window close."""
        self.stop_server()
        self.root.destroy()
        
    def run(self):
        """Run the mediator server."""
        self.root.mainloop()

if __name__ == "__main__":
    server = MediatorServer()
    server.run() 