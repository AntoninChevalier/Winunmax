import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

def afficher_matrice_corrélation(df):
    plt.figure(figsize=(10,8))
    sns.heatmap(df.corr(numeric_only=True),annot=True,fmt=".2f",cmap="coolwarm")
    plt.title("Matrice corrélation fichier de base résultat matchs")
    plt.show()