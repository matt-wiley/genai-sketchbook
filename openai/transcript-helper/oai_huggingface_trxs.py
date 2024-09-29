from transformers import pipeline

def fix_text_with_transformer(text):
    corrector = pipeline("text2text-generation", model="vennify/t5-base-grammar-correction")
    corrected_text = corrector(text)[0]['generated_text']
    return corrected_text

# Example usage
input_text = "Ths is an exmple txt with sme mispelled words and incorrect puntuation"
corrected_text = fix_text_with_transformer(input_text)

print("Corrected Text:\n", corrected_text)
