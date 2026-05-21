import joblib
import os
from sklearn.svm import SVC
from sklearn.datasets import make_classification

# Generate dummy classification data
X, y = make_classification(n_samples=100, n_features=10, random_state=42)

# Train a dummy SVM model
model = SVC(kernel='linear', probability=True)
model.fit(X, y)

# Save the model
model_dir = os.path.join(os.path.dirname(__file__), 'api', 'model')
os.makedirs(model_dir, exist_ok=True)
model_path = os.path.join(model_dir, 'svm_model.pkl')

joblib.dump(model, model_path)
print(f"Dummy model saved to {model_path}")
