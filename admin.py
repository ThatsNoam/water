#!/usr/bin/env python3
"""
Admin Panel for Remote Control System
Secure user management interface.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
import hashlib
import secrets
from datetime import datetime
import getpass

def authenticate_admin():
    """GUI-based admin authentication with modern design."""
    # Create authentication window
    auth_root = tk.Tk()
    auth_root.title("🔐 Admin Authentication")
    auth_root.geometry("450x300")
    auth_root.resizable(False, False)
    
    # Modern color scheme matching the admin panel
    colors = {
        'primary': '#1a1a2e',
        'secondary': '#16213e',
        'accent': '#e94560',
        'success': '#00d4aa',
        'error': '#f44336',
        'text_light': '#ffffff',
        'text_secondary': '#a0a0a0',
        'card_bg': '#1e1e3a',
        'input_bg': '#2a2a3e',
    }
    
    auth_root.configure(bg=colors['primary'])
    
    # Center the window
    auth_root.update_idletasks()
    x = (auth_root.winfo_screenwidth() // 2) - (450 // 2)
    y = (auth_root.winfo_screenheight() // 2) - (300 // 2)
    auth_root.geometry(f'450x300+{x}+{y}')
    
    # Variable to store authentication result
    authenticated = tk.BooleanVar(value=False)
    
    # Create main frame
    main_frame = tk.Frame(auth_root, bg=colors['primary'])
    main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
    
    # Header
    header_frame = tk.Frame(main_frame, bg=colors['accent'], height=60)
    header_frame.pack(fill=tk.X, pady=(0, 20))
    header_frame.pack_propagate(False)
    
    tk.Label(
        header_frame,
        text="🔐 Admin Access Required",
        font=('Segoe UI', 18, 'bold'),
        bg=colors['accent'],
        fg=colors['text_light']
    ).place(relx=0.5, rely=0.5, anchor='center')
    
    # Content frame
    content_frame = tk.Frame(main_frame, bg=colors['card_bg'])
    content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Instructions
    tk.Label(
        content_frame,
        text="Enter admin password to access the admin panel:",
        font=('Segoe UI', 12),
        bg=colors['card_bg'],
        fg=colors['text_light'],
        wraplength=350
    ).pack(pady=(20, 15))
    
    # Password frame
    password_frame = tk.Frame(content_frame, bg=colors['card_bg'])
    password_frame.pack(pady=10)
    
    tk.Label(
        password_frame,
        text="Password:",
        font=('Segoe UI', 11, 'bold'),
        bg=colors['card_bg'],
        fg=colors['text_light']
    ).pack(anchor='w')
    
    password_entry = tk.Entry(
        password_frame,
        font=('Segoe UI', 12),
        bg=colors['input_bg'],
        fg=colors['text_light'],
        relief='flat',
        bd=5,
        width=30,
        show='*'
    )
    password_entry.pack(pady=(5, 0))
    
    # Error label (initially hidden)
    error_label = tk.Label(
        content_frame,
        text="",
        font=('Segoe UI', 10),
        bg=colors['card_bg'],
        fg=colors['error']
    )
    error_label.pack(pady=(10, 0))
    
    # Buttons frame
    button_frame = tk.Frame(content_frame, bg=colors['card_bg'])
    button_frame.pack(pady=(20, 10))
    
    def check_password():
        """Check if the entered password is correct."""
        correct_password = "admin123"  # Change this to your desired password
        entered_password = password_entry.get()
        
        if entered_password == correct_password:
            authenticated.set(True)
            auth_root.destroy()
        else:
            error_label.config(text="❌ Incorrect password! Access denied.")
            password_entry.delete(0, tk.END)
            password_entry.focus()
            
            # Flash the entry field red
            original_bg = password_entry.cget('bg')
            password_entry.config(bg=colors['error'])
            auth_root.after(200, lambda: password_entry.config(bg=original_bg))
    
    def cancel_auth():
        """Cancel authentication."""
        authenticated.set(False)
        auth_root.destroy()
    
    # Login button
    login_btn = tk.Button(
        button_frame,
        text="🔓 Login",
        command=check_password,
        font=('Segoe UI', 11, 'bold'),
        bg=colors['success'],
        fg=colors['text_light'],
        relief='flat',
        padx=25,
        pady=8,
        cursor='hand2'
    )
    login_btn.pack(side=tk.LEFT, padx=(0, 10))
    
    # Cancel button
    cancel_btn = tk.Button(
        button_frame,
        text="❌ Cancel",
        command=cancel_auth,
        font=('Segoe UI', 11, 'bold'),
        bg=colors['error'],
        fg=colors['text_light'],
        relief='flat',
        padx=25,
        pady=8,
        cursor='hand2'
    )
    cancel_btn.pack(side=tk.LEFT)
    
    # Hover effects
    def on_enter_login(e):
        login_btn.configure(bg='#00f0cc')
    def on_leave_login(e):
        login_btn.configure(bg=colors['success'])
    def on_enter_cancel(e):
        cancel_btn.configure(bg='#ff6b6b')
    def on_leave_cancel(e):
        cancel_btn.configure(bg=colors['error'])
        
    login_btn.bind("<Enter>", on_enter_login)
    login_btn.bind("<Leave>", on_leave_login)
    cancel_btn.bind("<Enter>", on_enter_cancel)
    cancel_btn.bind("<Leave>", on_leave_cancel)
    
    # Bind Enter key to login
    password_entry.bind('<Return>', lambda e: check_password())
    
    # Focus password field
    password_entry.focus()
    
    # Run the authentication dialog
    auth_root.mainloop()
    
    return authenticated.get()

class AdminPanel:
    def __init__(self):
        self.root = tk.Tk()
        self.db_path = "users.db"
        self.setup_gui()
        self.load_users()
        
    def setup_gui(self):
        """Set up the modern admin GUI."""
        self.root.title("🔧 Admin Panel - Remote Control System")
        self.root.geometry("1000x700")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Modern color scheme
        self.colors = {
            'primary': '#1a1a2e',
            'secondary': '#16213e',
            'accent': '#e94560',
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
        
        # Create control panel
        self.create_control_panel()
        
    def create_header(self):
        """Create the header section."""
        header_frame = tk.Frame(self.root, bg=self.colors['accent'], height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Header content
        header_content = tk.Frame(header_frame, bg=self.colors['accent'])
        header_content.place(relx=0.02, rely=0.5, anchor='w')
        
        # Icon and title
        tk.Label(
            header_content,
            text="🔧",
            font=('Segoe UI', 28),
            bg=self.colors['accent'],
            fg=self.colors['text_light']
        ).pack(side=tk.LEFT, padx=(0, 15))
        
        title_frame = tk.Frame(header_content, bg=self.colors['accent'])
        title_frame.pack(side=tk.LEFT)
        
        tk.Label(
            title_frame,
            text="Admin Panel",
            font=('Segoe UI', 22, 'bold'),
            bg=self.colors['accent'],
            fg=self.colors['text_light']
        ).pack(anchor='w')
        
        tk.Label(
            title_frame,
            text="User Management & System Administration",
            font=('Segoe UI', 12),
            bg=self.colors['accent'],
            fg='#ffccd5'
        ).pack(anchor='w')
        
        # Refresh button in header
        refresh_btn = tk.Button(
            header_frame,
            text="🔄 Refresh",
            command=self.load_users,
            font=('Segoe UI', 12, 'bold'),
            bg=self.colors['success'],
            fg=self.colors['text_light'],
            relief='flat',
            padx=20,
            pady=8,
            cursor='hand2'
        )
        refresh_btn.place(relx=0.95, rely=0.5, anchor='e', x=-20)
        
    def create_main_content(self):
        """Create the main content area with user table."""
        main_frame = tk.Frame(self.root, bg=self.colors['primary'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Users table frame
        table_frame = tk.LabelFrame(
            main_frame,
            text="📋 User Database",
            font=('Segoe UI', 14, 'bold'),
            bg=self.colors['card_bg'],
            fg=self.colors['text_light'],
            relief='flat',
            bd=0
        )
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Create treeview with modern styling
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure treeview colors
        style.configure(
            "Treeview",
            background=self.colors['input_bg'],
            foreground=self.colors['text_light'],
            fieldbackground=self.colors['input_bg'],
            borderwidth=0,
            font=('Segoe UI', 10)
        )
        
        style.configure(
            "Treeview.Heading",
            background=self.colors['secondary'],
            foreground=self.colors['text_light'],
            font=('Segoe UI', 11, 'bold'),
            relief='flat'
        )
        
        # Create frame for treeview and scrollbar
        tree_frame = tk.Frame(table_frame, bg=self.colors['card_bg'])
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Create treeview
        columns = ("Username", "Role", "Created", "Password Hash", "Salt")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        self.tree.heading("Username", text="👤 Username")
        self.tree.heading("Role", text="🎭 Role")
        self.tree.heading("Created", text="📅 Created")
        self.tree.heading("Password Hash", text="🔒 Password Hash")
        self.tree.heading("Salt", text="🧂 Salt")
        
        # Set column widths
        self.tree.column("Username", width=150, minwidth=120)
        self.tree.column("Role", width=100, minwidth=80)
        self.tree.column("Created", width=150, minwidth=120)
        self.tree.column("Password Hash", width=200, minwidth=150)
        self.tree.column("Salt", width=150, minwidth=120)
        
        # Create scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click event
        self.tree.bind("<Double-1>", self.on_user_double_click)
        
    def create_control_panel(self):
        """Create the control panel with action buttons."""
        control_frame = tk.Frame(self.root, bg=self.colors['card_bg'], height=100)
        control_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        control_frame.pack_propagate(False)
        
        # Left side - user actions
        left_frame = tk.Frame(control_frame, bg=self.colors['card_bg'])
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=20, pady=20)
        
        tk.Label(
            left_frame,
            text="👥 User Actions:",
            font=('Segoe UI', 12, 'bold'),
            bg=self.colors['card_bg'],
            fg=self.colors['text_light']
        ).pack(anchor='w')
        
        button_frame = tk.Frame(left_frame, bg=self.colors['card_bg'])
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Add user button
        add_btn = self.create_action_button(
            button_frame, "➕ Add User", self.add_user, self.colors['success']
        )
        add_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Delete user button
        delete_btn = self.create_action_button(
            button_frame, "🗑️ Delete User", self.delete_user, self.colors['error']
        )
        delete_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Reset password button
        reset_btn = self.create_action_button(
            button_frame, "🔑 Reset Password", self.reset_password, self.colors['warning']
        )
        reset_btn.pack(side=tk.LEFT)
        
        # Right side - database info
        right_frame = tk.Frame(control_frame, bg=self.colors['card_bg'])
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=20, pady=20)
        
        tk.Label(
            right_frame,
            text="📊 Database Info:",
            font=('Segoe UI', 12, 'bold'),
            bg=self.colors['card_bg'],
            fg=self.colors['text_light']
        ).pack(anchor='w')
        
        self.info_label = tk.Label(
            right_frame,
            text="Loading...",
            font=('Segoe UI', 10),
            bg=self.colors['card_bg'],
            fg=self.colors['text_secondary']
        )
        self.info_label.pack(anchor='w', pady=(10, 0))
        
        # Security warning
        warning_frame = tk.Frame(control_frame, bg=self.colors['card_bg'])
        warning_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20)
        
        tk.Label(
            warning_frame,
            text="⚠️ Security Note: Password hashes are shown for technical purposes only. Never share this information.",
            font=('Segoe UI', 9),
            bg=self.colors['card_bg'],
            fg=self.colors['warning'],
            wraplength=800
        ).pack()
        
    def create_action_button(self, parent, text, command, color):
        """Create a styled action button."""
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
            cursor='hand2'
        )
        
        # Hover effects
        def on_enter(e):
            if color == self.colors['success']:
                btn.configure(bg='#00f0cc')
            elif color == self.colors['error']:
                btn.configure(bg='#ff6b6b')
            elif color == self.colors['warning']:
                btn.configure(bg='#ffb74d')
                
        def on_leave(e):
            btn.configure(bg=color)
            
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn
        
    def load_users(self):
        """Load all users from database."""
        try:
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
                
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT username, role, created_at FROM users ORDER BY created_at DESC')
            users = cursor.fetchall()
            
            for user in users:
                username, role, created_at = user
                
                # Parse date
                try:
                    if created_at:
                        date_obj = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        formatted_date = date_obj.strftime('%Y-%m-%d %H:%M')
                    else:
                        formatted_date = "Unknown"
                except:
                    formatted_date = "Unknown"
                
                # Color code by role
                tag = 'client' if role == 'client' else 'technician'
                
                self.tree.insert('', 'end', values=(username, role.title(), formatted_date), tags=(tag,))
            
            # Configure tags
            self.tree.tag_configure('client', background='#1e3a1e', foreground='#90ee90')
            self.tree.tag_configure('technician', background='#3a1e1e', foreground='#ffb6c1')
            
            # Update status
            user_count = len(users)
            client_count = sum(1 for user in users if user[1] == 'client')
            tech_count = sum(1 for user in users if user[1] == 'technician')
            
            self.info_label.config(
                text=f"Total Users: {user_count} | Clients: {client_count} | Technicians: {tech_count}"
            )
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load users: {str(e)}")

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
        
    def on_user_double_click(self, event):
        """Handle double-click on user row."""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            username = item['values'][0]
            self.show_user_details(username)
            
    def show_user_details(self, username):
        """Show detailed user information."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT username, role, password, salt, created_at 
                FROM users WHERE username = ?
            ''', (username,))
            
            user = cursor.fetchone()
            conn.close()
            
            if user:
                # Create details window
                details_window = tk.Toplevel(self.root)
                details_window.title(f"User Details - {username}")
                details_window.geometry("500x400")
                details_window.configure(bg=self.colors['secondary'])
                details_window.transient(self.root)
                details_window.grab_set()
                
                # Center window
                details_window.update_idletasks()
                x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (500 // 2)
                y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (400 // 2)
                details_window.geometry(f"500x400+{x}+{y}")
                
                # Content
                content_frame = tk.Frame(details_window, bg=self.colors['secondary'])
                content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
                
                tk.Label(
                    content_frame,
                    text=f"👤 {username}",
                    font=('Segoe UI', 18, 'bold'),
                    fg=self.colors['text_light'],
                    bg=self.colors['secondary']
                ).pack(pady=(0, 20))
                
                # Details
                details = [
                    ("Role:", user[1].title()),
                    ("Created:", user[4] if user[4] else "Unknown"),
                    ("Password Hash:", user[2]),
                    ("Salt:", user[3] if user[3] else "No Salt")
                ]
                
                for label, value in details:
                    detail_frame = tk.Frame(content_frame, bg=self.colors['secondary'])
                    detail_frame.pack(fill=tk.X, pady=5)
                    
                    tk.Label(
                        detail_frame,
                        text=label,
                        font=('Segoe UI', 11, 'bold'),
                        fg=self.colors['text_light'],
                        bg=self.colors['secondary']
                    ).pack(anchor='w')
                    
                    if "Hash" in label:
                        # Scrollable text for hash
                        text_frame = tk.Frame(detail_frame, bg=self.colors['input_bg'])
                        text_frame.pack(fill=tk.X, pady=(5, 0))
                        
                        text_widget = tk.Text(
                            text_frame,
                            height=3,
                            font=('Consolas', 9),
                            bg=self.colors['input_bg'],
                            fg=self.colors['text_light'],
                            wrap=tk.WORD,
                            relief='flat'
                        )
                        text_widget.pack(fill=tk.X, padx=5, pady=5)
                        text_widget.insert("1.0", value)
                        text_widget.configure(state='disabled')
                    else:
                        tk.Label(
                            detail_frame,
                            text=value,
                            font=('Segoe UI', 10),
                            fg=self.colors['text_secondary'],
                            bg=self.colors['secondary']
                        ).pack(anchor='w', padx=20)
                
                # Close button
                tk.Button(
                    content_frame,
                    text="Close",
                    command=details_window.destroy,
                    font=('Segoe UI', 11, 'bold'),
                    bg=self.colors['accent'],
                    fg=self.colors['text_light'],
                    relief='flat',
                    padx=30,
                    pady=10,
                    cursor='hand2'
                ).pack(pady=20)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load user details: {str(e)}")
            
    def add_user(self):
        """Add a new user."""
        # Create add user dialog
        add_window = tk.Toplevel(self.root)
        add_window.title("Add New User")
        add_window.geometry("400x350")
        add_window.configure(bg=self.colors['secondary'])
        add_window.transient(self.root)
        add_window.grab_set()
        
        # Center window
        add_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (400 // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (350 // 2)
        add_window.geometry(f"400x350+{x}+{y}")
        
        # Content
        content_frame = tk.Frame(add_window, bg=self.colors['secondary'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        tk.Label(
            content_frame,
            text="➕ Add New User",
            font=('Segoe UI', 16, 'bold'),
            fg=self.colors['text_light'],
            bg=self.colors['secondary']
        ).pack(pady=(0, 20))
        
        # Username field
        tk.Label(
            content_frame,
            text="Username:",
            font=('Segoe UI', 11, 'bold'),
            fg=self.colors['text_light'],
            bg=self.colors['secondary']
        ).pack(anchor='w', pady=(0, 5))
        
        username_entry = tk.Entry(
            content_frame,
            font=('Segoe UI', 11),
            bg=self.colors['input_bg'],
            fg=self.colors['text_light'],
            relief='flat',
            insertbackground=self.colors['text_light']
        )
        username_entry.pack(fill=tk.X, pady=(0, 15), ipady=8)
        
        # Password field
        tk.Label(
            content_frame,
            text="Password:",
            font=('Segoe UI', 11, 'bold'),
            fg=self.colors['text_light'],
            bg=self.colors['secondary']
        ).pack(anchor='w', pady=(0, 5))
        
        password_entry = tk.Entry(
            content_frame,
            font=('Segoe UI', 11),
            bg=self.colors['input_bg'],
            fg=self.colors['text_light'],
            relief='flat',
            show='*',
            insertbackground=self.colors['text_light']
        )
        password_entry.pack(fill=tk.X, pady=(0, 15), ipady=8)
        
        # Role selection
        tk.Label(
            content_frame,
            text="Role:",
            font=('Segoe UI', 11, 'bold'),
            fg=self.colors['text_light'],
            bg=self.colors['secondary']
        ).pack(anchor='w', pady=(0, 5))
        
        role_var = tk.StringVar(value="client")
        role_frame = tk.Frame(content_frame, bg=self.colors['secondary'])
        role_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Radiobutton(
            role_frame,
            text="Client",
            variable=role_var,
            value="client",
            font=('Segoe UI', 10),
            fg=self.colors['text_light'],
            bg=self.colors['secondary'],
            selectcolor=self.colors['accent'],
            activebackground=self.colors['secondary'],
            activeforeground=self.colors['text_light']
        ).pack(side=tk.LEFT, padx=(0, 20))
        
        tk.Radiobutton(
            role_frame,
            text="Technician",
            variable=role_var,
            value="technician",
            font=('Segoe UI', 10),
            fg=self.colors['text_light'],
            bg=self.colors['secondary'],
            selectcolor=self.colors['accent'],
            activebackground=self.colors['secondary'],
            activeforeground=self.colors['text_light']
        ).pack(side=tk.LEFT)
        
        # Buttons
        button_frame = tk.Frame(content_frame, bg=self.colors['secondary'])
        button_frame.pack(fill=tk.X, pady=10)
        
        def create_user():
            username = username_entry.get().strip()
            password = password_entry.get()
            role = role_var.get()
            
            if not username or not password:
                messagebox.showerror("Error", "Please fill in all fields!")
                return
            
            # Validate username length
            if len(username) < 3:
                messagebox.showerror("Error", "Username must be at least 3 characters!")
                return
                
            # Validate password strength
            password_issues = self.validate_password_strength(password)
            if password_issues:
                error_msg = "Password must meet the following requirements:\n\n" + "\n".join(f"• {issue}" for issue in password_issues)
                messagebox.showerror("Password Requirements", error_msg)
                return
                
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Check if user exists
                cursor.execute('SELECT username FROM users WHERE username = ?', (username,))
                if cursor.fetchone():
                    messagebox.showerror("Error", "Username already exists!")
                    conn.close()
                    return
                
                # Create user with salt
                salt = secrets.token_hex(32)
                salted_password = password + salt
                password_hash = hashlib.sha256(salted_password.encode('utf-8')).hexdigest()
                cursor.execute('''
                    INSERT INTO users (username, password, salt, role) 
                    VALUES (?, ?, ?, ?)
                ''', (username, password_hash, salt, role))
                
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Success", f"User '{username}' created successfully!")
                add_window.destroy()
                self.load_users()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create user: {str(e)}")
        
        tk.Button(
            button_frame,
            text="Create User",
            command=create_user,
            font=('Segoe UI', 11, 'bold'),
            bg=self.colors['success'],
            fg=self.colors['text_light'],
            relief='flat',
            padx=20,
            pady=8,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(
            button_frame,
            text="Cancel",
            command=add_window.destroy,
            font=('Segoe UI', 11, 'bold'),
            bg=self.colors['error'],
            fg=self.colors['text_light'],
            relief='flat',
            padx=20,
            pady=8,
            cursor='hand2'
        ).pack(side=tk.LEFT)
        
        # Focus username field
        username_entry.focus()
        
    def delete_user(self):
        """Delete selected user."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a user to delete!")
            return
            
        item = self.tree.item(selection[0])
        username = item['values'][0]
        
        # Confirm deletion
        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete user '{username}'?\n\nThis action cannot be undone!"):
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('DELETE FROM users WHERE username = ?', (username,))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    messagebox.showinfo("Success", f"User '{username}' deleted successfully!")
                    self.load_users()
                else:
                    messagebox.showerror("Error", "User not found!")
                    
                conn.close()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete user: {str(e)}")
                
    def reset_password(self):
        """Reset password for selected user."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a user to reset password!")
            return
            
        item = self.tree.item(selection[0])
        username = item['values'][0]
        
        # Get new password
        new_password = simpledialog.askstring(
            "Reset Password",
            f"Enter new password for '{username}':",
            show='*'
        )
        
        if new_password:
            # Validate password strength
            password_issues = self.validate_password_strength(new_password)
            if password_issues:
                error_msg = "Password must meet the following requirements:\n\n" + "\n".join(f"• {issue}" for issue in password_issues)
                messagebox.showerror("Password Requirements", error_msg)
                return
                
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Generate new salt and hash
                salt = secrets.token_hex(32)
                salted_password = new_password + salt
                password_hash = hashlib.sha256(salted_password.encode('utf-8')).hexdigest()
                cursor.execute(
                    'UPDATE users SET password = ?, salt = ? WHERE username = ?',
                    (password_hash, salt, username)
                )
                
                if cursor.rowcount > 0:
                    conn.commit()
                    messagebox.showinfo("Success", f"Password reset for '{username}' successfully!")
                    self.load_users()
                else:
                    messagebox.showerror("Error", "User not found!")
                    
                conn.close()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to reset password: {str(e)}")
                
    def on_close(self):
        """Handle window close."""
        self.root.destroy()
        
    def run(self):
        """Run the admin panel."""
        self.root.mainloop()

def main():
    if not authenticate_admin():
        # Show access denied message and exit
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        messagebox.showerror(
            "Access Denied", 
            "Admin authentication failed!\nAccess to the admin panel is denied."
        )
        root.destroy()
        return
    
    try:
        # Check if database exists
        import os
        if not os.path.exists("users.db"):
            messagebox.showerror(
                "Database Not Found", 
                "users.db not found!\nPlease run the login system first to create the database."
            )
            return
            
        app = AdminPanel()
        app.run()
    except Exception as e:
        print(f"Error: {e}")
        messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    main() 