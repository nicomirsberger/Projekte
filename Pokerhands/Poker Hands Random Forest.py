import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score


def load_data(file_path):
    # Spaltennamen definieren (Suit1, Rank1, ..., HandTyp)
    columns = ['S1', 'C1', 'S2', 'C2', 'S3', 'C3', 'S4', 'C4', 'S5', 'C5', 'Label']
    df = pd.read_csv(file_path, header=None, names=columns)

    # Feature Engineering Tipp: Die Karten sortieren
    # Warum? Ein Paar Asse an Position 1 & 2 ist dasselbe wie an Position 4 & 5.
    # Ohne Sortierung muss die KI jede Kombination einzeln lernen.

    # Wir trennen Features (X) und Zielwert (y)
    X = df.iloc[:, 0:10]
    y = df.iloc[:, 10]
    return X, y


# 1. Daten laden
print("Lade Trainingsdaten (25.000 Zeilen)...")
X_train, y_train = load_data('/Users/student/Downloads/poker+hand/poker-hand-training-true.data')

print("Lade Testdaten (1.000.000 Zeilen)...")
X_test, y_test = load_data('/Users/student/Downloads/poker+hand/poker-hand-testing.data')

# 2. Modell auswählen (Random Forest ist sehr gut für solche Tabellendaten)
# n_estimators=100 bedeutet wir nutzen 100 Entscheidungsbäume
model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)

# 3. Training starten
print("Training läuft... Bitte warten.")
model.fit(X_train, y_train)
print("Training abgeschlossen!")

# 4. Testen / Vorhersagen treffen
print("Vorhersage für 1.000.000 Testfälle wird erstellt...")
y_pred = model.predict(X_test)

# 5. Auswertung
accuracy = accuracy_score(y_test, y_pred)
print(f"\nGesamt-Genauigkeit: {accuracy * 100:.2f}%")

print("\nDetaillierter Bericht pro Pokerhand:")
# Da manche Hände im Testset extrem selten sind, nutzen wir zero_division=0
print(classification_report(y_test, y_pred, zero_division=0))