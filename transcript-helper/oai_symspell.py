from symspellpy import SymSpell, Verbosity

def fix_text_with_symspell(text):
    # Create a SymSpell object
    sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
    # Load the dictionary from the included file
    sym_spell.load_dictionary("frequency_dictionary_en_82_765.txt", 0, 1)
    
    # Look for suggestions
    suggestions = sym_spell.lookup_compound(text, max_edit_distance=2)
    
    return suggestions[0].term if suggestions else text

# Example usage
input_text = "Ths is an exmple txt with sme mispelled words and incorrect puntuation"
corrected_text = fix_text_with_symspell(input_text)

print("Original Text:\n", input_text)
print("Corrected Text:\n", corrected_text)
