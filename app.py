from flask import Flask, render_template, request, jsonify
import pickle
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

app = Flask(__name__)
try:
    stopwords.words('english')
except LookupError:
    nltk.download('stopwords')

def preprocess_text(text):
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

model_filename = "spam_classifier_model.pkl"
model = None
try:
    with open(model_filename, "rb") as f:
        model = pickle.load(f)
    print(f"Model '{model_filename}' loaded successfully.")
except Exception as e:
    print(f"FATAL ERROR loading model: {e}")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    if not model:
        return jsonify({'error': 'Model is not loaded.'}), 500
    try:
        data = request.get_json()
        message = data.get('message', '')
        if not message.strip():
            return jsonify({'error': 'Message cannot be empty.'}), 400
        processed_message = preprocess_text(message)
        prediction = model.predict([processed_message])[0]
        probabilities = model.predict_proba([processed_message])[0]
        confidence = probabilities[1] if prediction == 'spam' else probabilities[0]
        result = {
            'prediction': prediction.upper(),
            'confidence': f"{confidence*100:.2f}"
        }
        return jsonify(result)
    except Exception as e:
        print(f"Error during prediction: {e}")
        return jsonify({'error': 'An error occurred during prediction.'}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
