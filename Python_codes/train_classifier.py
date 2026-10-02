import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score, classification_report

# Load cleaned data
df = pd.read_csv(r"G:\Mini_project\Dataset\grievanceiq_15k_priority.csv")

X = df["narrative_clean"]
y = df["product_5"]

# Stratified 80/20 split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print("Train size:", len(X_train))
print("Test size:", len(X_test))

# TF-IDF vectorization
vectorizer = TfidfVectorizer(max_features=10000, stop_words="english")
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

# Train SVM
print("Training SVM...")
model = LinearSVC(random_state=42)
model.fit(X_train_tfidf, y_train)

# Evaluate
y_pred = model.predict(X_test_tfidf)
print("\nAccuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Save both the model AND the vectorizer (both needed to classify new text later)
with open(r"G:\Mini_project\Python_codes\classifier.pkl", "wb") as f:
    pickle.dump(model, f)

with open(r"G:\Mini_project\Python_codes\vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)

print("\nSaved classifier.pkl and vectorizer.pkl")