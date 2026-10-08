import pandas as pd
import pickle
import re
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score, classification_report

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

print("Loading Indian Banking Complaints dataset...")
df = pd.read_csv(r"G:\Mini_project\Dataset\GrievanceIQ_India_20K_Final.csv")

# Map 10 subcategories into 5 target departments
cat_map = {
    'Digital Payments': 'Digital & UPI Banking',
    'Mobile & Internet Banking': 'Digital & UPI Banking',
    'Remittance & Fund Transfer': 'Digital & UPI Banking',
    'Loans & Advances': 'Loans & Advances',
    'Credit Cards': 'Cards & ATM Services',
    'ATM & Debit Cards': 'Cards & ATM Services',
    'Deposit & Account Services': 'Account & Branch Operations',
    'Branch & Customer Service': 'Account & Branch Operations',
    'KYC & Account Compliance': 'Account & Branch Operations',
    'Fraud & Security': 'Fraud & Risk Management'
}

df['department'] = df['category'].map(cat_map)
df['complaint_clean'] = df['complaint_text'].apply(clean_text)

X = df['complaint_clean']
y = df['department']

print("Class distribution:")
print(y.value_counts())

# Stratified 80/20 split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"\nTrain size: {len(X_train)} | Test size: {len(X_test)}")

# TF-IDF vectorization
print("\nExtracting TF-IDF features...")
vectorizer = TfidfVectorizer(max_features=12000, stop_words="english", ngram_range=(1, 2))
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

# Train Linear SVM
print("Training Linear SVM classifier...")
model = LinearSVC(random_state=42, max_iter=2000)
model.fit(X_train_tfidf, y_train)

# Evaluate
y_pred = model.predict(X_test_tfidf)
acc = accuracy_score(y_test, y_pred)
print(f"\nModel Accuracy: {acc * 100:.2f}%")
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Save models
with open(r"G:\Mini_project\Python_codes\classifier.pkl", "wb") as f:
    pickle.dump(model, f)

with open(r"G:\Mini_project\Python_codes\vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)

print("Saved new classifier.pkl and vectorizer.pkl successfully!")