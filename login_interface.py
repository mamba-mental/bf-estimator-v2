#!/usr/bin/env python
# login_interface.py - Login and registration interface
# Created: 03/27/25

import os
import tkinter as tk
import customtkinter as ctk
from user_auth import UserAuth
from theme_manager import ThemeManager

class LoginInterface(ctk.CTkFrame):
    def __init__(self, parent, on_login_success=None, on_cancel=None):
        super().__init__(parent)
        self.parent = parent
        self.on_login_success = on_login_success
        self.on_cancel = on_cancel
        
        self.auth = UserAuth()
        self.theme_manager = ThemeManager(parent)
        
        # Apply default theme
        self.theme_manager.apply_theme("enhanced_blue")
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the login interface UI."""
        # Configure the grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create a frame to hold the login form
        self.login_frame = ctk.CTkFrame(self)
        self.login_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        # Configure the login frame grid
        self.login_frame.grid_columnconfigure(0, weight=1)
        self.login_frame.grid_columnconfigure(1, weight=1)
        
        # Title label
        self.title_label = ctk.CTkLabel(
            self.login_frame, 
            text="Body Fat Estimator", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(20, 5), sticky="ew")
        
        # Subtitle label
        self.subtitle_label = ctk.CTkLabel(
            self.login_frame, 
            text="Login to your account", 
            font=ctk.CTkFont(size=14)
        )
        self.subtitle_label.grid(row=1, column=0, columnspan=2, pady=(0, 20), sticky="ew")
        
        # Username field
        self.username_label = ctk.CTkLabel(self.login_frame, text="Username:")
        self.username_label.grid(row=2, column=0, padx=10, pady=(10, 0), sticky="w")
        
        self.username_entry = ctk.CTkEntry(self.login_frame, width=200)
        self.username_entry.grid(row=2, column=1, padx=10, pady=(10, 0), sticky="ew")
        
        # Password field
        self.password_label = ctk.CTkLabel(self.login_frame, text="Password:")
        self.password_label.grid(row=3, column=0, padx=10, pady=(10, 0), sticky="w")
        
        self.password_entry = ctk.CTkEntry(self.login_frame, width=200, show="*")
        self.password_entry.grid(row=3, column=1, padx=10, pady=(10, 0), sticky="ew")
        
        # Remember me checkbox
        self.remember_var = ctk.BooleanVar(value=False)
        self.remember_checkbox = ctk.CTkCheckBox(
            self.login_frame, 
            text="Remember me", 
            variable=self.remember_var
        )
        self.remember_checkbox.grid(row=4, column=0, columnspan=2, padx=10, pady=(10, 0), sticky="w")
        
        # Login button
        self.login_button = ctk.CTkButton(
            self.login_frame, 
            text="Login", 
            command=self.login
        )
        self.login_button.grid(row=5, column=0, padx=10, pady=(20, 10), sticky="ew")
        
        # Register button
        self.register_button = ctk.CTkButton(
            self.login_frame, 
            text="Register", 
            command=self.show_register_form,
            fg_color="transparent",
            border_width=2
        )
        self.register_button.grid(row=5, column=1, padx=10, pady=(20, 10), sticky="ew")
        
        # Skip login button (for development)
        self.skip_button = ctk.CTkButton(
            self.login_frame, 
            text="Guest Mode", 
            command=self.skip_login,
            fg_color="gray",
            hover_color="#555555"
        )
        self.skip_button.grid(row=6, column=0, columnspan=2, padx=10, pady=(5, 20), sticky="ew")
        
        # Error message label
        self.error_label = ctk.CTkLabel(
            self.login_frame, 
            text="", 
            text_color="red"
        )
        self.error_label.grid(row=7, column=0, columnspan=2, padx=10, pady=(0, 20), sticky="ew")
        
        # Register frame (initially hidden)
        self.register_frame = ctk.CTkFrame(self)
        
        # Configure the login frame grid
        self.register_frame.grid_columnconfigure(0, weight=1)
        self.register_frame.grid_columnconfigure(1, weight=1)
        
        # Register form title
        self.register_title = ctk.CTkLabel(
            self.register_frame, 
            text="Create an Account", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.register_title.grid(row=0, column=0, columnspan=2, pady=(20, 5), sticky="ew")
        
        # Register username field
        self.reg_username_label = ctk.CTkLabel(self.register_frame, text="Username:")
        self.reg_username_label.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="w")
        
        self.reg_username_entry = ctk.CTkEntry(self.register_frame, width=200)
        self.reg_username_entry.grid(row=1, column=1, padx=10, pady=(10, 0), sticky="ew")
        
        # Register password field
        self.reg_password_label = ctk.CTkLabel(self.register_frame, text="Password:")
        self.reg_password_label.grid(row=2, column=0, padx=10, pady=(10, 0), sticky="w")
        
        self.reg_password_entry = ctk.CTkEntry(self.register_frame, width=200, show="*")
        self.reg_password_entry.grid(row=2, column=1, padx=10, pady=(10, 0), sticky="ew")
        
        # Confirm password field
        self.confirm_password_label = ctk.CTkLabel(self.register_frame, text="Confirm Password:")
        self.confirm_password_label.grid(row=3, column=0, padx=10, pady=(10, 0), sticky="w")
        
        self.confirm_password_entry = ctk.CTkEntry(self.register_frame, width=200, show="*")
        self.confirm_password_entry.grid(row=3, column=1, padx=10, pady=(10, 0), sticky="ew")
        
        # Email field (optional)
        self.email_label = ctk.CTkLabel(self.register_frame, text="Email (optional):")
        self.email_label.grid(row=4, column=0, padx=10, pady=(10, 0), sticky="w")
        
        self.email_entry = ctk.CTkEntry(self.register_frame, width=200)
        self.email_entry.grid(row=4, column=1, padx=10, pady=(10, 0), sticky="ew")
        
        # Create account button
        self.create_account_button = ctk.CTkButton(
            self.register_frame, 
            text="Create Account", 
            command=self.register
        )
        self.create_account_button.grid(row=5, column=0, padx=10, pady=(20, 10), sticky="ew")
        
        # Back button
        self.back_button = ctk.CTkButton(
            self.register_frame, 
            text="Back to Login", 
            command=self.show_login_form,
            fg_color="transparent",
            border_width=2
        )
        self.back_button.grid(row=5, column=1, padx=10, pady=(20, 10), sticky="ew")
        
        # Register error message label
        self.register_error_label = ctk.CTkLabel(
            self.register_frame, 
            text="", 
            text_color="red"
        )
        self.register_error_label.grid(row=6, column=0, columnspan=2, padx=10, pady=(0, 20), sticky="ew")
    
    def login(self):
        """Handle login button click."""
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            self.error_label.configure(text="Please enter username and password")
            return
        
        success, message = self.auth.login(username, password)
        
        if success:
            if self.on_login_success:
                # Call the success callback. The callback handler (in create_login_window)
                # will be responsible for destroying the window if necessary.
                self.on_login_success(self.auth)
        else:
            self.error_label.configure(text=message)
    
    def register(self):
        """Handle register button click."""
        username = self.reg_username_entry.get()
        password = self.reg_password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        email = self.email_entry.get()
        
        if not username or not password or not confirm_password:
            self.register_error_label.configure(text="Please fill all required fields")
            return
        
        if password != confirm_password:
            self.register_error_label.configure(text="Passwords do not match")
            return
        
        if len(password) < 6:
            self.register_error_label.configure(text="Password must be at least 6 characters")
            return
        
        # Email is optional, pass None if empty
        email_to_pass = email if email else None
        
        success, message = self.auth.register_user(username, password, email_to_pass)
        
        if success:
            self.show_login_form()
            self.username_entry.delete(0, 'end')
            self.username_entry.insert(0, username)
            self.password_entry.delete(0, 'end')
            self.error_label.configure(text="Registration successful! You can now login.")
        else:
            self.register_error_label.configure(text=message)
    
    def show_register_form(self):
        """Show the registration form."""
        self.login_frame.grid_forget()
        self.register_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        # Clear existing entries
        self.reg_username_entry.delete(0, 'end')
        self.reg_password_entry.delete(0, 'end')
        self.confirm_password_entry.delete(0, 'end')
        self.email_entry.delete(0, 'end')
        self.register_error_label.configure(text="")
    
    def show_login_form(self):
        """Show the login form."""
        self.register_frame.grid_forget()
        self.login_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
    
    def skip_login(self):
        """Skip login for development purposes."""
        if self.on_login_success:
            self.on_login_success(None)
        
def create_login_window(on_login_success=None, on_cancel=None):
    """Create a standalone login window."""
    login_window = ctk.CTk()
    login_window.title("Body Fat Estimator - Login")
    login_window.geometry("400x500")
    login_window.resizable(False, False)
    
    # Configure the grid
    login_window.grid_columnconfigure(0, weight=1)
    login_window.grid_rowconfigure(0, weight=1)
    
    def handle_login_success(auth):
        """Handle login success in the standalone window."""
        # Call the original callback first
        if on_login_success:
            on_login_success(auth)
        # Schedule the window destruction shortly after
        login_window.after(50, login_window.destroy)
    
    def handle_cancel():
        """Handle cancel in the standalone window."""
        login_window.destroy()
        if on_cancel:
            on_cancel()
    
    login_interface = LoginInterface(
        login_window,
        on_login_success=handle_login_success,
        on_cancel=handle_cancel
    )
    login_interface.grid(row=0, column=0, sticky="nsew")
    
    login_window.mainloop()
    
if __name__ == "__main__":
    # Test the login interface
    create_login_window()
