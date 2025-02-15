import pandas as pd
import json
import sqlite3
from dateutil import parser
from datetime import datetime
import subprocess
import sys
import shutil
from pathlib import Path
import os
import ast
from fastapi import FastAPI, Query, HTTPException
import requests
import pathlib
from parser import AIRPROXY_TOKEN

BASE_DIR = Path(__file__).resolve().parent



url = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
def count_weekdays(task,input_file,output_file):
    weekday_num = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6}
    day = ""
    for n in weekday_num:
        if(n in task):
            day = n
            break;
    
    with open(input_file,"r") as file:
        dates = file.readlines()
    
    formatted_dates = []

    for date in dates:
        date = date.strip()
        if date:
            parsed_date = parser.parse(date)
            formatted_dates.append(parsed_date.strftime("%d-%m-%Y"))
   

    date_objects = [datetime.strptime(date, "%d-%m-%Y") for date in formatted_dates]

    count = sum(1 for date in date_objects if date.weekday() ==weekday_num[day] )

    print(count)

    with open(output_file,"w") as file:
        json.dump(count, file, indent=4)
        
def format_markdown(task,file_path,file_out):
  
    file_path = Path(file_path).resolve()

    if not shutil.which("prettier"):
        print("Error: Prettier is not installed. Run install_prettier() first.")
        return

    try:
        print(f"Formatting {file_path}...")
        path_prettier = "C:\\Users\\Nimisha Manawat\\AppData\\Roaming\\npm\\prettier.cmd"
        subprocess.run([path_prettier, "--write", str(file_path)], check=True)
        print("Formatting complete!")
    except subprocess.CalledProcessError:
        print("Error: Failed to format the file.")



def email_result(task,file_i,file_o):
    
    with open(file_i,"r") as f:
        mail = f.readlines()
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AIRPROXY_TOKEN}" 
    }
    prompt = '''You are an Automation agent. You must respond **only** in valid JSON format. Do not return any additional text. Your response should always be in this format: 
    {"Answer": "Extracted email", "output_file_path": "Given file path"} 
    Ensure that "Answer" contains the exact email extracted.'''
    data = {
        "model":"gpt-4o-mini",
        "messages": [
            {"role":"system" , "content":prompt },
            {"role":"user","content":f'Extract the email asked from the following text and respond strictly in JSON format: {mail}'}
        ],
        "temperature": 0.7
    }
    
    response = requests.post(url,headers=headers,json=data)
    response_json = response.json()

    if "choices" in response_json:
        message_content = response_json["choices"][0]["message"]["content"]
        data = json.loads(message_content)  # Ensure we parse the inner JSON string
    elif "content" in response_json:  # Fallback if response is simpler
        data = {"Answer": response_json["content"]}
    else:
        raise ValueError("Unexpected API response format")
    
    with open(file_o, "w") as f:
        f.write(data.get('Answer', '').strip('"'))


def sort(task,file_i,file_o):
    with open(file_i,"r") as f:
        contacts = f.read()
    u = ast.literal_eval(contacts)
    sorted_people = sorted(u, key=lambda x: (x["last_name"], x["first_name"]))

    with open(file_o,"w") as f:
        json.dump(sorted_people, f, indent=4)

SCRIPT_URL = "https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/project-1/datagen.py"
SCRIPT_PATH = BASE_DIR/ "datagen.py"
DATA_PATH = pathlib.Path("data")

def download_script(file_i):
   
    if not SCRIPT_PATH.exists():
        url = file_i
        response = requests.get(url)
        
        if response.status_code == 200:
            with open(SCRIPT_PATH, "wb") as f:
                f.write(response.content)
        else:
            raise Exception("Failed to download datagen.py")
def execute_script(user_email: str,file_i):
   
    try:
        download_script(file_i) 

        os.makedirs(DATA_PATH, exist_ok=True)

        command = ["uv", "run", str(SCRIPT_PATH), user_email]
        process = subprocess.run(command, capture_output=True, text=True)

        if process.returncode == 0:
            return {"status": "success", "output": process.stdout.strip()}
        else:
            raise HTTPException(status_code=500, detail=f"Script error: {process.stderr.strip()}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

def install_files(task,file_i,file_o):
    if task:
        user_email = "23f2001025@ds.study.iitm.ac.in"  
        return execute_script(user_email,file_i)
    else:
        raise HTTPException(status_code=400, detail="Invalid task description")
    




def log_files(task,file_i,file_o):
    log_dir = Path(file_i)
    output_file = Path(file_o)

    # Get all .log files in the directory
    log_files = sorted(
        log_dir.glob("*.log"),  # Find all .log files
        key=lambda f: f.stat().st_mtime,  # Sort by modification time (most recent first)
        reverse=True  # Newest first
    )

    # Select the 10 most recent files
    recent_logs = log_files[:10]

    # Read the first line from each file
    first_lines = []
    for log_file in recent_logs:
        with open(log_file, "r", encoding="utf-8") as f:
            first_line = f.readline().strip()  # Read the first line
            first_lines.append(first_line)

    # Write the collected lines to the output file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(first_lines))

    print("Recent log entries written to:", output_file)

import base64
import re

def extract_credit_card_number(llm_output):
    # Regular expression to match a 16-digit credit card number in groups of 4
    match = re.search(r'(\d{4} \d{4} \d{4} \d{4})', llm_output)
    
    if match:
        card_number = match.group(1).replace(" ", "")  # Remove spaces
        return card_number
    return None

def image_extraction(task,file_i,file_o):
    with open(file_i, 'rb') as image_file:
        image_data = image_file.read()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AIRPROXY_TOKEN}"
    }

    base64_image = base64.b64encode(image_data).decode('utf-8')

    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        # Let's modify the prompt to give the LLM some creativity
                        "text": "Describe the image."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "detail": "low",
                            # Instead of passing the image URL, we create a base64 encoded data URL
                            "url": f"data:image/png;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
    }

    url = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"

    response = requests.post(url, headers=headers, json=data)

    print(response.json()["choices"][0]["message"]["content"])

    data1 = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        # Let's modify the prompt to give the LLM some creativity
                        "text": "Describe the image.Read all the content written on it."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "detail": "low",
                            # Instead of passing the image URL, we create a base64 encoded data URL
                            "url": f"data:image/png;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
    }


    response1 = requests.post(url, headers=headers, json=data1)

    l = response1.json()["choices"][0]["message"]["content"]

    j = extract_credit_card_number(l)
    print(j)

    with open(file_o,"w") as f:
        f.write(str(j))


TASK_MAPPING = {
    "count_weekdays": count_weekdays,
    "updating_files": format_markdown,
    "extract_information_from_email": email_result,
    "sort_contacts":sort,
    "download_files":install_files,
    "recent_files":log_files,
    "extract_images":image_extraction,

}

def execute_task(parsed_task):
    function_name = parsed_task["Function"]
    input_file = parsed_task["Input_file_path"]
    output_file = parsed_task["output_file_path"]
    task = parsed_task["Task"]


    if function_name in TASK_MAPPING:
        return TASK_MAPPING[function_name](task,input_file,output_file)
    else:
        return f"Task '{function_name}' not found."

