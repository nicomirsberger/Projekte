import tensorflow as tf
import pandas as pd
from sklearn.model_selection import train_test_split

path = '/Users/student/Downloads/poker+hand/poker-hand-training-true.data'
data = pd.read_csv(path, delimiter=',')
print(data.head())

# Was soll vorhergesagt werden? Spaltenname in Variable speichern.
#col_name = 'species'

# Zeichenkette in Zahlen umwandeln
#data[col_name] = data[col_name].astype('category')
#data[col_name] = data[col_name].cat.codes

# Hier findet die Aufteilung in zwei Tabellen statt (Input=data und Output=col).
#col = data[col_name]
#data = data.drop([col_name], axis = 1)

# Aus den zwei Tabellen vier Tabellen erzeugen
#train_data, test_data, train_col, test_col = train_test_split(data,col, test_size=0.2)

# Aufbau KNN
#model = tf.keras.Sequential()
#model.add(tf.keras.Input(shape=(4,)))
#model.add(tf.keras.layers.Dense(32, activation=tf.nn.sigmoid))
#model.add(tf.keras.layers.Dense(64, activation=tf.nn.sigmoid))
#model.add(tf.keras.layers.Dense(3, activation=tf.nn.softmax))

# Konfiguration des Lernprozesses
#model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# 30 Durchläufe
#model.fit(train_data, train_col, epochs=30)

#test_loss, test_acc = model.evaluate(test_data, test_col)
#print('Test accuracy:', test_acc)