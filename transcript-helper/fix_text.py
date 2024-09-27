from textblob import TextBlob
from symspellpy import SymSpell, Verbosity

INPUT_TEXT = "Ths is an exmple txt with sme mispelled words and incorrect puntuation let's see if this works"

def split_sentences_with_textblob(text):
    blob = TextBlob(text)
    return blob.sentences

def fix_text_with_symspell(text):
    # Create a SymSpell object
    sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
    # Load the dictionary from the included file
    sym_spell.load_dictionary("frequency_dictionary_en_82_765.txt", 0, 1)
    
    # Look for suggestions
    suggestions = sym_spell.lookup_compound(text, max_edit_distance=2)
    
    return suggestions[0].term if suggestions else text

def text_blob_corrections(text):
    # Convert the text to a TextBlob object
    blob = TextBlob(text)
    
    # Correct the spelling
    corrected_text = blob.correct()
    
    return str(corrected_text)


# Example usage
if __name__ == "__main__":
    input_text = INPUT_TEXT

    sentences = split_sentences_with_textblob(input_text)

    for sentence in sentences:
        print("Original sentence:\n", input_text)
        output_text = str(input_text)

        output_text = fix_text_with_symspell(output_text)
        print("SymSpell Corrections:\n", output_text)

        # output_text = text_blob_corrections(input_text)
        # print("TextBlob Correcte Text:\n", output_text)
