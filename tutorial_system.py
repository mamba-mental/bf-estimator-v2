#!/usr/bin/env python
# tutorial_system.py - Interactive tutorial and guidance system
# Created: 03/27/25

import tkinter as tk
import customtkinter as ctk
import time

class TutorialTooltip(ctk.CTkToplevel):
    """Custom tooltip widget for the tutorial system."""
    
    def __init__(self, master, text, target_widget=None, position="auto", width=250, height=None,
                 callback=None, next_text="Next", close_text="Got it", arrow_position=None):
        """
        Initialize the tooltip.
        
        Args:
            master: Parent window
            text: Text to display
            target_widget: Widget this tooltip is associated with (for positioning)
            position: Where to position relative to target ("top", "bottom", "left", "right", "auto")
            width: Width of tooltip
            height: Height of tooltip (None for auto)
            callback: Function to call when "Next" or "Got it" is clicked
            next_text: Text for the next button
            close_text: Text for the close button
            arrow_position: Where to place the arrow if not auto ("n", "s", "e", "w")
        """
        super().__init__(master)
        
        # Remove window decorations
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        
        # Store parameters
        self.master = master
        self.target_widget = target_widget
        self.position = position
        self.callback = callback
        self.arrow_position = arrow_position
        
        # Configure window appearance
        self.configure(fg_color="#FF9C5E")  # Orange highlight color
        self.title("Tooltip")
        
        # Set size
        self.width = width
        self.height = height if height else self._calculate_height(text)
        
        # Create content frame with slight margin
        self.content_frame = ctk.CTkFrame(self, fg_color="#FF9C5E", corner_radius=8)
        self.content_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Add text
        self.text_label = ctk.CTkLabel(
            self.content_frame, 
            text=text,
            wraplength=width - 20,
            text_color="#ffffff",  # White text
            justify="left",
            font=("Roboto", 12)
        )
        self.text_label.pack(padx=10, pady=(10, 5), fill="both", expand=True)
        
        # Add buttons
        self.button_frame = ctk.CTkFrame(self.content_frame, fg_color="#FF9C5E")
        self.button_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Next or close button
        if next_text:
            self.next_button = ctk.CTkButton(
                self.button_frame,
                text=next_text,
                command=self._on_next,
                fg_color="#ffffff",
                text_color="#FF9C5E",
                hover_color="#f0f0f0",
                width=80,
                height=30
            )
            self.next_button.pack(side="right", padx=5)
        
        if close_text:
            self.close_button = ctk.CTkButton(
                self.button_frame,
                text=close_text,
                command=self._on_close,
                fg_color="#ffffff",
                text_color="#FF9C5E",
                hover_color="#f0f0f0",
                width=80,
                height=30
            )
            self.close_button.pack(side="right", padx=5)
        
        # Position the tooltip
        self.update_idletasks()  # Ensure the window size is calculated
        if target_widget:
            self.position_near_widget(target_widget, position)
        else:
            # Center on screen
            screen_width = self.master.winfo_screenwidth()
            screen_height = self.master.winfo_screenheight()
            x = (screen_width - self.width) // 2
            y = (screen_height - self.height) // 2
            self.geometry(f"{self.width}x{self.height}+{x}+{y}")
        
        # Add arrow if needed
        if target_widget and not self.arrow_position:
            self._add_arrow()
        elif self.arrow_position:
            self._add_arrow(self.arrow_position)
        
        # Make sure window renders on top
        self.lift()
        self.attributes("-topmost", True)
        
        # Bind events
        self.bind("<Escape>", lambda e: self._on_close())
    
    def _calculate_height(self, text):
        """Calculate an appropriate height based on text length."""
        lines = len(text) // 30 + text.count('\n') + 2  # Rough estimate of lines
        return max(80, lines * 20 + 60)  # Base height + line height * lines
    
    def position_near_widget(self, widget, position="auto"):
        """Position the tooltip near the target widget."""
        # Get widget position relative to screen
        if widget.winfo_ismapped():
            x = widget.winfo_rootx()
            y = widget.winfo_rooty()
            w = widget.winfo_width()
            h = widget.winfo_height()
        else:
            # Widget not mapped, use default positioning
            screen_width = self.master.winfo_screenwidth()
            screen_height = self.master.winfo_screenheight()
            x = screen_width // 2 - self.width // 2
            y = screen_height // 2 - self.height // 2
            self.geometry(f"{self.width}x{self.height}+{x}+{y}")
            return
        
        # Get screen dimensions
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        
        # Calculate tooltip dimensions
        tooltip_width = self.width
        tooltip_height = self.height
        
        # Determine best position if auto
        if position == "auto":
            # Check space in each direction
            space_above = y
            space_below = screen_height - (y + h)
            space_left = x
            space_right = screen_width - (x + w)
            
            # Find direction with most space
            spaces = [
                ("bottom", space_below),
                ("top", space_above),
                ("right", space_right),
                ("left", space_left)
            ]
            position = max(spaces, key=lambda s: s[1])[0]
        
        # Position based on chosen direction
        if position == "bottom":
            x = x + w // 2 - tooltip_width // 2
            y = y + h + 10
            self.arrow_position = "n"
        elif position == "top":
            x = x + w // 2 - tooltip_width // 2
            y = y - tooltip_height - 10
            self.arrow_position = "s"
        elif position == "left":
            x = x - tooltip_width - 10
            y = y + h // 2 - tooltip_height // 2
            self.arrow_position = "e"
        elif position == "right":
            x = x + w + 10
            y = y + h // 2 - tooltip_height // 2
            self.arrow_position = "w"
        
        # Ensure tooltip stays within screen bounds
        x = max(10, min(x, screen_width - tooltip_width - 10))
        y = max(10, min(y, screen_height - tooltip_height - 10))
        
        # Set geometry
        self.geometry(f"{tooltip_width}x{tooltip_height}+{x}+{y}")
    
    def _add_arrow(self, position=None):
        """Add a directional arrow to the tooltip."""
        # This is a simplified version - for a real app, you might want to 
        # create actual arrow shapes using a canvas
        position = position or self.arrow_position
        if not position:
            return
        
        arrow_text = {
            "n": "▲",  # North - arrow pointing up
            "s": "▼",  # South - arrow pointing down
            "e": "►",  # East - arrow pointing right
            "w": "◄"   # West - arrow pointing left
        }.get(position, "")
        
        if not arrow_text:
            return
        
        # Create arrow label
        arrow = ctk.CTkLabel(
            self,
            text=arrow_text,
            text_color="#FF9C5E",
            font=("Arial", 16, "bold")
        )
        
        # Position it
        if position == "n":
            arrow.place(relx=0.5, rely=0, anchor="n")
        elif position == "s":
            arrow.place(relx=0.5, rely=1, anchor="s")
        elif position == "e":
            arrow.place(relx=1, rely=0.5, anchor="e")
        elif position == "w":
            arrow.place(relx=0, rely=0.5, anchor="w")
    
    def _on_next(self):
        """Handle click on the Next button."""
        self.destroy()
        if self.callback:
            self.callback(True)  # True indicates "next" was clicked
    
    def _on_close(self):
        """Handle click on the Close button or Escape key."""
        self.destroy()
        if self.callback:
            self.callback(False)  # False indicates "close" was clicked

class TutorialSystem:
    """System to provide interactive tutorials for application features."""
    
    def __init__(self, app, callback=None):
        """
        Initialize the tutorial system.
        
        Args:
            app: The main application instance
            callback: Function to call when tutorial completes or is dismissed
        """
        self.app = app
        self.callback = callback
        self.current_step = 0
        self.steps = []
        self.active_tooltip = None
        self.is_running = False
    
    def start_tutorial(self, tutorial_steps):
        """
        Start a tutorial sequence.
        
        Args:
            tutorial_steps: List of tutorial step dictionaries, each with:
                - text: The tooltip text
                - target: Widget or widget path to highlight (optional)
                - position: Position relative to target (optional)
                - delay: Delay before showing this step in milliseconds (optional)
                - highlight: Whether to highlight the target (optional)
        """
        if self.is_running:
            return
        
        self.steps = tutorial_steps
        self.current_step = 0
        self.is_running = True
        
        # Start the first step after a short delay
        self.app.after(100, self.show_current_step)
    
    def show_current_step(self):
        """Show the current tutorial step."""
        if not self.is_running or self.current_step >= len(self.steps):
            self.complete_tutorial()
            return
        
        # Get current step
        step = self.steps[self.current_step]
        
        # Get target widget if specified
        target_widget = None
        if 'target' in step:
            if isinstance(step['target'], str):
                # Target is a widget path
                try:
                    target_widget = self.app.nametowidget(step['target'])
                except KeyError:
                    print(f"Warning: Widget {step['target']} not found")
            else:
                # Target is a widget reference
                target_widget = step['target']
        
        # If there's a delay, wait before showing tooltip
        delay = step.get('delay', 0)
        if delay > 0:
            self.app.after(delay, lambda: self._show_step_tooltip(step, target_widget))
        else:
            self._show_step_tooltip(step, target_widget)
    
    def _show_step_tooltip(self, step, target_widget):
        """Show the tooltip for the current step."""
        if not self.is_running:
            return
        
        # Determine button text based on whether this is the last step
        is_last_step = self.current_step == len(self.steps) - 1
        next_text = "Finish" if is_last_step else "Next"
        
        # Create tooltip
        self.active_tooltip = TutorialTooltip(
            self.app,
            text=step['text'],
            target_widget=target_widget,
            position=step.get('position', 'auto'),
            width=step.get('width', 250),
            height=step.get('height', None),
            next_text=next_text,
            close_text="Skip" if not is_last_step else "Close",
            callback=self._handle_step_completion
        )
        
        # Highlight target if requested
        if target_widget and step.get('highlight', False):
            self._highlight_widget(target_widget)
    
    def _highlight_widget(self, widget):
        """Highlight a widget temporarily."""
        # Save original appearance
        original_fg = widget.cget("fg_color") if hasattr(widget, "cget") else None
        
        # Apply highlight
        if hasattr(widget, "configure") and hasattr(widget, "cget"):
            widget.configure(fg_color="#FF9C5E")  # Orange highlight
            
            # Restore original appearance after a delay
            self.app.after(5000, lambda: widget.configure(fg_color=original_fg))
    
    def _handle_step_completion(self, continue_tutorial):
        """Handle completion of the current tutorial step."""
        self.active_tooltip = None
        
        if continue_tutorial:
            # Move to next step
            self.current_step += 1
            if self.current_step < len(self.steps):
                self.show_current_step()
            else:
                self.complete_tutorial()
        else:
            # User clicked Skip/Close, end tutorial
            self.complete_tutorial(completed=False)
    
    def complete_tutorial(self, completed=True):
        """Complete or cancel the tutorial."""
        self.is_running = False
        self.steps = []
        self.current_step = 0
        
        if self.active_tooltip:
            self.active_tooltip.destroy()
            self.active_tooltip = None
        
        if self.callback:
            self.callback(completed)

def create_welcome_tutorial(app):
    """Create a tutorial for welcoming new users to the application."""
    # Define the tutorial steps
    welcome_steps = [
        {
            'text': "Welcome to the Enhanced Body Fat Estimator! This tutorial will guide you through the main features of the application.",
            'position': 'auto',
            'width': 350
        },
        {
            'text': "The Dashboard tab shows your progress at a glance with customizable widgets that you can drag and arrange.",
            'target': app.dashboard_tab if hasattr(app, 'dashboard_tab') else None,
            'position': 'bottom',
            'width': 350,
            'delay': 500
        },
        {
            'text': "The Edit Dashboard button allows you to customize your dashboard layout. Try it out after this tutorial!",
            'target': app.edit_button if hasattr(app, 'edit_button') else None,
            'position': 'bottom',
            'width': 300,
            'delay': 500
        },
        {
            'text': "This tab is where you'll enter your weekly measurements and body composition data.",
            'target': app.input_tab if hasattr(app, 'input_tab') else None,
            'position': 'bottom',
            'width': 350,
            'delay': 500
        },
        {
            'text': "Use the Settings tab to set your personal information, goals, and appearance preferences.",
            'target': app.settings_tab if hasattr(app, 'settings_tab') else None,
            'position': 'bottom',
            'width': 350,
            'delay': 500
        },
        {
            'text': "Need to speak your measurements? Click the microphone button to use voice input!",
            'target': app.voice_input_button if hasattr(app, 'voice_input_button') else None,
            'position': 'left',
            'width': 300,
            'delay': 500
        },
        {
            'text': "That's it! You're ready to start tracking your fitness journey. If you need help at any time, check the About tab for more information.",
            'position': 'auto',
            'width': 350
        }
    ]
    
    return welcome_steps

def show_welcome_tutorial(app, on_complete=None):
    """Show the welcome tutorial for new users."""
    # Create tutorial steps
    welcome_steps = create_welcome_tutorial(app)
    
    # Create and start tutorial
    tutorial = TutorialSystem(app, callback=on_complete)
    tutorial.start_tutorial(welcome_steps)
    
    return tutorial

def create_feature_tutorial(app, feature):
    """Create a tutorial for specific features."""
    if feature == "dashboard":
        return [
            {
                'text': "The Dashboard provides a quick overview of your progress.",
                'target': app.dashboard_tab if hasattr(app, 'dashboard_tab') else None,
                'position': 'bottom',
                'width': 300
            },
            {
                'text': "Click 'Edit Dashboard' to rearrange widgets by dragging them.",
                'target': app.edit_button if hasattr(app, 'edit_button') else None,
                'position': 'bottom',
                'width': 300,
                'delay': 500
            },
            {
                'text': "When in edit mode, drag widgets by their title bars to position them.",
                'target': app.dashboard_widgets["weight"].title_bar if hasattr(app, 'dashboard_widgets') and "weight" in app.dashboard_widgets else None,
                'position': 'bottom',
                'width': 300,
                'delay': 500,
                'highlight': True
            },
            {
                'text': "Click 'Save Layout' when you're happy with your dashboard arrangement.",
                'position': 'auto',
                'width': 300
            }
        ]
    elif feature == "voice_input":
        return [
            {
                'text': "Voice Input allows you to speak your measurements instead of typing them.",
                'target': app.voice_input_button if hasattr(app, 'voice_input_button') else None,
                'position': 'left',
                'width': 300
            },
            {
                'text': "Try saying phrases like 'Weight 180 pounds' or 'Body fat 15 percent'.",
                'position': 'auto',
                'width': 300,
                'delay': 500
            },
            {
                'text': "You can also record measurements like 'Waist 32 inches' or 'Arms 16 inches'.",
                'position': 'auto',
                'width': 300,
                'delay': 500
            }
        ]
    elif feature == "measurements":
        return [
            {
                'text': "The Additional Measurements section allows you to track multiple body parts.",
                'target': app.measurements_section if hasattr(app, 'measurements_section') else None,
                'position': 'left',
                'width': 300
            },
            {
                'text': "Enter values for different body parts to track your body composition in detail.",
                'target': app.measurements_entry_frame if hasattr(app, 'measurements_entry_frame') else None,
                'position': 'top',
                'width': 300,
                'delay': 500
            },
            {
                'text': "Click 'Add Custom Measurement' to track additional body parts not listed by default.",
                'target': app.custom_measurement_button if hasattr(app, 'custom_measurement_button') else None,
                'position': 'top',
                'width': 300,
                'delay': 500
            }
        ]
    else:
        # Default generic tutorial
        return [
            {
                'text': f"Welcome to the {feature} feature tutorial.",
                'position': 'auto',
                'width': 300
            },
            {
                'text': "This feature helps you track and visualize your fitness progress.",
                'position': 'auto',
                'width': 300,
                'delay': 1000
            },
            {
                'text': "Explore the interface to learn more about how to use this feature.",
                'position': 'auto',
                'width': 300,
                'delay': 1000
            }
        ]

def show_feature_tutorial(app, feature, on_complete=None):
    """Show a tutorial for a specific feature."""
    feature_steps = create_feature_tutorial(app, feature)
    
    tutorial = TutorialSystem(app, callback=on_complete)
    tutorial.start_tutorial(feature_steps)
    
    return tutorial

# Test the tutorial system when run directly
if __name__ == "__main__":
    app = ctk.CTk()
    app.title("Tutorial System Test")
    app.geometry("800x600")
    
    # Create some widgets to target in the tutorial
    frame = ctk.CTkFrame(app)
    frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    label = ctk.CTkLabel(frame, text="This is a test widget")
    label.pack(pady=20)
    
    button = ctk.CTkButton(frame, text="Test Button")
    button.pack(pady=20)
    
    # Define a test tutorial
    test_steps = [
        {
            'text': "Welcome to the tutorial system test!",
            'position': 'auto',
            'width': 300
        },
        {
            'text': "This tooltip is attached to a label widget.",
            'target': label,
            'position': 'bottom',
            'width': 300,
            'delay': 500
        },
        {
            'text': "This tooltip is attached to a button widget.",
            'target': button,
            'position': 'top',
            'width': 300,
            'delay': 500,
            'highlight': True
        },
        {
            'text': "Tutorial complete! You can now use the tutorial system in your application.",
            'position': 'auto',
            'width': 350
        }
    ]
    
    # Start the tutorial after a short delay
    app.after(1000, lambda: TutorialSystem(app).start_tutorial(test_steps))
    
    app.mainloop()
