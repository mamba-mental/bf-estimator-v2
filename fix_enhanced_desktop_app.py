#!/usr/bin/env python

def fix_file():
    # Path to the file
    file_path = 'enhanced_desktop_app.py'
    
    # Read the file content
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    # Find and fix the line with the error
    for i in range(len(lines)):
        # Look for line 652 area
        if i >= 650 and i <= 654:
            # Check for unclosed parenthesis or positional arg after keyword arg
            if "self.muscle_entry.grid(row=3, column=1, pa" in lines[i]:
                # Fix this line by completing it correctly
                lines[i] = "        self.muscle_entry.grid(row=3, column=1, padx=10, pady=(10, 0), sticky=\"ew\")\n"
                print(f"Fixed line {i+1}: {lines[i].strip()}")
    
    # Write the fixed content back to the file
    with open(file_path, 'w') as file:
        file.writelines(lines)
    
    print("Fix completed! The enhanced_desktop_app.py file has been updated.")

if __name__ == "__main__":
    fix_file()
