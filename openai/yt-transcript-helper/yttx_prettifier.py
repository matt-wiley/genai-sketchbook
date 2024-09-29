
import sys
import os
import json
import openai



openai.api_key = os.getenv('OPENAI_API_KEY')
MODEL = os.getenv('OPENAI_MODEL', 'gpt-4')
TEMPERATURE = 0.0
OUTPUT_DIR=".local/output/yttx"

# write a function that sends a generic message to OpenAI and returns the response
def chat_completion(model: str, messages: list[dict], temperature: float = 0):
    """Send a message to OpenAI and return the response."""
    openai.api_key = os.getenv('OPENAI_API_KEY')
    model = os.getenv('OPENAI_MODEL', model)
    response = openai.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=1500,
        temperature=temperature,
    )
    return response


# write a function that reads in a text file and breaks it into 10 line stanzas, each stanza being a separate string, preserving the line breaks
def read_file_into_stanzas(file_path):
    stanzas = []
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for i in range(0, len(lines), 10):
            stanza = ''.join(lines[i:i+10])
            stanzas.append(stanza)
    return stanzas



def ai_edit_stanza(stanza: str):
    messages = [
        {
            "role": "user",
            "content": "\n".join([
                "The text below is an excerpt of dialog transcripted from an interview.",
                "Edit the text for spelling and punctuation.",
                "DO NOT alter the text in any other way.",
                "DO NOT omit words or change phrasing in any way.",
                "Only return the edited text.\n"
                f"Excerpt:\n\n{stanza}"
            ])
        }
    ]

    chat_response = chat_completion(MODEL, messages, TEMPERATURE)

    all_responses = [choice.message.content for choice in chat_response.choices]

    return "\n\n".join(all_responses)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # read file path from cli
    file_path = sys.argv[1]
    stanzas = read_file_into_stanzas(file_path)

    # get file name of the input file without the extension
    output_filename_prefix = os.path.basename(os.path.dirname(file_path))

    count = 0
    for stanza in stanzas:
        output_file = os.path.join(OUTPUT_DIR, f"{output_filename_prefix}/part_{count}.md")
        with open(output_file, 'w') as file:
            # file.write(f"Input:\n\n{stanza}\n\n---\n\nOutput:\n\n")
            file.write(ai_edit_stanza(stanza))
        count += 1


if __name__ == '__main__':
    main()