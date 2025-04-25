import datetime
import random
import json
import os
import re
import webbrowser
import tkinter as tk
from tkinter import scrolledtext, ttk
from typing import Dict, List, Callable, Any, Optional

class PersonalAssistant:
    def __init__(self, name: str = "Assistant"):
        self.name = name
        self.commands = {}
        self.tasks = []
        self.notes = []
        self.user_preferences = {}
        
        # Register built-in commands
        self.register_command("help", self.help_command, "Show available commands")
        self.register_command("time", self.get_time, "Display current time")
        self.register_command("date", self.get_date, "Display current date")
        self.register_command("add_task", self.add_task, "Add a task to your to-do list")
        self.register_command("list_tasks", self.list_tasks, "List all tasks")
        self.register_command("complete_task", self.complete_task, "Mark a task as completed")
        self.register_command("add_note", self.add_note, "Save a quick note")
        self.register_command("list_notes", self.list_notes, "List all saved notes")
        self.register_command("set_preference", self.set_preference, "Set a user preference")
        self.register_command("web_search", self.web_search, "Open web browser with search query")
        self.register_command("exit", self.exit_assistant, "Exit the assistant")
        
        # Load saved data if it exists
        self.load_data()
        
    def register_command(self, command: str, function: Callable, description: str) -> None:
        """Register a new command with the assistant."""
        self.commands[command] = {"function": function, "description": description}
    
    def process_input(self, user_input: str) -> str:
        """Process user input and execute appropriate command."""
        # Check for direct commands
        parts = user_input.strip().lower().split(" ", 1)
        command = parts[0]
        args = parts[1] if len(parts) > 1 else ""
        
        if command in self.commands:
            return self.commands[command]["function"](args)
        
        # Natural language processing (very basic)
        if "time" in user_input and "what" in user_input:
            return self.get_time("")
        elif "date" in user_input and "what" in user_input:
            return self.get_date("")
        elif any(phrase in user_input for phrase in ["add task", "new task", "create task"]):
            task_content = re.search(r"(?:add task|new task|create task)\s+(.*)", user_input, re.IGNORECASE)
            if task_content:
                return self.add_task(task_content.group(1))
        elif any(phrase in user_input for phrase in ["add note", "new note", "save note"]):
            note_content = re.search(r"(?:add note|new note|save note)\s+(.*)", user_input, re.IGNORECASE)
            if note_content:
                return self.add_note(note_content.group(1))
        elif "search for" in user_input or "look up" in user_input:
            search_terms = re.search(r"(?:search for|look up)\s+(.*)", user_input, re.IGNORECASE)
            if search_terms:
                return self.web_search(search_terms.group(1))
                
        # Default response if no command is recognized
        return self._generate_response(user_input)
    
    def _generate_response(self, user_input: str) -> str:
        """Generate a response when no specific command is recognized."""
        responses = [
            f"I'm not sure how to help with '{user_input}'. Type 'help' to see what I can do.",
            "I didn't understand that. Try 'help' to see available commands.",
            "Could you phrase that differently? Type 'help' for a list of commands I understand."
        ]
        return random.choice(responses)
    
    # Command implementations
    def help_command(self, args: str) -> str:
        """Display available commands and their descriptions."""
        help_text = f"\n{self.name} - Available Commands:\n"
        for cmd, details in self.commands.items():
            help_text += f"• {cmd}: {details['description']}\n"
        return help_text
    
    def get_time(self, args: str) -> str:
        """Get the current time."""
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        return f"The current time is {current_time}"
    
    def get_date(self, args: str) -> str:
        """Get the current date."""
        current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
        return f"Today is {current_date}"
    
    def add_task(self, task_description: str) -> str:
        """Add a task to the to-do list."""
        if not task_description:
            return "Please provide a task description."
        
        task = {
            "id": len(self.tasks) + 1,
            "description": task_description,
            "created": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "completed": False
        }
        self.tasks.append(task)
        self.save_data()
        return f"Task added: {task_description}"
    
    def list_tasks(self, args: str) -> str:
        """List all tasks."""
        if not self.tasks:
            return "You have no tasks."
        
        active_tasks = [task for task in self.tasks if not task["completed"]]
        completed_tasks = [task for task in self.tasks if task["completed"]]
        
        response = "\n--- TO-DO LIST ---\n"
        
        if active_tasks:
            response += "Active Tasks:\n"
            for task in active_tasks:
                response += f"[{task['id']}] {task['description']}\n"
        else:
            response += "No active tasks.\n"
        
        if completed_tasks:
            response += "\nCompleted Tasks:\n"
            for task in completed_tasks:
                response += f"[{task['id']}] {task['description']} ✓\n"
        
        return response
    
    def complete_task(self, task_id: str) -> str:
        """Mark a task as completed."""
        try:
            task_id = int(task_id)
            for task in self.tasks:
                if task["id"] == task_id:
                    task["completed"] = True
                    self.save_data()
                    return f"Task {task_id} marked as completed."
            return f"Task with ID {task_id} not found."
        except ValueError:
            return "Please provide a valid task ID number."
    
    def add_note(self, note_content: str) -> str:
        """Save a quick note."""
        if not note_content:
            return "Please provide note content."
        
        note = {
            "id": len(self.notes) + 1,
            "content": note_content,
            "created": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.notes.append(note)
        self.save_data()
        return f"Note saved: {note_content}"
    
    def list_notes(self, args: str) -> str:
        """List all saved notes."""
        if not self.notes:
            return "You have no saved notes."
        
        response = "\n--- NOTES ---\n"
        for note in self.notes:
            date = note["created"]
            response += f"[{note['id']}] ({date}): {note['content']}\n"
        
        return response
    
    def set_preference(self, preference_str: str) -> str:
        """Set a user preference."""
        try:
            key, value = preference_str.split("=", 1)
            key = key.strip()
            value = value.strip()
            self.user_preferences[key] = value
            self.save_data()
            return f"Preference set: {key} = {value}"
        except ValueError:
            return "Format should be: 'set_preference key=value'"
    
    def web_search(self, query: str) -> str:
        """Open web browser with search query."""
        if not query:
            return "Please provide a search query."
        
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(search_url)
        return f"Searching for: {query}"
    
    def exit_assistant(self, args: str) -> str:
        """Exit the assistant."""
        return "Goodbye! Have a great day."
    
    def save_data(self) -> None:
        """Save tasks, notes, and preferences to file."""
        data = {
            "tasks": self.tasks,
            "notes": self.notes,
            "preferences": self.user_preferences
        }
        
        with open("assistant_data.json", "w") as f:
            json.dump(data, f, indent=2)
    
    def load_data(self) -> None:
        """Load saved data if it exists."""
        try:
            if os.path.exists("assistant_data.json"):
                with open("assistant_data.json", "r") as f:
                    data = json.load(f)
                    self.tasks = data.get("tasks", [])
                    self.notes = data.get("notes", [])
                    self.user_preferences = data.get("preferences", {})
        except Exception as e:
            print(f"Error loading data: {e}")


class AssistantGUI:
    def __init__(self, root):
        self.root = root
        self.assistant = PersonalAssistant("MyAssistant")
        
        # Configure the root window
        self.root.title(f"{self.assistant.name}")
        self.root.geometry("700x500")
        self.root.minsize(600, 400)
        
        # Set default theme colors
        self.bg_color = "#f0f0f0"
        self.chat_bg = "#ffffff"
        self.input_bg = "#ffffff"
        self.button_bg = "#4a86e8"
        self.button_fg = "#ffffff"
        self.accent_color = "#4a86e8"
        
        # Create all UI components first
        self.setup_ui()
        
        # Then load theme preferences and apply them
        self.load_theme_preference()
        
        # Finally, display welcome message
        welcome_message = f"Welcome to {self.assistant.name}! Type 'help' to see available commands."
        self.display_message("Assistant", welcome_message)
        
    def setup_ui(self):
        # Create main frame
        self.main_frame = tk.Frame(self.root, bg=self.bg_color)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create chat display
        self.create_chat_display()
        
        # Create input area
        self.create_input_area()
        
        # Create shortcut buttons
        self.create_shortcut_buttons()
        
        # Create menu
        self.create_menu()
        
    def create_chat_display(self):
        # Chat display frame
        self.chat_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.chat_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(
            self.chat_frame,
            wrap=tk.WORD,
            bg=self.chat_bg,
            font=("Helvetica", 10),
            state="disabled"
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        # Configure tags for formatting
        self.chat_display.tag_configure("user", foreground="#333333", font=("Helvetica", 10, "bold"))
        self.chat_display.tag_configure("assistant", foreground=self.accent_color, font=("Helvetica", 10, "bold"))
        self.chat_display.tag_configure("message", foreground="#000000", font=("Helvetica", 10))
        
    def create_input_area(self):
        # Input frame
        self.input_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Input field
        self.user_input = tk.Entry(
            self.input_frame,
            bg=self.input_bg,
            font=("Helvetica", 10),
            relief=tk.SOLID,
            borderwidth=1
        )
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.user_input.bind("<Return>", self.on_send)
        self.user_input.focus_set()
        
        # Send button
        self.send_button = tk.Button(
            self.input_frame,
            text="Send",
            command=self.on_send,
            bg=self.button_bg,
            fg=self.button_fg,
            relief=tk.FLAT,
            padx=15
        )
        self.send_button.pack(side=tk.RIGHT)
        
    def create_shortcut_buttons(self):
        # Shortcut buttons frame
        self.shortcut_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.shortcut_frame.pack(fill=tk.X, padx=5, pady=5)
        
        shortcuts = [
            ("Help", "help"),
            ("Tasks", "list_tasks"),
            ("Notes", "list_notes"),
            ("Time", "time"),
            ("Date", "date")
        ]
        
        for label, command in shortcuts:
            btn = tk.Button(
                self.shortcut_frame,
                text=label,
                command=lambda cmd=command: self.execute_shortcut(cmd),
                bg="#e0e0e0",
                relief=tk.FLAT,
                padx=10,
                font=("Helvetica", 9)
            )
            btn.pack(side=tk.LEFT, padx=2)
            
    def create_menu(self):
        # Create main menu
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Clear Chat", command=self.clear_chat)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Theme menu
        theme_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Theme", menu=theme_menu)
        theme_menu.add_command(label="Light Theme", command=lambda: self.change_theme("light"))
        theme_menu.add_command(label="Dark Theme", command=lambda: self.change_theme("dark"))
        theme_menu.add_command(label="Blue Theme", command=lambda: self.change_theme("blue"))
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Commands", command=lambda: self.execute_shortcut("help"))
        help_menu.add_command(label="About", command=self.show_about)
    
    def on_send(self, event=None):
        user_input = self.user_input.get().strip()
        if not user_input:
            return
        
        # Display user input
        self.display_message("You", user_input)
        
        # Process input and get response
        response = self.assistant.process_input(user_input)
        
        # Display assistant response
        self.display_message("Assistant", response)
        
        # Clear input field
        self.user_input.delete(0, tk.END)
        
        # Handle exit command
        if user_input.lower() == "exit":
            self.root.after(1000, self.root.quit)
    
    def display_message(self, sender, message):
        self.chat_display.config(state="normal")
        
        # Add a newline if there's already content
        if self.chat_display.index('end-1c') != '1.0':
            self.chat_display.insert(tk.END, "\n\n")
        
        # Insert sender with appropriate tag
        sender_tag = "user" if sender == "You" else "assistant"
        self.chat_display.insert(tk.END, f"{sender}: ", sender_tag)
        
        # Insert message
        self.chat_display.insert(tk.END, message, "message")
        
        # Scroll to the end
        self.chat_display.see(tk.END)
        self.chat_display.config(state="disabled")
    
    def execute_shortcut(self, command):
        # Display command
        self.display_message("You", command)
        
        # Process command and get response
        response = self.assistant.process_input(command)
        
        # Display assistant response
        self.display_message("Assistant", response)
    
    def clear_chat(self):
        self.chat_display.config(state="normal")
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.config(state="disabled")
        
        # Add welcome message again
        welcome_message = f"Welcome to {self.assistant.name}! Type 'help' to see available commands."
        self.display_message("Assistant", welcome_message)
    
    def show_about(self):
        about_window = tk.Toplevel(self.root)
        about_window.title("About")
        about_window.geometry("400x200")
        about_window.resizable(False, False)
        
        # Center the window
        about_window.geometry("+{}+{}".format(
            int(self.root.winfo_x() + (self.root.winfo_width() / 2) - 200),
            int(self.root.winfo_y() + (self.root.winfo_height() / 2) - 100)
        ))
        
        frame = tk.Frame(about_window, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        title_label = tk.Label(
            frame, 
            text=f"{self.assistant.name}",
            font=("Helvetica", 14, "bold")
        )
        title_label.pack(pady=(0, 10))
        
        description = "A personal assistant that helps you manage tasks, notes, and more."
        desc_label = tk.Label(frame, text=description, wraplength=350)
        desc_label.pack(pady=(0, 15))
        
        version_label = tk.Label(frame, text="Version 1.0")
        version_label.pack()
        
        close_button = tk.Button(
            frame,
            text="Close",
            command=about_window.destroy,
            bg=self.button_bg,
            fg=self.button_fg,
            relief=tk.FLAT,
            padx=15
        )
        close_button.pack(pady=(15, 0))
    
    def change_theme(self, theme):
        if theme == "light":
            self.bg_color = "#f0f0f0"
            self.chat_bg = "#ffffff"
            self.input_bg = "#ffffff"
            self.button_bg = "#4a86e8"
            self.button_fg = "#ffffff"
            self.accent_color = "#4a86e8"
        elif theme == "dark":
            self.bg_color = "#2d2d2d"
            self.chat_bg = "#3d3d3d"
            self.input_bg = "#3d3d3d"
            self.button_bg = "#5294e2"
            self.button_fg = "#ffffff"
            self.accent_color = "#5294e2"
        elif theme == "blue":
            self.bg_color = "#e6f0ff"
            self.chat_bg = "#ffffff"
            self.input_bg = "#ffffff"
            self.button_bg = "#0066cc"
            self.button_fg = "#ffffff"
            self.accent_color = "#0066cc"
        
        # Save theme preference
        self.assistant.user_preferences["theme"] = theme
        self.assistant.save_data()
        
        # Apply theme
        self.apply_theme()
    
    def apply_theme(self):
        # Update main frames
        self.main_frame.config(bg=self.bg_color)
        self.chat_frame.config(bg=self.bg_color)
        self.input_frame.config(bg=self.bg_color)
        self.shortcut_frame.config(bg=self.bg_color)
        
        # Update chat display
        self.chat_display.config(bg=self.chat_bg)
        
        # Update input field
        self.user_input.config(bg=self.input_bg)
        
        # Update send button
        self.send_button.config(bg=self.button_bg, fg=self.button_fg)
        
        # Update tags
        self.chat_display.tag_configure("assistant", foreground=self.accent_color)
        
        # Update shortcut buttons (using a more subtle style)
        for child in self.shortcut_frame.winfo_children():
            if isinstance(child, tk.Button):
                child.config(bg="#e0e0e0" if self.bg_color == "#f0f0f0" else "#4d4d4d")
    
    def load_theme_preference(self):
        # Get theme preference or default to "light"
        theme = self.assistant.user_preferences.get("theme", "light")
        self.change_theme(theme)


def main():
    root = tk.Tk()
    app = AssistantGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()