from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import numpy as np
import pandas as pd
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt


def affichage_complet_score(y_test,y_pred):
    """print("\nAccuracy :", accuracy_score(y_test, y_pred))
    print("Precision :", precision_score(y_test, y_pred, average='macro'))
    print("Recall :", recall_score(y_test, y_pred, average='macro'))
    print("F1 Score :", f1_score(y_test, y_pred, average='macro'),"(pondéré:",f1_score(y_test, y_pred, average='weighted'),")")
    print("Matrice de confusion :\n", confusion_matrix(y_test, y_pred))"""

    cm = confusion_matrix(y_test, y_pred, labels=[-1, 0, 1])
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["Defaite (-1)", "Nul (0)", "Victoire (1)"])

    # Création figure avec 2 zones : matrice à gauche, texte à droite
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 3), gridspec_kw={'width_ratios': [1,1]})

    # Affichage matrice
    disp.plot(ax=ax1, cmap="Blues", values_format='d', colorbar=False)
    for texts in disp.text_.ravel():
        texts.set_fontsize(13)
    ax1.set_title("Matrice de confusion", fontsize=14)

    # Texte explicatif à droite
    ax2.axis("off")  # Pas d'axes visibles
    
    y_test = np.array(y_test)
    y_pred = np.array(y_pred)
    total = len(y_test)
    prediction_opposee = np.sum(((y_test == -1) & (y_pred == 1)) | ((y_test == 1) & (y_pred == -1))) / total

    text = (classification_report(y_test, y_pred, target_names=["-1", "0", "1"],digits=3,zero_division=0))
    text = text + f"\n\n\nTaux predictions opposees : {prediction_opposee:.2%}"
    ax2.text(1, 1, text, fontsize=11, va="top",ha="right")

    plt.tight_layout()
    plt.show()

def affichage_matrice_confusion(Y_pred,Y_test):
    cm = confusion_matrix(Y_test, Y_pred, labels=[-1, 0, 1])
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["Defaite (-1)", "Nul (0)", "Victoire (1)"])

    # Création figure avec 2 zones : matrice à gauche, texte à droite
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7, 4), gridspec_kw={'width_ratios': [3, 2]})

    # Affichage matrice
    disp.plot(ax=ax1, cmap="Blues", values_format='d', colorbar=False)
    ax1.set_title("Matrice de confusion", fontsize=14)

    # Texte explicatif à droite
    ax2.axis("off")  # Pas d'axes visibles
    text = (
        "📊 Analyse :\n"
        "- Bonne détection des victoires.\n"
        "- Quelques confusions entre nuls et défaites.\n"
        "- F1 score plus faible pour classe 'nul'.\n"
    )
    ax2.text(0, 0.8, text, fontsize=12, va='top')

    plt.tight_layout()
    plt.show()

#Prédiction simple basé sur le signe de la différence
def prediction_modele_simple_diff_position(diff_series):
    diff_values = diff_series.values
    pred = np.zeros_like(diff_values)
    pred[diff_values > 1] = -1
    pred[diff_values < -1] = 1
    return pd.Series(pred, index=diff_series.index)

def prediction_modele_simple_diff_winrate(diff_series):
    diff_values = diff_series.values
    pred = np.zeros_like(diff_values)
    pred[diff_values > 0.05] = 1
    pred[diff_values < -0.05] = -1
    return pd.Series(pred, index=diff_series.index)