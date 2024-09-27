import spacy

# Load the SpaCy model with dependency parsing
nlp = spacy.load("en_core_web_sm")

def split_sentences_with_spacy(text):
    doc = nlp(text)
    # Use SpaCy's dependency parsing to segment sentences
    sentences = [sent.text.strip() for sent in doc.sents]
    return sentences

# Example usage
input_text = "This is a poorly punctuated text it has no periods or commas can you identify sentences"
sentences = split_sentences_with_spacy(input_text)

print("Identified Sentences:\n", sentences)
