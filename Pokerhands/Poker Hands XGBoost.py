import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.metrics import accuracy_score, classification_report
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix


def load_and_sort_poker_data(file_path):
    print(f"Lade und transformiere Daten: {file_path}")
    columns = ['S1', 'C1', 'S2', 'C2', 'S3', 'C3', 'S4', 'C4', 'S5', 'C5', 'Label']
    df = pd.read_csv(file_path, header=None, names=columns)

    X_raw = df.iloc[:, 0:10].values
    y = df.iloc[:, 10].values
    X_reshaped = X_raw.reshape(-1, 5, 2)

    # Sortieren nach Kartenwert
    values = X_reshaped[:, :, 1]
    sort_idx = np.argsort(values, axis=1)
    X_sorted_reshaped = np.take_along_axis(X_reshaped, sort_idx[:, :, np.newaxis], axis=1)

    sorted_values = X_sorted_reshaped[:, :, 1]
    sorted_suits = X_sorted_reshaped[:, :, 0]

# --- FEATURE ENGINEERING ---
    # 1. Flush-Check: Wie viele Farben?
    unique_suits_count = np.array([len(np.unique(row)) for row in sorted_suits]).reshape(-1, 1)

    # 2. Straight-Check: Range und Unique Values
    value_range = (sorted_values[:, 4] - sorted_values[:, 0]).reshape(-1, 1)
    unique_values_count = np.array([len(np.unique(row)) for row in sorted_values]).reshape(-1, 1)

    # 3. Royal-Check: Ein Royal Flush startet immer bei 10
    min_value = sorted_values[:, 0].reshape(-1, 1)
    max_value = sorted_values[:, 4].reshape(-1, 1)


    def get_max_counts(row):
        _, counts = np.unique(row, return_counts=True)
        return np.max(counts)

    max_counts = np.array([get_max_counts(row) for row in sorted_values]).reshape(-1, 1)

    min_value = sorted_values[:, 0].reshape(-1, 1)
    max_value = sorted_values[:, 4].reshape(-1, 1)

# --- ZUSAMMENFÜHREN ---
    X_base = X_sorted_reshaped.reshape(-1, 10)
    X_engineered = np.hstack([
        X_base,
        unique_suits_count,
        value_range,
        unique_values_count,
        max_counts,
        min_value,
        max_value])


    return X_engineered, y


# --- HAUPTPROGRAMM ---
train_path = '/Users/student/Documents/poker+hand/poker-hand-training.data'
test_path = '/Users/student/Documents/poker+hand/poker-hand-testing.data'

try:
    X_train, y_train = load_and_sort_poker_data(train_path)
    X_test, y_test = load_and_sort_poker_data(test_path)

    model = xgb.XGBClassifier(
        n_estimators=500,
        max_depth=7,
        learning_rate=0.1,
        objective='multi:softmax',
        num_class=10,
        tree_method='hist',
        random_state=42
    )

    print(f"Starte Training...")
    model.fit(X_train, y_train)

    print(f"Starte Test...")
    y_pred = model.predict(X_test)
#--- Karten benennen für Plotausgabe ---
    hand_names = ["High card", "One pair", "Two pairs", "Three of a kind",
                  "Straight", "Flush", "Full house", "Four of a kind",
                  "Straight flush", "Royal flush"]
#--- Genauigkeit ausgeben ---
    print(f"\nGenauigkeit: {accuracy_score(y_test, y_pred) * 100:.2f}%")
    print(classification_report(y_test, y_pred, target_names=hand_names, zero_division=0))

# --- VISUALISIERUNG ---
    # Feature Importance
    feature_names = ['S1', 'C1', 'S2', 'C2', 'S3', 'C3', 'S4', 'C4', 'S5', 'C5',
                     'unique_suits', 'value_range', 'unique_vals', 'max_counts', 'min_val', 'max_val']

    plt.figure(figsize=(10, 6))
    feat_imp = pd.Series(model.feature_importances_, index=feature_names).sort_values()
    feat_imp.plot(kind='barh', color='teal')
    plt.title("Feature Importance")
    plt.show()

    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    cm_percent = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    plt.figure(figsize=(12, 10))
    sns.heatmap(cm_percent, annot=True, fmt='.2%', cmap='Blues', xticklabels=hand_names, yticklabels=hand_names)
    plt.show()

except FileNotFoundError as e:
    print(f"Datei nicht gefunden: {e}")

# Die Namen deiner 16 Features
all_possible_names = [
    'S1', 'C1', 'S2', 'C2', 'S3', 'C3', 'S4', 'C4', 'S5', 'C5',
    'unique_suits', 'value_range', 'unique_vals', 'max_counts',
    'min_val', 'max_val']

# Wichtigkeit abrufen
importance = model.feature_importances_

# SICHERHEITS-CHECK: Nur so viele Namen nehmen, wie das Modell Features hat
current_feature_names = all_possible_names[:len(importance)]

indices = np.argsort(importance)

plt.figure(figsize=(10, 6))
plt.title("Feature Importance")
plt.barh(range(len(indices)), importance[indices], align='center')


plt.yticks(range(len(indices)), [current_feature_names[i] for i in indices])

plt.xlabel('Relative Wichtigkeit')
plt.tight_layout()
plt.show()

# 1. Confusion Matrix berechnen
cm = confusion_matrix(y_test, y_pred)

# 2. Matrix normalisieren (um Prozente statt riesiger Zahlen zu sehen)
cm_percent = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

# 3. Plot erstellen
plt.figure(figsize=(12, 10))
sns.heatmap(cm_percent, annot=True, fmt='.2%', cmap='Blues',
            xticklabels=hand_names, yticklabels=hand_names)

plt.title('Wo liegen die Fehler? (Normalisierte Confusion Matrix)')
plt.ylabel('Tatsächliche Hand')
plt.xlabel('Vorhergesagte Hand')
plt.show()