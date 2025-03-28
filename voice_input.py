#!/usr/bin/env python
# voice_input.py - Voice recognition for data entry
# Created: 03/27/25

import tkinter as tk
import speech_recognition as sr
import threading
import re
import datetime
from tkinter import messagebox
import customtkinter as ctk

class VoiceInputDialog:
    """Dialog for voice input of fitness data."""
    
    def __init__(self, parent):
        """Initialize the voice input dialog."""
        self.parent = parent
        self.result = None
        self.recognizer = sr.Recognizer()
        self.microphone = None
        
        # Try to initialize microphone
        try:
            self.microphone = sr.Microphone()
            # Calibrate for ambient noise
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
        except (sr.RequestError, sr.UnknownValueError, OSError) as e:
            messagebox.showerror("Microphone Error", f"Could not initialize microphone: {e}")
        
        # Create dialog window
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("Voice Input")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)  # Make dialog modal
        self.dialog.grab_set()
        
        # Center the dialog on parent
        if parent:
            x = parent.winfo_x() + (parent.winfo_width() // 2) - (500 // 2)
            y = parent.winfo_y() + (parent.winfo_height() // 2) - (400 // 2)
            self.dialog.geometry(f"+{x}+{y}")
        
        # Set up UI
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the voice input dialog UI."""
        # Instructions label
        instructions = ctk.CTkLabel(
            self.dialog,
            text="Speak your measurement data clearly.\nExamples:\n'Weight 180 pounds'\n'Body fat 15 percent'\n'Waist 32 inches'\n'Arms 16 inches'",
            font=("Roboto", 14),
            justify="center"
        )
        instructions.pack(pady=(20, 10))
        
        # Recognized text display
        self.text_frame = ctk.CTkFrame(self.dialog)
        self.text_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.recognized_text = ctk.CTkTextbox(self.text_frame, height=150)
        self.recognized_text.pack(fill="both", expand=True, padx=10, pady=10)
        self.recognized_text.insert("1.0", "Recognized text will appear here...")
        
        # Status label
        self.status_label = ctk.CTkLabel(
            self.dialog,
            text="Ready to listen",
            font=("Roboto", 12)
        )
        self.status_label.pack(pady=5)
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=20, pady=20)
        
        # Listen button
        self.listen_button = ctk.CTkButton(
            buttons_frame,
            text="Start Listening",
            command=self.start_listening
        )
        self.listen_button.pack(side="left", padx=10)
        
        # Cancel button
        self.cancel_button = ctk.CTkButton(
            buttons_frame,
            text="Cancel",
            command=self.cancel
        )
        self.cancel_button.pack(side="right", padx=10)
        
        # Accept button
        self.accept_button = ctk.CTkButton(
            buttons_frame,
            text="Accept & Close",
            command=self.accept,
            state="disabled"  # Initially disabled until speech is recognized
        )
        self.accept_button.pack(side="right", padx=10)
        
        # Position buttons properly
        buttons_frame.columnconfigure(0, weight=1)
        buttons_frame.columnconfigure(1, weight=1)
        buttons_frame.columnconfigure(2, weight=1)
        
        # Handle dialog close
        self.dialog.protocol("WM_DELETE_WINDOW", self.cancel)
        
        # Initialize variables
        self.is_listening = False
        self.listen_thread = None
    
    def start_listening(self):
        """Start the voice recognition process."""
        if self.microphone is None:
            messagebox.showerror("Error", "Microphone not available")
            return
            
        if self.is_listening:
            self.stop_listening()
            return
            
        self.is_listening = True
        self.listen_button.configure(text="Stop Listening")
        self.status_label.configure(text="Listening... Speak now")
        
        # Clear previous text
        self.recognized_text.delete("1.0", "end")
        self.recognized_text.insert("1.0", "Listening...")
        
        # Start listening in a separate thread to avoid UI freezing
        self.listen_thread = threading.Thread(target=self._listen)
        self.listen_thread.daemon = True
        self.listen_thread.start()
    
    def stop_listening(self):
        """Stop the voice recognition process."""
        self.is_listening = False
        self.listen_button.configure(text="Start Listening")
        self.status_label.configure(text="Stopped listening")
    
    def _listen(self):
        """Background listening task."""
        try:
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=10.0)
                
            # Indicate processing
            self.dialog.after(0, lambda: self.status_label.configure(text="Processing speech..."))
                
            # Recognize speech
            text = self.recognizer.recognize_google(audio)
            
            # Update UI with recognized text
            self.dialog.after(0, lambda: self._update_recognized_text(text))
            
        except sr.WaitTimeoutError:
            self.dialog.after(0, lambda: self.status_label.configure(text="No speech detected. Try again."))
            self.dialog.after(0, lambda: self.listen_button.configure(text="Start Listening"))
            self.is_listening = False
            
        except sr.UnknownValueError:
            self.dialog.after(0, lambda: self.status_label.configure(text="Could not understand audio. Try again."))
            self.dialog.after(0, lambda: self.listen_button.configure(text="Start Listening"))
            self.is_listening = False
            
        except sr.RequestError as e:
            self.dialog.after(0, lambda: self.status_label.configure(text=f"Error: {e}"))
            self.dialog.after(0, lambda: self.listen_button.configure(text="Start Listening"))
            self.is_listening = False
            
        except Exception as e:
            self.dialog.after(0, lambda: self.status_label.configure(text=f"Error: {e}"))
            self.dialog.after(0, lambda: self.listen_button.configure(text="Start Listening"))
            self.is_listening = False
    
    def _update_recognized_text(self, text):
        """Update the recognized text display and parse the input."""
        self.recognized_text.delete("1.0", "end")
        self.recognized_text.insert("1.0", text)
        
        # Parse the recognized text
        parsed_data = self._parse_speech(text)
        
        # If we have data, enable the accept button
        if parsed_data:
            self.result = parsed_data
            self.accept_button.configure(state="normal")
            
            # Add parsed data display
            self.recognized_text.insert("end", "\n\nParsed data:")
            for key, value in parsed_data.items():
                if key == 'measurements':
                    self.recognized_text.insert("end", f"\n{key}:")
                    for m_type, m_value in value.items():
                        self.recognized_text.insert("end", f"\n  {m_type}: {m_value}")
                else:
                    self.recognized_text.insert("end", f"\n{key}: {value}")
        
        # Reset UI state
        self.status_label.configure(text="Speech recognized. Click Accept or try again.")
        self.listen_button.configure(text="Start Listening")
        self.is_listening = False
    
    def _parse_speech(self, text):
        """Parse the recognized speech to extract fitness data.
        
        Looks for patterns like:
        - "weight (number) pounds"
        - "body fat (number) percent"
        - "(measurement) (number) inches"
        - "date (month) (day) (year)"
        
        Returns:
            dict: Dictionary with the extracted data
        """
        result = {}
        measurements = {}
        
        # Convert text to lowercase for easier matching
        text = text.lower()
        
        # Extract weight
        weight_match = re.search(r'weight\s+(\d+(?:\.\d+)?)', text)
        if weight_match:
            result['weight'] = float(weight_match.group(1))
        
        # Extract body fat percentage
        bf_match = re.search(r'(?:body\s*fat|bf)\s+(\d+(?:\.\d+)?)', text)
        if bf_match:
            result['body_fat'] = float(bf_match.group(1))
        
        # Extract date
        # First check format like "date january 15 2025" or "date 1/15/2025"
        date_word_match = re.search(r'date\s+([a-z]+)\s+(\d+)(?:st|nd|rd|th)?\s+(\d{4})', text)
        date_slash_match = re.search(r'date\s+(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})', text)
        
        if date_word_match:
            month_str = date_word_match.group(1)
            day = int(date_word_match.group(2))
            year = int(date_word_match.group(3))
            
            # Convert month name to number
            months = {
                'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
                'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12
            }
            
            if month_str in months:
                month = months[month_str]
                try:
                    date_obj = datetime.date(year, month, day)
                    result['date'] = date_obj.strftime("%Y-%m-%d")  # Store in ISO format
                except ValueError:
                    pass  # Invalid date
        
        elif date_slash_match:
            try:
                month = int(date_slash_match.group(1))
                day = int(date_slash_match.group(2))
                year = int(date_slash_match.group(3))
                
                # Handle 2-digit years
                if year < 100:
                    year += 2000
                
                date_obj = datetime.date(year, month, day)
                result['date'] = date_obj.strftime("%Y-%m-%d")  # Store in ISO format
            except ValueError:
                pass  # Invalid date
        
        # If no explicit date mentioned, use today
        if 'date' not in result:
            result['date'] = datetime.date.today().strftime("%Y-%m-%d")
        
        # Extract other body measurements
        # Look for patterns like "waist 32 inches" or "arms 16"
        measurement_types = [
            'chest', 'waist', 'hips', 'arm', 'arms', 'thigh', 'thighs', 
            'calf', 'calves', 'neck', 'shoulder', 'shoulders'
        ]
        
        for m_type in measurement_types:
            # Handle plural forms
            search_type = m_type
            if m_type == 'arms':
                search_type = r'(?:arm|arms)'
            elif m_type == 'thighs':
                search_type = r'(?:thigh|thighs)'
            elif m_type == 'calves':
                search_type = r'(?:calf|calves)'
            elif m_type == 'shoulders':
                search_type = r'(?:shoulder|shoulders)'
                
            pattern = fr'{search_type}\s+(\d+(?:\.\d+)?)'
            match = re.search(pattern, text)
            
            if match:
                value = float(match.group(1))
                # Normalize the measurement type
                normalized_type = m_type
                if m_type in ['arms', 'thighs', 'calves', 'shoulders']:
                    normalized_type = m_type[:-1]  # Remove the 's'
                
                measurements[normalized_type] = value
        
        # Add any custom measurements that match the pattern
        # Pattern: any word followed by a number and "inches"
        custom_measurements = re.findall(r'(\w+)\s+(\d+(?:\.\d+)?)\s+inch(?:es)?', text)
        for m_type, value in custom_measurements:
            if m_type not in ['weight', 'date', 'body', 'fat', 'bf'] and m_type not in measurement_types:
                measurements[m_type] = float(value)
        
        # Add measurements to result if any were found
        if measurements:
            result['measurements'] = measurements
        
        return result
    
    def accept(self):
        """Accept the recognized data and close the dialog."""
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel the dialog and discard any data."""
        self.result = None
        self.dialog.destroy()
    
    def get_result(self):
        """Get the result of the voice input.
        
        Returns:
            dict: Dictionary with the extracted data, or None if cancelled
        """
        return self.result

def show_voice_input_dialog(parent):
    """Show the voice input dialog and return the result.
    
    Args:
        parent: The parent window
        
    Returns:
        dict: Dictionary with the extracted data, or None if cancelled
    """
    dialog = VoiceInputDialog(parent)
    parent.wait_window(dialog.dialog)
    return dialog.result

# Test the dialog if run directly
if __name__ == "__main__":
    app = ctk.CTk()
    app.title("Voice Input Test")
    app.geometry("300x200")
    
    def test_dialog():
        result = show_voice_input_dialog(app)
        if result:
            print("Voice input result:", result)
        else:
            print("Voice input cancelled")
    
    button = ctk.CTkButton(app, text="Test Voice Input", command=test_dialog)
    button.pack(pady=50)
    
    app.mainloop()
