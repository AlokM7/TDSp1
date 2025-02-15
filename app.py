from fastapi import FastAPI
import subprocess
import json
from pathlib import Path
from task import *
from parser import *
app = FastAPI()

BASE_DIR = Path("output_files")
BASE_DIR.mkdir(exist_ok=True)

@app.get("/")
def home():
    return {"detail":"hello"}

@app.post("/run")
def run_task(task: str):
    try:
        print(f"Received task: {task}")  # Debugging log
        parsed_task = parse_task(task)
        
        if "error" in parsed_task:
            return {"error": parsed_task["error"]}

        print(f"Parsed task: {parsed_task}")  # Debugging log
        result = execute_task(parsed_task) 

        return {"task": parsed_task, "result": result}
    
    except Exception as e:
        return {"error": str(e)}

@app.get("/read")
def read_file(path: str):
    file_path =  BASE_DIR /path
    if file_path.exists():
        

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()  # Read the file as raw text

        print(content)
      
        # Try to convert to an integer if the content is purely numeric
        if content.strip().isdigit():
            return int(content.strip())  
        # Ensure no leading/trailing spaces
        content = content.encode().decode('unicode_escape')
    
        
        # Try to parse as JSON (for lists, dictionaries, etc.)
        try:
            return json.loads(content.strip())  # Strip whitespace before parsing JSON
        except json.JSONDecodeError:
            pass  # If it's not JSON, continue

        return content  # Return exactly as read, preserving format

    return {"error": "File not found"}
