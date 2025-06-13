#!/usr/bin/env python3
"""
Modern Login/Sign Up System for Remote Control Application
Beautiful UI with contemporary design patterns.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import hashlib
import os
import subprocess
import sys
import secrets

class ModernLoginSystem:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_database()
        self.setup_modern_gui()
        
    def setup_database(self):
        """Initialize SQLite database and create users table."""
        self.db_path = "users.db"
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    role TEXT CHECK(role IN ('client', 'technician')) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Check if salt column exists (for migration of existing database)
            cursor.execute("PRAGMA table_info(users)")
            columns = [column[1] for column in cursor.fetchall()]
            if 'salt' not in columns:
                cursor.execute('ALTER TABLE users ADD COLUMN salt TEXT DEFAULT ""')
                print("Added salt column to existing database")
            
            conn.commit()
            conn.close()
            print("Database initialized successfully")
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to initialize database: {str(e)}")
            
    def setup_modern_gui(self):
        """Set up the modern GUI interface."""
        # Window configuration
        self.root.title("🖥️ Remote Control System")
        self.root.geometry("650x850")
        self.root.resizable(False, False)
        
        # Modern color scheme
        self.colors = {
            'primary': '#1a1a2e',      # Dark blue
            'secondary': '#16213e',     # Darker blue
            'accent': '#e94560',        # Red accent
            'accent_hover': '#ff6b7a',  # Light red
            'success': '#00d4aa',       # Teal
            'error': '#f44336',         # Red error
            'text_light': '#ffffff',    # White
            'text_secondary': '#a0a0a0', # Light gray
            'input_bg': '#2a2a3e',      # Dark input background
            'card_bg': '#1e1e3a',       # Card background
        }
        
        # Configure window
        self.root.configure(bg=self.colors['primary'])
        
        # Main content frame
        self.main_frame = tk.Frame(self.root, bg=self.colors['primary'])
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create main container with gradient effect
        self.create_gradient_background()
        
        # Logo and header
        self.create_header()
        
        # Login card
        self.create_login_card()
        
        # Footer
        self.create_footer()
        
        # Show login form by default
        self.current_mode = None
        self.show_login_form()
        
        # Center window
        self.center_window()
        
    def create_gradient_background(self):
        """Create a gradient background effect."""
        # Since we're using a simple solid color approach, we'll just set the background
        # The main_frame already has the primary color background
        pass
        
    def create_header(self):
        """Create the header section."""
        header_frame = tk.Frame(self.main_frame, bg=self.colors['primary'])
        header_frame.pack(pady=(40, 20))
        
        # Main title with emoji
        title = tk.Label(
            header_frame,
            text="🖥️ Remote Control",
            font=('Segoe UI', 32, 'bold'),
            fg=self.colors['text_light'],
            bg=self.colors['primary']
        )
        title.pack()
        
        # Subtitle
        subtitle = tk.Label(
            header_frame,
            text="Secure • Fast • Reliable",
            font=('Segoe UI', 14),
            fg=self.colors['text_secondary'],
            bg=self.colors['primary']
        )
        subtitle.pack(pady=(5, 0))
        
    def create_login_card(self):
        """Create the main login/signup card."""
        # Card frame with shadow effect
        card_shadow = tk.Frame(self.main_frame, bg='#0f0f1f', height=550, width=450)
        card_shadow.pack(pady=(20, 0))
        card_shadow.pack_propagate(False)
        
        self.card_frame = tk.Frame(card_shadow, bg=self.colors['card_bg'], height=540, width=440)
        self.card_frame.place(x=5, y=5)
        self.card_frame.pack_propagate(False)
        
        # Tab buttons frame
        tab_frame = tk.Frame(self.card_frame, bg=self.colors['card_bg'])
        tab_frame.pack(fill=tk.X, padx=20, pady=(20, 0))
        
        # Login tab button
        self.login_tab = self.create_tab_button(
            tab_frame, "🔐 Sign In", 
            lambda: self.show_login_form(),
            active=True
        )
        self.login_tab.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Register tab button
        self.register_tab = self.create_tab_button(
            tab_frame, "✨ Sign Up",
            lambda: self.show_register_form(),
            active=False
        )
        self.register_tab.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # Create scrollable content area
        self.create_scrollable_content_area()
        
    def create_tab_button(self, parent, text, command, active=False):
        """Create a modern tab button."""
        if active:
            bg_color = self.colors['accent']
            fg_color = self.colors['text_light']
        else:
            bg_color = self.colors['input_bg']
            fg_color = self.colors['text_secondary']
            
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=('Segoe UI', 11, 'bold'),
            bg=bg_color,
            fg=fg_color,
            relief='flat',
            borderwidth=0,
            padx=15,
            pady=12,
            cursor='hand2'
        )
        
        # Hover effects
        def on_enter(e):
            if not active:
                btn.configure(bg=self.colors['secondary'])
                
        def on_leave(e):
            if not active:
                btn.configure(bg=self.colors['input_bg'])
                
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn
        
    def create_scrollable_content_area(self):
        """Create a scrollable content area for the form."""
        # Frame to contain canvas and scrollbar
        scroll_frame = tk.Frame(self.card_frame, bg=self.colors['card_bg'])
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create canvas for scrolling
        self.content_canvas = tk.Canvas(
            scroll_frame,
            bg=self.colors['card_bg'],
            highlightthickness=0,
            height=400
        )
        self.content_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create scrollbar
        scrollbar = ttk.Scrollbar(
            scroll_frame,
            orient="vertical",
            command=self.content_canvas.yview
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure canvas
        self.content_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Create the actual content frame inside the canvas
        self.content_area = tk.Frame(self.content_canvas, bg=self.colors['card_bg'])
        self.canvas_window = self.content_canvas.create_window(
            (0, 0), 
            window=self.content_area, 
            anchor="nw"
        )
        
        # Bind events for scrolling
        def configure_scroll_region(event=None):
            self.content_canvas.configure(scrollregion=self.content_canvas.bbox("all"))
            
        def configure_canvas_width(event=None):
            # Update the canvas window width to match the canvas
            canvas_width = self.content_canvas.winfo_width()
            self.content_canvas.itemconfig(self.canvas_window, width=canvas_width)
            
        self.content_area.bind('<Configure>', configure_scroll_region)
        self.content_canvas.bind('<Configure>', configure_canvas_width)
        
        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            self.content_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
        # Bind mousewheel events
        def bind_mousewheel(event):
            self.content_canvas.bind_all("<MouseWheel>", _on_mousewheel)
            
        def unbind_mousewheel(event):
            self.content_canvas.unbind_all("<MouseWheel>")
            
        self.content_canvas.bind('<Enter>', bind_mousewheel)
        self.content_canvas.bind('<Leave>', unbind_mousewheel)
        
    def update_tab_buttons(self, active_tab):
        """Update tab button states."""
        if active_tab == 'login':
            self.login_tab.configure(
                bg=self.colors['accent'],
                fg=self.colors['text_light']
            )
            self.register_tab.configure(
                bg=self.colors['input_bg'],
                fg=self.colors['text_secondary']
            )
        else:
            self.login_tab.configure(
                bg=self.colors['input_bg'],
                fg=self.colors['text_secondary']
            )
            self.register_tab.configure(
                bg=self.colors['accent'],
                fg=self.colors['text_light']
            )
        
    def show_login_form(self):
        """Show the login form."""
        if self.current_mode == 'login':
            return
            
        self.current_mode = 'login'
        self.update_tab_buttons('login')
        self.clear_content()
        
        # Welcome message
        welcome = tk.Label(
            self.content_area,
            text="Welcome Back! 👋",
            font=('Segoe UI', 20, 'bold'),
            fg=self.colors['text_light'],
            bg=self.colors['card_bg']
        )
        welcome.pack(pady=(20, 30))
        
        # Username field
        self.create_input_field("👤 Username", "username")
        
        # Password field
        self.create_input_field("🔒 Password", "password", show="*")
        
        # Login button
        login_btn = self.create_action_button(
            "🚀 Sign In",
            self.handle_signin,
            self.colors['accent']
        )
        login_btn.pack(pady=(30, 20), fill=tk.X)
        
        # Info text
        info = tk.Label(
            self.content_area,
            text="Your role will be detected automatically",
            font=('Segoe UI', 10),
            fg=self.colors['text_secondary'],
            bg=self.colors['card_bg']
        )
        info.pack()
        
        # Focus username field
        self.username_entry.focus()
        
    def show_register_form(self):
        """Show the registration form."""
        if self.current_mode == 'register':
            return
            
        self.current_mode = 'register'
        self.update_tab_buttons('register')
        self.clear_content()
        
        # Welcome message
        welcome = tk.Label(
            self.content_area,
            text="Create Account ✨",
            font=('Segoe UI', 20, 'bold'),
            fg=self.colors['text_light'],
            bg=self.colors['card_bg']
        )
        welcome.pack(pady=(10, 20))
        
        # Username field
        self.create_input_field("👤 Username", "reg_username")
        
        # Password field
        self.create_input_field("🔒 Password", "reg_password", show="*")
        
        # Password strength indicator
        self.create_password_strength_indicator()
        
        # Confirm password field
        self.create_input_field("🔒 Confirm Password", "reg_confirm", show="*")
        
        # Role selection
        self.create_role_selector()
        
        # Register button
        register_btn = self.create_action_button(
            "✨ Create Account",
            self.handle_signup,
            self.colors['success']
        )
        register_btn.pack(pady=(20, 10), fill=tk.X)
        
        # Add extra padding at bottom for scrolling
        tk.Frame(self.content_area, bg=self.colors['card_bg'], height=50).pack()
        
        # Focus username field
        self.reg_username_entry.focus()
        
    def create_password_strength_indicator(self):
        """Create password strength indicator with requirements checklist."""
        # Container frame
        strength_frame = tk.Frame(self.content_area, bg=self.colors['card_bg'])
        strength_frame.pack(fill=tk.X, pady=(5, 15))
        
        # Title
        tk.Label(
            strength_frame,
            text="Password Requirements:",
            font=('Segoe UI', 9, 'bold'),
            fg=self.colors['text_secondary'],
            bg=self.colors['card_bg']
        ).pack(anchor='w')
        
        # Requirements list
        requirements_frame = tk.Frame(strength_frame, bg=self.colors['card_bg'])
        requirements_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Store requirement labels for dynamic updates
        self.requirement_labels = {}
        requirements = [
            ("length", "At least 8 characters"),
            ("uppercase", "At least one uppercase letter (A-Z)"),
            ("lowercase", "At least one lowercase letter (a-z)"),
            ("number", "At least one number (0-9)"),
            ("special", "At least one special character (!@#$%^&*...)"),
            ("common", "Not a common weak password")
        ]
        
        for req_id, req_text in requirements:
            req_frame = tk.Frame(requirements_frame, bg=self.colors['card_bg'])
            req_frame.pack(fill=tk.X, anchor='w')
            
            # Status icon
            status_label = tk.Label(
                req_frame,
                text="❌",
                font=('Segoe UI', 8),
                bg=self.colors['card_bg'],
                fg=self.colors['error']
            )
            status_label.pack(side=tk.LEFT)
            
            # Requirement text
            text_label = tk.Label(
                req_frame,
                text=req_text,
                font=('Segoe UI', 8),
                bg=self.colors['card_bg'],
                fg=self.colors['text_secondary']
            )
            text_label.pack(side=tk.LEFT, padx=(5, 0))
            
            self.requirement_labels[req_id] = (status_label, text_label)
        
        # Bind password field to update requirements
        self.reg_password_entry.bind('<KeyRelease>', self.update_password_strength)
        
    def update_password_strength(self, event=None):
        """Update password strength indicator in real-time."""
        password = self.reg_password_entry.get()
        
        # Check each requirement
        requirements_status = {
            "length": len(password) >= 8,
            "uppercase": any(c.isupper() for c in password),
            "lowercase": any(c.islower() for c in password),
            "number": any(c.isdigit() for c in password),
            "special": any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password),
            "common": password.lower() not in ['password', '12345678', 'qwerty123', 'admin123', 'password123']
        }
        
        # Update visual indicators
        for req_id, (status_label, text_label) in self.requirement_labels.items():
            if requirements_status[req_id]:
                status_label.config(text="✅", fg=self.colors['success'])
                text_label.config(fg=self.colors['success'])
            else:
                status_label.config(text="❌", fg=self.colors['error'])
                text_label.config(fg=self.colors['text_secondary'])
        
    def create_input_field(self, label, field_name, show=None):
        """Create a modern input field."""
        # Label
        label_widget = tk.Label(
            self.content_area,
            text=label,
            font=('Segoe UI', 11, 'bold'),
            fg=self.colors['text_light'],
            bg=self.colors['card_bg']
        )
        label_widget.pack(anchor='w', pady=(10, 5))
        
        # Entry frame for border effect
        entry_frame = tk.Frame(self.content_area, bg=self.colors['accent'], height=45)
        entry_frame.pack(fill=tk.X, pady=(0, 5))
        entry_frame.pack_propagate(False)
        
        # Entry widget
        entry = tk.Entry(
            entry_frame,
            font=('Segoe UI', 12),
            bg=self.colors['input_bg'],
            fg=self.colors['text_light'],
            relief='flat',
            borderwidth=0,
            show=show,
            insertbackground=self.colors['text_light']
        )
        entry.place(x=2, y=2, relwidth=1, relheight=1, width=-4, height=-4)
        
        # Store reference
        setattr(self, f"{field_name}_entry", entry)
        
        # Bind Enter key for password fields
        if "password" in field_name:
            if field_name == "password":
                entry.bind('<Return>', lambda e: self.handle_signin())
            elif field_name == "reg_confirm":
                entry.bind('<Return>', lambda e: self.handle_signup())
                
    def create_role_selector(self):
        """Create role selection widget."""
        # Label
        label = tk.Label(
            self.content_area,
            text="🎯 Choose Your Role",
            font=('Segoe UI', 11, 'bold'),
            fg=self.colors['text_light'],
            bg=self.colors['card_bg']
        )
        label.pack(anchor='w', pady=(15, 10))
        
        # Role frame
        role_frame = tk.Frame(self.content_area, bg=self.colors['card_bg'])
        role_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.selected_role = tk.StringVar(value="client")
        
        # Client option
        client_frame = tk.Frame(role_frame, bg=self.colors['input_bg'])
        client_frame.pack(fill=tk.X, pady=(0, 8))
        
        client_radio = tk.Radiobutton(
            client_frame,
            text="👤 Client (Need Help)",
            variable=self.selected_role,
            value="client",
            font=('Segoe UI', 11),
            fg=self.colors['text_light'],
            bg=self.colors['input_bg'],
            selectcolor=self.colors['accent'],
            activebackground=self.colors['input_bg'],
            activeforeground=self.colors['text_light']
        )
        client_radio.pack(anchor='w', padx=15, pady=10)
        
        # Technician option
        tech_frame = tk.Frame(role_frame, bg=self.colors['input_bg'])
        tech_frame.pack(fill=tk.X)
        
        tech_radio = tk.Radiobutton(
            tech_frame,
            text="🔧 Technician (Provide Help)",
            variable=self.selected_role,
            value="technician",
            font=('Segoe UI', 11),
            fg=self.colors['text_light'],
            bg=self.colors['input_bg'],
            selectcolor=self.colors['accent'],
            activebackground=self.colors['input_bg'],
            activeforeground=self.colors['text_light']
        )
        tech_radio.pack(anchor='w', padx=15, pady=10)
        
    def create_action_button(self, text, command, color):
        """Create a modern action button."""
        btn = tk.Button(
            self.content_area,
            text=text,
            command=command,
            font=('Segoe UI', 12, 'bold'),
            bg=color,
            fg=self.colors['text_light'],
            relief='flat',
            borderwidth=0,
            padx=20,
            pady=15,
            cursor='hand2'
        )
        
        # Hover effects
        def on_enter(e):
            if color == self.colors['accent']:
                btn.configure(bg=self.colors['accent_hover'])
            else:
                btn.configure(bg='#00f0cc')
                
        def on_leave(e):
            btn.configure(bg=color)
            
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn
        
    def create_footer(self):
        """Create footer section."""
        footer = tk.Label(
            self.main_frame,
            text="🔒 Secure Remote Access System",
            font=('Segoe UI', 10),
            fg=self.colors['text_secondary'],
            bg=self.colors['primary']
        )
        footer.pack(pady=(20, 30))
        
    def clear_content(self):
        """Clear content area."""
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
    def center_window(self):
        """Center the window on screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def generate_salt(self):
        """Generate a random salt for password hashing."""
        return secrets.token_hex(32)  # 64 character hex string
        
    def hash_password(self, password, salt):
        """Hash password using SHA256 with salt."""
        # Combine password and salt
        salted_password = password + salt
        return hashlib.sha256(salted_password.encode('utf-8')).hexdigest()
        
    def validate_password_strength(self, password):
        """Validate password strength and return issues list."""
        issues = []
        
        if len(password) < 8:
            issues.append("At least 8 characters")
        
        if not any(c.isupper() for c in password):
            issues.append("At least one uppercase letter")
            
        if not any(c.islower() for c in password):
            issues.append("At least one lowercase letter")
            
        if not any(c.isdigit() for c in password):
            issues.append("At least one number")
            
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            issues.append("At least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)")
            
        # Check for common weak patterns
        if password.lower() in ['password', '12345678', 'qwerty123', 'admin123', 'password123']:
            issues.append("Cannot be a common weak password")
            
        # Check for repeated characters
        if len(set(password)) < 4:
            issues.append("Too many repeated characters")
            
        return issues
    
    def validate_input(self, username, password, confirm_password=None):
        """Validate user input."""
        if not username.strip():
            self.show_error("Username cannot be empty!")
            return False
            
        if not password:
            self.show_error("Password cannot be empty!")
            return False
            
        if len(username.strip()) < 3:
            self.show_error("Username must be at least 3 characters!")
            return False
            
        # For signup, validate password strength
        if confirm_password is not None:
            password_issues = self.validate_password_strength(password)
            if password_issues:
                error_msg = "Password must meet the following requirements:\n\n" + "\n".join(f"• {issue}" for issue in password_issues)
                self.show_error(error_msg)
                return False
        else:
            # For login, just check minimum length (backward compatibility)
            if len(password) < 4:
                self.show_error("Password must be at least 4 characters!")
                return False
            
        if confirm_password is not None and password != confirm_password:
            self.show_error("Passwords do not match!")
            return False
                
        return True
        
    def show_error(self, message):
        """Show error message with modern styling."""
        # Create custom error dialog
        error_window = tk.Toplevel(self.root)
        error_window.title("Error")
        error_window.geometry("400x180")
        error_window.configure(bg=self.colors['secondary'])
        error_window.resizable(False, False)
        error_window.transient(self.root)
        error_window.grab_set()
        
        # Center error window
        error_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (400 // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (180 // 2)
        error_window.geometry(f"400x180+{x}+{y}")
        
        # Error content
        error_frame = tk.Frame(error_window, bg=self.colors['secondary'])
        error_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Error icon and message
        tk.Label(
            error_frame,
            text="⚠️ Error",
            font=('Segoe UI', 14, 'bold'),
            fg=self.colors['accent'],
            bg=self.colors['secondary']
        ).pack(pady=(0, 10))
        
        tk.Label(
            error_frame,
            text=message,
            font=('Segoe UI', 11),
            fg=self.colors['text_light'],
            bg=self.colors['secondary'],
            wraplength=300
        ).pack(pady=(0, 20))
        
        # OK button
        ok_btn = tk.Button(
            error_frame,
            text="OK",
            command=error_window.destroy,
            font=('Segoe UI', 14, 'bold'),
            bg=self.colors['accent'],
            fg=self.colors['text_light'],
            relief='flat',
            padx=50,
            pady=15,
            cursor='hand2',
            width=12
        )
        
        # Add hover effects
        def on_enter(e):
            ok_btn.configure(bg=self.colors['accent_hover'])
        def on_leave(e):
            ok_btn.configure(bg=self.colors['accent'])
        
        ok_btn.bind("<Enter>", on_enter)
        ok_btn.bind("<Leave>", on_leave)
        ok_btn.pack(pady=10)
        
        # Allow Enter key to close dialog
        error_window.bind('<Return>', lambda e: error_window.destroy())
        ok_btn.focus_set()
        
    def show_success(self, message):
        """Show success message with modern styling."""
        # Create custom success dialog
        success_window = tk.Toplevel(self.root)
        success_window.title("Success")
        success_window.geometry("400x180")
        success_window.configure(bg=self.colors['secondary'])
        success_window.resizable(False, False)
        success_window.transient(self.root)
        success_window.grab_set()
        
        # Center success window
        success_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (400 // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (180 // 2)
        success_window.geometry(f"400x180+{x}+{y}")
        
        # Success content
        success_frame = tk.Frame(success_window, bg=self.colors['secondary'])
        success_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Success icon and message
        tk.Label(
            success_frame,
            text="✅ Success",
            font=('Segoe UI', 14, 'bold'),
            fg=self.colors['success'],
            bg=self.colors['secondary']
        ).pack(pady=(0, 10))
        
        tk.Label(
            success_frame,
            text=message,
            font=('Segoe UI', 11),
            fg=self.colors['text_light'],
            bg=self.colors['secondary'],
            wraplength=300
        ).pack(pady=(0, 20))
        
        # OK button
        ok_btn = tk.Button(
            success_frame,
            text="OK",
            command=success_window.destroy,
            font=('Segoe UI', 14, 'bold'),
            bg=self.colors['success'],
            fg=self.colors['text_light'],
            relief='flat',
            padx=50,
            pady=15,
            cursor='hand2',
            width=12
        )
        
        # Add hover effects
        def on_enter(e):
            ok_btn.configure(bg='#00f0cc')  # Lighter green
        def on_leave(e):
            ok_btn.configure(bg=self.colors['success'])
        
        ok_btn.bind("<Enter>", on_enter)
        ok_btn.bind("<Leave>", on_leave)
        ok_btn.pack(pady=10)
        
        # Allow Enter key to close dialog
        success_window.bind('<Return>', lambda e: success_window.destroy())
        ok_btn.focus_set()
        
    def handle_signin(self):
        """Handle sign in."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not self.validate_input(username, password):
            return
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # First get the user's salt
            cursor.execute('SELECT salt, password, role FROM users WHERE username = ?', (username,))
            result = cursor.fetchone()
            
            if result:
                stored_salt, stored_password, user_role = result
                
                # Handle users without salt (migration case)
                if not stored_salt:
                    # For existing users without salt, check if they're using old plain hash
                    old_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
                    if old_hash == stored_password:
                        # Migrate user to salted password
                        new_salt = self.generate_salt()
                        new_hash = self.hash_password(password, new_salt)
                        cursor.execute('UPDATE users SET password = ?, salt = ? WHERE username = ?', 
                                     (new_hash, new_salt, username))
                        conn.commit()
                        self.show_success(f"Welcome {username}!\nPassword security upgraded.\nLogging in as {user_role.title()}...")
                        self.root.after(2000, lambda: self.launch_application(user_role, username))
                    else:
                        self.show_error("Invalid username or password!")
                else:
                    # Normal salted password verification
                    hashed_password = self.hash_password(password, stored_salt)
                    if hashed_password == stored_password:
                        self.show_success(f"Welcome {username}!\nLogging in as {user_role.title()}...")
                        self.root.after(1500, lambda: self.launch_application(user_role, username))
                    else:
                        self.show_error("Invalid username or password!")
            else:
                self.show_error("Invalid username or password!")
                
            conn.close()
                
        except Exception as e:
            self.show_error(f"Database error: {str(e)}")
            
    def handle_signup(self):
        """Handle sign up."""
        username = self.reg_username_entry.get().strip()
        password = self.reg_password_entry.get()
        confirm_password = self.reg_confirm_entry.get()
        role = self.selected_role.get()
        
        if not self.validate_input(username, password, confirm_password):
            return
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if user exists
            cursor.execute('SELECT username FROM users WHERE username = ?', (username,))
            if cursor.fetchone():
                self.show_error("Username already exists!")
                conn.close()
                return
                
            # Create user with salt
            salt = self.generate_salt()
            hashed_password = self.hash_password(password, salt)
            cursor.execute('''
                INSERT INTO users (username, password, salt, role) 
                VALUES (?, ?, ?, ?)
            ''', (username, hashed_password, salt, role))
            
            conn.commit()
            conn.close()
            
            self.show_success(f"Account created successfully!\n{username} registered as {role.title()}")
            
            # Switch to login and prefill username
            self.root.after(1500, lambda: self.switch_to_login_with_username(username))
            
        except Exception as e:
            self.show_error(f"Database error: {str(e)}")
            
    def switch_to_login_with_username(self, username):
        """Switch to login tab and prefill username."""
        self.show_login_form()
        self.username_entry.delete(0, tk.END)
        self.username_entry.insert(0, username)
        self.password_entry.focus()
            
    def launch_application(self, role, username):
        """Launch appropriate application."""
        try:
            if role == "client":
                script_path = "client_with_mediator.py"
            else:
                script_path = "technician_with_mediator.py"
                
            if not os.path.exists(script_path):
                self.show_error(f"File {script_path} not found!")
                return
                
            self.root.destroy()
            subprocess.Popen([sys.executable, script_path, username])
            
        except Exception as e:
            self.show_error(f"Launch error: {str(e)}")
            
    def run(self):
        """Run the application."""
        self.root.mainloop()

def main():
    try:
        app = ModernLoginSystem()
        app.run()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 