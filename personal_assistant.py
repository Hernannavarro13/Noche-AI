import datetime
import random
import json
import os
import re
import webbrowser
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

def main():
    assistant = PersonalAssistant("MyAssistant")
    print(f"\nWelcome to {assistant.name}! Type 'help' to see available commands.\n")
    
    while True:
        user_input = input("> ")
        if user_input.lower() == "exit":
            print(assistant.exit_assistant(""))
            break
        
        response = assistant.process_input(user_input)
        print(response)

if __name__ == "__main__":
    main()
