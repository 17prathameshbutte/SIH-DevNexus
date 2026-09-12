"""
pulse_classifier.py
--------------------
Multi-layer perceptron that classifies interleaved pulse trains (PDWs) into
specific emitter / threat categories. Same nn.Module + DataLoader + training
loop pattern used in ANN_Classification.ipynb, adapted to the PDW feature
matrix produced by dataset_preprocessing.py.
"""

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split

from dataset_preprocessing import build_feature_matrix

WEIGHTS_PATH = "pulse_classifier.pth"


class PulseClassifier(nn.Module):
    def __init__(self, input_dim, num_classes):
        super(PulseClassifier, self).__init__()

        self.model = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, num_classes),
        )

    def forward(self, x):
        return self.model(x)


def prepare_tensors(csv_path="test_pdw_sample.csv", test_size=0.2, seed=42):
    df = pd.read_csv(csv_path)
    X, y, scaler, vectorizer, feature_names = build_feature_matrix(df, fit=True)

    if y is None:
        raise ValueError("No 'emitter_id' label column found in the parsed dataset.")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=seed, stratify=y
    )

    X_train_t = torch.tensor(X_train, dtype=torch.float32)
    y_train_t = torch.tensor(y_train, dtype=torch.long)
    X_test_t = torch.tensor(X_test, dtype=torch.float32)
    y_test_t = torch.tensor(y_test, dtype=torch.long)

    return X_train_t, y_train_t, X_test_t, y_test_t, scaler, vectorizer, feature_names


def train_pulse_classifier(csv_path="test_pdw_sample.csv", epochs=100, batch_size=32, lr=1e-3):
    X_train_t, y_train_t, X_test_t, y_test_t, scaler, vectorizer, feature_names = \
        prepare_tensors(csv_path)

    num_classes = int(torch.cat([y_train_t, y_test_t]).max().item()) + 1
    input_dim = X_train_t.shape[1]

    train_loader = DataLoader(TensorDataset(X_train_t, y_train_t),
                               batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(TensorDataset(X_test_t, y_test_t), batch_size=batch_size)

    model = PulseClassifier(input_dim=input_dim, num_classes=num_classes)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)

    for epoch in range(epochs):
        model.train()
        running_loss = 0.0

        for xb, yb in train_loader:
            optimizer.zero_grad()
            outputs = model(xb)
            loss = criterion(outputs, yb)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()

        train_loss = running_loss / len(train_loader)

        if (epoch + 1) % 10 == 0 or epoch == 0:
            print(f"epoch = {epoch+1}/{epochs}, loss = {train_loss:.4f}")

    torch.save(model.state_dict(), WEIGHTS_PATH)
    print(f"Saved classifier weights to {WEIGHTS_PATH}")

    return model, test_loader


def evaluate_accuracy(model, test_loader):
    model.eval()
    correct, total = 0, 0
    all_preds, all_labels = [], []

    with torch.no_grad():
        for xb, yb in test_loader:
            outputs = model(xb)
            _, predicted = torch.max(outputs, 1)

            correct += (predicted == yb).sum().item()
            total += yb.size(0)

            all_preds.extend(predicted.tolist())
            all_labels.extend(yb.tolist())

    accuracy = correct / total * 100
    print("accuracy: ", accuracy)
    return accuracy, all_preds, all_labels


if __name__ == "__main__":
    model, test_loader = train_pulse_classifier()
    evaluate_accuracy(model, test_loader)
