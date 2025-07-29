import openai
import time
import json
import sys
import os
from dotenv import load_dotenv

load_dotenv(override=True)

openai.api_key = os.getenv("OPENAI_API_KEY")  # Replace with your API key

job_id = "ftjob-TklRFzcTLiPM39XLX8NTR8Pg"  # Replace with your job ID

# response = openai.fine_tuning.jobs.retrieve(job_id)
# print(response)

# Fix Unicode error on Windows (forces UTF-8 encoding)
sys.stdout.reconfigure(encoding='utf-8')

def monitor_finetune():
    try:
        # Retrieve fine-tuning job details
        response = openai.fine_tuning.jobs.retrieve(job_id)

        # Convert Pydantic object to a dictionary
        response_dict = json.loads(response.model_dump_json())

        # Extract relevant information safely
        status = response_dict.get("status", "Unknown")
        model = response_dict.get("fine_tuned_model", "Not available yet")
        created_at = response_dict.get("created_at", "Unknown")
        completed_at = response_dict.get("completed_at", "Still running")
        errors = response_dict.get("error", None)

        # Print output with proper formatting
        print("\n🚀 Fine-Tuning Job Status 🚀")
        print(f"📌 Job ID: {job_id}")
        print(f"🔄 Status: {status}")
        print(f"🤖 Fine-Tuned Model: {model}")
        print(f"📅 Created At: {created_at}")
        print(f"✅ Completed At: {completed_at}")

        if errors:
            print(f"⚠️ Error: {errors}")

    except Exception as e:
        print(f"[ERROR] Failed to retrieve job status: {e}")

# Run the monitor every 30 seconds
while True:
    monitor_finetune()
    time.sleep(30)  # Sleep for 30 seconds