import seaborn as sns
import matplotlib.pyplot as plt
#import pandas as pd

def afficher_matrice_correlation(df):
    plt.figure(figsize=(10,8))
    sns.heatmap(df.corr(numeric_only=True),annot=True,fmt=".2f",cmap="coolwarm")
    plt.title("Matrice corrélation fichier de base résultat matchs")
    plt.show()

def calculer_winrate_global(df_resultat_matchs):
    nb_victoires_domicile = df_resultat_matchs[df_resultat_matchs["results"]==1]["home_club_id"].value_counts()
    nb_nuls_domicile = df_resultat_matchs[df_resultat_matchs["results"]==0]["home_club_id"].value_counts()
    nb_matchs_domicile = df_resultat_matchs["home_club_id"].value_counts()

    nb_victoires_exterieur = df_resultat_matchs[df_resultat_matchs["results"]==-1]["away_club_id"].value_counts()
    nb_nuls_exterieur = df_resultat_matchs[df_resultat_matchs["results"]==0]["away_club_id"].value_counts()
    nb_matchs_exterieur = df_resultat_matchs["away_club_id"].value_counts()


    calcul_points = nb_victoires_domicile.add(nb_victoires_exterieur,fill_value=0) + 0.5*(nb_nuls_domicile.add(nb_nuls_exterieur,fill_value=0))
    nb_total_matchs = nb_matchs_domicile.add(nb_matchs_exterieur,fill_value=0)
    winrate_global = (calcul_points/nb_total_matchs).reset_index()
    winrate_global.columns = ["club_id","winrate_global"]
    return winrate_global