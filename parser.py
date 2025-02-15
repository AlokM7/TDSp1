import openai
import os
import requests

import json

 # Load API keys from .env

AIRPROXY_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIzZjIwMDEwMjVAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.Af3URUAy9FzLTCSs2naVRcH9Ew7mRg5UeE2fKfqagvs"
url = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"

FUNCTION_LIST=[
    "download_files",
    "count_weekdays",
    "updating_files",
    "recent_files",
    "extract_information_from_email",
    "extract_information_from_markdown",
    "sort_contacts",
    "extract_images",
    "similar_embeddings",
    "Database_file_queries"
]

def parse_task(user_input):


    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AIRPROXY_TOKEN}" 
     }
    prompt = f"""
    You are an automation agent.A user provides a task in natural language. Your job is to extract:
    - The Function name (from the predefined list)
    - The source file (file to read from)
    - The output file (if specified, otherwise return null)
    - The task from the user input

    Give input and output file path in formate that avoids SyntaxError: unicodeescape,for example c:\\user\\onedrive .
    Your job is to map this task to one of the following standardized functions and :

    {', '.join(FUNCTION_LIST)}
    If the user input is similar to "Install uv (if required) and run https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/project-1/datagen.py" with user.email as the only argument Function is - "download_files"
    If the user input is similar to "Count the Sundays in the given date list", Function is- "count_weekdays".
    If the user input is "Extract sender’s email from /data/email.txt", Function is- "extract_information_from_email".
    If the user input is "Find all H1 titles from Markdown files", Function is- "extract_information_from_markdown".
    If the user input is " Format the contents of /data/format.md using prettier@3.4.2", Function is- "updating_files".
    If the user input is "Sort the array of contacts in /data/contacts.json by last_name, then first_name, and write the result to /data/contacts-sorted.json", Function is- "sort_contacts".
    If the user input is " Write the first line of the 10 most recent .log file in /data/logs/ to /data/logs-recent.txt, most recent first", Function is- "recent_files".
    If the user input is "data/credit-card.png contains a credit card number. Pass the image to an LLM, have it extract the card number, and write it without spaces to /data/credit-card.txt", Function is- "extract_images".
    If the user input is "/data/comments.txt contains a list of comments, one per line. Using embeddings, find the most similar pair of comments and write them to /data/comments-similar.txt, one per line", Function is- "similar_embeddings".
    If the user input is "The SQLite database file /data/ticket-sales.db has a tickets with columns type, units, and price. Each row is a customer bid for a concert ticket. What is the total sales of all the items in the “Gold” ticket type? Write the number in /data/ticket-sales-gold.txt", Function is- "Database_file_queries".
    
    
    Your Response should contain the following objects 
    1. Function
    2.Input_file_path
    3.output_file_path.
    4.Task

    return response as json.NO markdown or code blocks, just pure JSON!

    

    """ 
    data = {
        "model":"gpt-4o-mini",
        "messages": [
            {"role":"system" , "content":prompt},
            {"role":"user","content":user_input}
        ],
        "temperature": 0.7
    }

    response = requests.post(url, headers=headers, json=data)

    try:
        response_json = response.json()
        print("API Response:", response_json)  # Debugging log

        if "choices" not in response_json:
            return {"error": "Missing 'choices' in API response"}
        
        # ✅ Check if "choices" contains data
        choices = response_json.get("choices", [])
        if not choices:
            return {"error": "'choices' is empty"}

        # ✅ Extract response safely
        tasks = json.loads(choices[0]["message"]["content"])
        return tasks

    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}
    except json.JSONDecodeError:
        return {"error": "Invalid JSON response"}
    except KeyError as e:
        return {"error": f"Missing key: {str(e)}"}

   