import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

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

#Calculer le winrate pour un club donné sur les x dernières saisons avant saison_match
def calculer_winrate_club_classe(df_resultat_matchs, club_id, saison_match, x):
        saisons_precedentes = [saison_match - i for i in range(1, x + 1)]
        
        # Filtrer les matchs du club pendant ces saisons
        matchs_club = df_resultat_matchs[df_resultat_matchs['season'].isin(saisons_precedentes)]
        
        # Sélectionner les matchs à domicile et à l'extérieur pour ce club
        matchs_domicile = matchs_club[matchs_club["home_club_id"] == club_id]
        matchs_exterieur = matchs_club[matchs_club["away_club_id"] == club_id]
        
        # Calcul des victoires et nuls à domicile et à l'extérieur
        nb_victoires_domicile = matchs_domicile[matchs_domicile["results"] == 1].shape[0]
        nb_nuls_domicile = matchs_domicile[matchs_domicile["results"] == 0].shape[0]
        nb_victoires_exterieur = matchs_exterieur[matchs_exterieur["results"] == -1].shape[0]
        nb_nuls_exterieur = matchs_exterieur[matchs_exterieur["results"] == 0].shape[0]
        
        # Total des matchs joués
        total_matchs = matchs_domicile.shape[0] + matchs_exterieur.shape[0]
        
        # Calcul des points
        total_points = nb_victoires_domicile + nb_victoires_exterieur + 0.5 * (nb_nuls_domicile + nb_nuls_exterieur)
        
        # Si aucun match joué dans les saisons précédentes, on attribue un winrate par défaut
        if total_matchs == 0:
            return 0.35
        else:
            return total_points / total_matchs
        
def calcul_winrate_historique(df_resultat_matchs,x):
    winrates = []
    for index, row in df_resultat_matchs.iterrows():
        home_club_id = row['home_club_id']
        away_club_id = row['away_club_id']
        saison_match = row['season']
        
        # Calculer le winrate pour les deux clubs (domicile et extérieur) sur la période spécifiée
        winrate_home = calculer_winrate_club_classe(df_resultat_matchs, home_club_id, saison_match, x)
        winrate_away = calculer_winrate_club_classe(df_resultat_matchs, away_club_id, saison_match, x)
        
        # Ajouter les résultats au dataframe
        winrates.append((winrate_home, winrate_away))
    
    # Ajouter les colonnes de winrate pour home et away
    df_resultat_matchs['winrate_home '+str(x)+" ans"] = [w[0] for w in winrates]
    df_resultat_matchs['winrate_away '+str(x)+" ans"] = [w[1] for w in winrates]
    
    return df_resultat_matchs


def calculer_winrate_confrontation_directe(df_resultat_matchs, home_id, away_id, saison_match, x):
    saisons_precedentes = [saison_match - i for i in range(1, x + 1)]

    # Filtrer uniquement les confrontations entre les deux clubs sur les saisons précédentes
    confrontations = df_resultat_matchs[
        (df_resultat_matchs['season'].isin(saisons_precedentes)) &
        (
            ((df_resultat_matchs['home_club_id'] == home_id) & (df_resultat_matchs['away_club_id'] == away_id)) |
            ((df_resultat_matchs['home_club_id'] == away_id) & (df_resultat_matchs['away_club_id'] == home_id))
        )
    ]

    # Si aucun match n’a été joué entre les deux clubs, retour par défaut
    if confrontations.empty:
        return 0.5

    # Calcul des points pour home_id
    points_home = 0
    matchs_home = 0
    for _, match in confrontations.iterrows():
        if match['home_club_id'] == home_id:
            matchs_home += 1
            if match['results'] == 1:
                points_home += 1
            elif match['results'] == 0:
                points_home += 0.5
        elif match['away_club_id'] == home_id:
            matchs_home += 1
            if match['results'] == -1:
                points_home += 1
            elif match['results'] == 0:
                points_home += 0.5

    return points_home / matchs_home if matchs_home > 0 else 0.5


def ajout_winrate_confrontation_directe(df_resultat_matchs, x):
    winrate_confrontations = []
    for index, row in df_resultat_matchs.iterrows():
        home_id = row['home_club_id']
        away_id = row['away_club_id']
        saison = row['season']

        winrate_home_confrontation = calculer_winrate_confrontation_directe(df_resultat_matchs, home_id, away_id, saison, x)
        winrate_confrontations.append(winrate_home_confrontation)

    df_resultat_matchs['winrate_confrontation_home '+str(x)+' ans'] = winrate_confrontations
    return df_resultat_matchs






def calcul_market_value_sans_remplacant(df_composition_equipes,df_valeur_joueurs):
    #On va trier d’abord par player_id puis par date, mais également enlever les remplaçants du calcul de coût
    df_compo_triee = df_composition_equipes.sort_values(by=['player_id']).sort_values(by=["date"])
    df_compo_triee = df_compo_triee[df_compo_triee["type"] == "starting_lineup"]
    df_valeurs_triee = df_valeur_joueurs.sort_values(by=['player_id']).sort_values(by=["date"])

    df_compo_valeur = pd.merge_asof(df_compo_triee,df_valeurs_triee,on='date',by='player_id',direction='backward')
    df_valeur_equipes = df_compo_valeur.groupby(['game_id', 'club_id'])['market_value_in_eur'].sum().reset_index()
    df_valeur_equipes.rename(columns={'market_value_in_eur': 'team_market_value'}, inplace=True)

    return df_valeur_equipes

def calcul_difference_valorisation(df_matchs,df_composition_equipes,df_valeur_joueurs):
    df_valeur_equipes = calcul_market_value_sans_remplacant(df_composition_equipes,df_valeur_joueurs)
    df_valeur_home = df_valeur_equipes.rename(columns={"club_id": "home_club_id", "team_market_value": "home_team_value"})
    df_valeur_away = df_valeur_equipes.rename(columns={"club_id": "away_club_id", "team_market_value": "away_team_value"})

    df_matchs_valo = df_matchs.merge(df_valeur_home, on=["game_id", "home_club_id"], how="left")
    df_matchs_valo = df_matchs_valo.merge(df_valeur_away, on=["game_id", "away_club_id"], how="left")

    df_matchs_valo["home_team_value"] = df_matchs_valo["home_team_value"].fillna(22000000)
    df_matchs_valo["away_team_value"] = df_matchs_valo["away_team_value"].fillna(22000000)

    df_matchs_valo["Difference value home et away"] = df_matchs_valo["home_team_value"] - df_matchs_valo["away_team_value"]
    df_matchs_valo = df_matchs_valo.drop(columns=["home_team_value","away_team_value"])
    return df_matchs_valo


def calcul_ratio_valorisation(df_matchs,df_composition_equipes,df_valeur_joueurs):
    df_valeur_equipes = calcul_market_value_sans_remplacant(df_composition_equipes,df_valeur_joueurs)
    df_valeur_home = df_valeur_equipes.rename(columns={"club_id": "home_club_id", "team_market_value": "home_team_value"})
    df_valeur_away = df_valeur_equipes.rename(columns={"club_id": "away_club_id", "team_market_value": "away_team_value"})

    df_matchs_valo = df_matchs.merge(df_valeur_home, on=["game_id", "home_club_id"], how="left")
    df_matchs_valo = df_matchs_valo.merge(df_valeur_away, on=["game_id", "away_club_id"], how="left")

    df_matchs_valo["home_team_value"] = df_matchs_valo["home_team_value"].fillna(22000000)
    df_matchs_valo["away_team_value"] = df_matchs_valo["away_team_value"].fillna(22000000)

    df_matchs_valo["Ratio value home par away"] = df_matchs_valo["home_team_value"] / df_matchs_valo["away_team_value"]
    df_matchs_valo = df_matchs_valo.drop(columns=["home_team_value","away_team_value"])
    return df_matchs_valo

def calcul_log_ratio_valorisation(df_matchs,df_composition_equipes,df_valeur_joueurs):
    df_valeur_equipes = calcul_market_value_sans_remplacant(df_composition_equipes,df_valeur_joueurs)
    df_valeur_home = df_valeur_equipes.rename(columns={"club_id": "home_club_id", "team_market_value": "home_team_value"})
    df_valeur_away = df_valeur_equipes.rename(columns={"club_id": "away_club_id", "team_market_value": "away_team_value"})

    df_matchs_valo = df_matchs.merge(df_valeur_home, on=["game_id", "home_club_id"], how="left")
    df_matchs_valo = df_matchs_valo.merge(df_valeur_away, on=["game_id", "away_club_id"], how="left")

    df_matchs_valo["home_team_value"] = df_matchs_valo["home_team_value"].fillna(22000000)
    df_matchs_valo["away_team_value"] = df_matchs_valo["away_team_value"].fillna(22000000)

    df_matchs_valo["LOG Ratio value home par away"] = np.log(df_matchs_valo["home_team_value"] / df_matchs_valo["away_team_value"])
    df_matchs_valo = df_matchs_valo.drop(columns=["home_team_value","away_team_value"])
    return df_matchs_valo