from deepsegment import DeepSegment

def split_sentences_with_deepsegment(text):
    segmenter = DeepSegment('en')
    sentences = segmenter.segment(text)
    return sentences

# Example usage
input_text = "this is a poorly punctuated text it doesnt have proper periods or commas but it needs segmentation"
sentences = split_sentences_with_deepsegment(input_text)

print("Identified Sentences:\n", sentences)
