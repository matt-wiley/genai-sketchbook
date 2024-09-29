import language_tool_python

def fix_text_with_languagetool(text):
    tool = language_tool_python.LanguageTool('en-US')
    matches = tool.check(text)
    corrected_text = language_tool_python.correct(text, matches)
    return corrected_text

# Example usage
input_text = "Ths is an exmple txt with sme mispelled words and incorrect puntuation"
corrected_text = fix_text_with_languagetool(input_text)

print("Original Text:\n", input_text)
print("Corrected Text:\n", corrected_text)
