import pandas as pd
import re
import pickle
import nltk
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# --- Setup: Download NLTK data ---
try:
    stopwords.words('english')
except LookupError:
    nltk.download('stopwords')

# --- 1. Preprocessing Function (This part is now perfect) ---
def preprocess_text(text):
    """
    Cleans and preprocesses text data, including emoji and symbol handling.
    """
    stemmer = PorterStemmer()
    stop_words = set(stopwords.words('english'))

    text = text.lower()
    text = re.sub(r'💰', ' _moneyemoji_ ', text)
    text = re.sub(r'([\$£€₹]|rs)', ' _currency_ ', text)
    text = re.sub(r"http\S+|www\S+", " _link_ ", text)
    text = re.sub(r"\d+", " _number_ ", text)
    text = re.sub(r'([!@#?])', r' \1 ', text)
    text = re.sub(r'[^\w\s_]', '', text)

    tokens = text.split()
    stemmed_tokens = [stemmer.stem(word) for word in tokens if word not in stop_words]

    return ' '.join(stemmed_tokens)

# --- 2. Load and Prepare the Dataset ---
print("Loading and preparing dataset from spam.csv...")
try:
    df = pd.read_csv("spam.csv", encoding="ISO-8859-1", usecols=['v1', 'v2'])
    df.columns = ['label', 'text']
    df.dropna(inplace=True)
except FileNotFoundError:
    print("Error: 'spam.csv' not found.")
    exit()

# --- 3. Apply Preprocessing ---
print("\nCleaning text data with the final function...")
df['clean_text'] = df['text'].apply(preprocess_text)
print("Preprocessing complete.")

# --- 4. Split Data and Build NEW Model Pipeline ---
print("\nBuilding the new, more powerful model pipeline...")
X_train, X_test, y_train, y_test = train_test_split(
    df['clean_text'], df['label'], test_size=0.2, random_state=42, stratify=df['label']
)

# NEW: We are building a more advanced pipeline
model_pipeline = Pipeline([
    # The vectorizer will now look at single words and pairs of words (n-grams)
    ('tfidf', TfidfVectorizer(ngram_range=(1, 2))),
    
    # We are using a more robust classifier that handles imbalanced data
    ('classifier', LogisticRegression(class_weight='balanced', solver='liblinear', random_state=42))
])

# --- 5. Train the New Model ---
print("Training the new Logistic Regression model...")
model_pipeline.fit(X_train, y_train)
print("Model training complete.")

# --- 6. Evaluate Model Performance ---
accuracy = model_pipeline.score(X_test, y_test)
print(f"\nNew model accuracy on the test data: {accuracy:.2%}")

# --- 7. Save the Final Trained Model ---
model_filename = "spam_classifier_model.pkl"
print(f"Saving the final, most powerful model to '{model_filename}'...")
with open(model_filename, "wb") as f:
    pickle.dump(model_pipeline, f)

print(f"\n[OK] ✅ The definitive model has been trained and saved!")
