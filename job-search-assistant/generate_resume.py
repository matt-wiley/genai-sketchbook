import json
import re
from collections import defaultdict
from datetime import datetime

def read_json_file(file_path):
    """Reads a JSON file and returns its content."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def read_text_file(file_path):
    """Reads a text file and returns its content."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def extract_keywords(job_description):
    """Extracts significant keywords from the job description."""
    words = re.findall(r'\b\w+\b', job_description.lower())
    common_words = set(["and", "the", "to", "of", "in", "a", "with", "for", "on", "as", "by", "at", "from", "or", "an", "is", "it", "this", "that"])
    return set(word for word in words if word not in common_words)

def match_relevant_experience(job_history, keywords):
    """Matches job history experiences that are relevant to the job description."""
    relevant_experience = []
    
    for employer in job_history['employers']:
        for role in employer['roles']:
            role_keywords = extract_keywords(role['description'] or "")

            if role_keywords.intersection(keywords):
                experience_entry = {
                    "employer": employer['name'],
                    "location": employer['location'],
                    "role_title": role['title'],
                    "start_date": role['start_date'],
                    "end_date": role['end_date'] or "Present",
                    "description": role['description'],
                    "notes": [note['summary'] for note in role['notes'] if note['is_enabled']]
                }
                relevant_experience.append(experience_entry)
    
    return sorted(relevant_experience, key=lambda x: datetime.strptime(x['start_date'], "%Y-%m") if x['start_date'] else datetime.min, reverse=True)

def generate_summary(relevant_experience, job_description_keywords):
    """Generates a brief summary highlighting how experience aligns with the job description."""
    if not relevant_experience:
        return "Experienced professional with a diverse background, eager to contribute effectively to this role."
    
    matched_keywords = set()
    for experience in relevant_experience:
        matched_keywords.update(extract_keywords(experience['description'] or ""))

    common_keywords = matched_keywords.intersection(job_description_keywords)
    summary = f"Experienced professional with strong expertise in {', '.join(list(common_keywords)[:5])}, ready to leverage skills in this position." \
              if common_keywords else "Seasoned professional with relevant experience ready to excel in this role."

    return summary

def format_resume_text(summary, relevant_experience):
    """Formats the résumé text based on the matched experiences and summary."""
    resume_text = "SUMMARY\n" + summary + "\n\nWORK EXPERIENCE\n"
    
    for experience in relevant_experience:
        resume_text += f"{experience['role_title']} at {experience['employer']} ({experience['location']})\n"
        resume_text += f"{experience['start_date']} to {experience['end_date']}\n"
        if experience['description']:
            resume_text += experience['description'] + "\n"
        for note in experience['notes']:
            resume_text += f"- {note}\n"
        resume_text += "\n"
    
    return resume_text.strip()

def generate_resume(job_history_file, job_description_file, output_file):
    """Generates a tailored résumé."""
    job_history = read_json_file(job_history_file)
    job_description = read_text_file(job_description_file)
    
    job_description_keywords = extract_keywords(job_description)
    relevant_experience = match_relevant_experience(job_history, job_description_keywords)
    summary = generate_summary(relevant_experience, job_description_keywords)
    resume_text = format_resume_text(summary, relevant_experience)
    
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(resume_text)

    print(f"Résumé generated and saved to {output_file}")

# Example usage
# generate_resume('job_history.json', 'job_description.txt', 'tailored_resume.txt')
