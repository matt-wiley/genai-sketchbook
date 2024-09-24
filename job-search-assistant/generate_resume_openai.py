import os
import json
import openai

from dotenv import load_dotenv

load_dotenv()

def read_json_file(file_path):
    """Reads a JSON file and returns its content."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def read_text_file(file_path):
    """Reads a text file and returns its content."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def generate_openai_prompt(job_history, job_description):
    """Creates a prompt for OpenAI based on job history and job description."""
    # Extract key roles, skills, and experiences from job history
    job_experiences = []
    for employer in job_history['employers']:
        for role in employer['roles']:
            job_experiences.append({
                "employer": employer['name'],
                "location": employer['location'],
                "role_title": role['title'],
                "start_date": role['start_date'],
                "end_date": role['end_date'] or "Present",
                "description": role['description'],
                "notes": [note['summary'] for note in role['notes'] if note['is_enabled']]
            })
    
    # Constructing the prompt to be sent to OpenAI
    prompt = (
        "You are a professional résumé writer. Generate a résumé based on the following job history and job description. "
        "Focus on highlighting skills and responsibilities relevant to the job description, but also include any experiences "
        "that align with the company's mission or values if possible.\n\n"
        
        "Job Description:\n"
        f"{job_description}\n\n"
        
        "Job History:\n"
    )
    
    for experience in job_experiences:
        prompt += (
            f"Role: {experience['role_title']} at {experience['employer']} ({experience['location']})\n"
            f"Period: {experience['start_date']} to {experience['end_date']}\n"
            f"Description: {experience['description'] or 'No description provided'}\n"
            "Key Achievements:\n"
        )
        for note in experience['notes']:
            prompt += f"- {note}\n"
        prompt += "\n"
    
    prompt += (
        "Please create a one-page professional résumé, ensuring the content is concise and aligns with the job description. "
        "Start with a brief summary of relevant skills, then highlight the most relevant work experiences, emphasizing skills, "
        "responsibilities, and achievements that match the job description. The résumé should maintain a professional tone."
    )
    
    return prompt

def generate_resume_with_openai(job_history_file, job_description_file, output_file):
    """Generates a résumé using OpenAI's API."""
    # Read job history and job description
    job_history = read_json_file(job_history_file)
    job_description = read_text_file(job_description_file)
    
    # Prepare the prompt for OpenAI
    prompt = generate_openai_prompt(job_history, job_description)
    
    # Read the OpenAI API key from environment
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        raise EnvironmentError("OpenAI API key not found in environment variables. Please set OPENAI_API_KEY.")
    
    # Set up OpenAI API
    openai.api_key = openai_api_key
    
    # Call OpenAI to generate the résumé
    response = openai.Completion.create(
        engine=os.getenv('OPENAI_MODEL', 'gpt-4o-2024-05-13'),  # Read engine from environment variable
        prompt=prompt,
        max_tokens=1500,            # Adjust based on how detailed you want the résumé to be
        temperature=0.7             # Adjust for creativity level; 0.7 should keep it balanced
    )
    
    # Extract the generated résumé text
    resume_text = response['choices'][0]['text'].strip()
    
    # Write the résumé to the output file
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(resume_text)
    
    print(f"AI-generated résumé saved to {output_file}")

# Example usage
# generate_resume_with_openai('job_history.json', 'job_description.txt', 'tailored_resume_openai.txt')
