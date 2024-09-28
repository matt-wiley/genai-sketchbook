from textblob import TextBlob

def fix_text(text):
    # Convert the text to a TextBlob object
    blob = TextBlob(text)
    
    # Correct the spelling
    corrected_text = blob.correct()
    
    return str(corrected_text)

# Example usage
if __name__ == "__main__":
    input_text = "Ths is an exmple txt with sme mispelled words and incorrect puntuation"
    corrected_text = fix_text(input_text)
    
    print("Original Text:\n", input_text)
    print("\nCorrected Text:\n", corrected_text)
