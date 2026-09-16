import json
import random
from datetime import datetime

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB


class ChatbotEngine:
    def __init__(self, intents_path, confidence_threshold=0.15):
        self.confidence_threshold = confidence_threshold

        with open(intents_path, "r", encoding="utf-8") as f:
            self.intents = json.load(f)["intents"]

        training_texts = []
        training_labels = []
        self.tag_data = {}

        for intent in self.intents:
            tag = intent["tag"]
            self.tag_data[tag] = {
                "responses": intent["responses"],
                "quick_replies": intent.get("quick_replies", [])
            }
            for pattern in intent["patterns"]:
                training_texts.append(self._clean(pattern))
                training_labels.append(tag)

        self.vectorizer = TfidfVectorizer()
        X = self.vectorizer.fit_transform(training_texts)

        self.model = MultinomialNB()
        self.model.fit(X, training_labels)

    @staticmethod
    def _clean(text):
        text = text.lower().strip()
        for ch in "?!.,":
            text = text.replace(ch, "")
        return text

    def _dynamic_response(self, tag):
        now = datetime.now()
        if tag == "time":
            return f"The current time is {now.strftime('%I:%M %p')}. ⏰"
        if tag == "date":
            return f"Today's date is {now.strftime('%B %d, %Y')}. 📅"
        return None

    def get_response(self, message):
        cleaned = self._clean(message)

        if not cleaned:
            return self._fallback()

        X_input = self.vectorizer.transform([cleaned])

        predicted_tag = self.model.predict(X_input)[0]

        probabilities = self.model.predict_proba(X_input)[0]
        confidence = max(probabilities)

        if confidence < self.confidence_threshold:
            return self._fallback()

        dynamic = self._dynamic_response(predicted_tag)
        if dynamic:
            quick_replies = self.tag_data[predicted_tag]["quick_replies"]
            return dynamic, predicted_tag, quick_replies

        data = self.tag_data[predicted_tag]
        response = random.choice(data["responses"])
        return response, predicted_tag, data["quick_replies"]

    def _fallback(self):
        data = self.tag_data.get("default", {"responses": ["I'm not sure I understand."], "quick_replies": []})
        return random.choice(data["responses"]), "default", data["quick_replies"]
