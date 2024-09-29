import tiktoken


def calculate_tokens(text, model="gpt-3.5-turbo"):
    """
    Calculate the number of tokens in the given text for the specified model.
    
    :param text: The input text to tokenize
    :param model: The model to use for tokenization (default: "gpt-3.5-turbo")
    :return: The number of tokens in the text
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print(f"Warning: model '{model}' not found. Using default encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    
    num_tokens = len(encoding.encode(text))
    return num_tokens


if __name__ == "__main__":
    model = input("Enter the model name (default: gpt-3.5-turbo): ") or "gpt-3.5-turbo"
    text = input("Enter the text to tokenize: ")
    
    token_count = calculate_tokens(text, model)
    print(f"Number of tokens: {token_count}")