from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter

# 1. Setup for Fixed Size Chunking
fixed_splitter = CharacterTextSplitter(
    separator="", #nothing bcz based on no. of characters/words
    chunk_size=100,
    chunk_overlap=0
)
# 2. Setup for Paragraph-Based Chunking
paragraph_splitter = CharacterTextSplitter(
    separator="\n\n",  # Represents empty lines between paragraphs
    chunk_size=100,
    chunk_overlap=0
)
# 3. Setup for Recursive Character Chunking
recursive_splitter = RecursiveCharacterTextSplitter(
    # No separator needed; it uses a default list prioritized from paragraphs down to characters
    chunk_size=100,
    chunk_overlap=20   # Retains 20 characters from the end of the previous chunk
)

text = """The man who did the crime was John. Nobody in the village trusted him, but he had disappeared three days before the murder. The detective immediately realized something was wrong. The room was silent, and the blood-stained letter that lay on the table was the only clue.

John had always been a quiet man, keeping to himself and rarely speaking to the neighbors. However, his recent behavior had raised suspicions. 

Why did John do the crime? That remains a mystery, but the evidence points directly at him."""

print("\n----------- FIXED SIZE -----------")
for i, chunk in enumerate(fixed_splitter.split_text(text), 1):
    print(f"\nChunk {i}:")
    print(chunk)
    print("-" * 40)

print("\n----------- PARAGRAPH -----------")
for i, chunk in enumerate(paragraph_splitter.split_text(text), 1):
    print(f"\nChunk {i}:")
    print(chunk)
    print("-" * 40)

print("\n----------- RECURSIVE -----------")
for i, chunk in enumerate(recursive_splitter.split_text(text), 1):
    print(f"\nChunk {i}:")
    print(chunk)
    print("-" * 40)