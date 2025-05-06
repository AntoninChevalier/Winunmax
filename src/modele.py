from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import numpy as np
import pandas as pd


def affichage_complet_score(y_test,y_pred):
    print("\nAccuracy :", accuracy_score(y_test, y_pred))
    print("Precision :", precision_score(y_test, y_pred, average='macro'))
    print("Recall :", recall_score(y_test, y_pred, average='macro'))
    print("F1 Score :", f1_score(y_test, y_pred, average='macro'))
    print("Matrice de confusion :\n", confusion_matrix(y_test, y_pred))


#Prédiction simple basé sur le signe de la différence
def prediction_modele_simple(diff_series):
    diff_values = diff_series.values
    pred = np.zeros_like(diff_values)
    pred[diff_values > 1] = -1
    pred[diff_values < -1] = 1
    return pd.Series(pred, index=diff_series.index)