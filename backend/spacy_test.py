import spacy

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

# Function to extract named entities
def extract_named_entities(text):
    # Process the text with spaCy
    doc = nlp(text)
    # Extract named entities
    named_entities = [(ent.text, ent.label_) for ent in doc.ents]
    return named_entities

# Example usage
user_question = "Is there a condo called Sunview Gardens near the Central Park station with a pool and fitness center, priced under $2000 per month?"
entities = extract_named_entities(user_question)

# Display the extracted named entities
print(entities)
