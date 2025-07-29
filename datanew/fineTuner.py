import openai
import os
from dotenv import load_dotenv

load_dotenv(override=True)

# Set your API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Path to your file
file_path = "D:\\Study\\3rd Year\\6th Sem\\LawLiet\\check.jsonl"

# Upload your dataset
with open(file_path, "rb") as file:
    response = openai.files.create(file=file, purpose="fine-tune")

file_id = response.id  # Access the file ID from the response object

# Create a fine-tuning job
response = openai.fine_tuning.jobs.create(
    training_file=file_id, model="gpt-4o-mini-2024-07-18"
)

print(f"Fine-tuning job created: {response.id}")  # print the job ID
