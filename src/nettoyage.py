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

def calculer_classement_moyenne_club(df_resultat_matchs, club_id, saison_match, x):
    saisons_precedentes = [saison_match - i for i in range(1, x + 1)]

    # Filtrer les matchs du club pendant ces saisons
    matchs_club = df_resultat_matchs[df_resultat_matchs['season'].isin(saisons_precedentes)]
    
    # Séparer domicile et extérieur
    matchs_domicile = matchs_club[matchs_club["home_club_id"] == club_id]
    matchs_exterieur = matchs_club[matchs_club["away_club_id"] == club_id]

    # Récupérer les positions (NaN ignorés automatiquement par mean())
    positions = pd.concat([
        matchs_domicile["home_club_position"],
        matchs_exterieur["away_club_position"]
    ])

    if positions.empty:
        return 20.0  # Position moyenne par défaut
    else:
        return positions.mean()


def ajout_classement_moyen_historique(df_resultat_matchs, x):
    pos_moyennes = []
    for index, row in df_resultat_matchs.iterrows():
        home_club_id = row['home_club_id']
        away_club_id = row['away_club_id']
        saison = row['season']

        pos_home = calculer_classement_moyenne_club(df_resultat_matchs, home_club_id, saison, x)
        pos_away = calculer_classement_moyenne_club(df_resultat_matchs, away_club_id, saison, x)

        pos_moyennes.append((pos_home, pos_away))

    df_resultat_matchs['pos_moy_home_'+str(x)+'_ans'] = [p[0] for p in pos_moyennes]
    df_resultat_matchs['pos_moy_away_'+str(x)+'_ans'] = [p[1] for p in pos_moyennes]

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
    #df_matchs_valo = df_matchs_valo.drop(columns=["home_team_value","away_team_value"])
    return df_matchs_valo



def calcul_valorisation_flexible(df_matchs, df_compo, df_valeurs, methode="diff", valeur_par_defaut=22000000):
    def calcul_market_value_sans_remplacants(df_compo, df_valeurs):
        df_compo['date'] = pd.to_datetime(df_compo['date'])
        df_valeurs['date'] = pd.to_datetime(df_valeurs['date'])

        df = df_compo[df_compo['type'] == 'StartingXI'].merge(
            df_valeurs, on=['player_id'], suffixes=('', '_val')
        )

        df = df[df['date_val'] <= df['date']]
        df = df.sort_values('date_val').drop_duplicates(subset=['player_id', 'date'], keep='last')

        return df.groupby(['game_id', 'club_id'])['market_value_in_eur'].sum().reset_index().rename(columns={'market_value_in_eur': 'team_market_value'})

    df_valeurs_equipes = calcul_market_value_sans_remplacants(df_compo, df_valeurs)

    # On isole les valeurs de 2022 pour l'estimation de 2023 si besoin
    df_matchs_dates = df_matchs[['game_id', 'season', 'home_club_id', 'away_club_id']]
    valeurs_2022 = df_matchs_dates[df_matchs_dates['season'] == 2022].merge(
        df_valeurs_equipes, on=['game_id'], how='left'
    )
    moyennes_2022 = valeurs_2022.groupby('club_id')['team_market_value'].mean().fillna(valeur_par_defaut)

    # Ajout des valeurs home et away
    df_valeurs_home = df_valeurs_equipes.rename(columns={'club_id': 'home_club_id', 'team_market_value': 'home_team_value'})
    df_valeurs_away = df_valeurs_equipes.rename(columns={'club_id': 'away_club_id', 'team_market_value': 'away_team_value'})

    df = df_matchs.merge(df_valeurs_home, on=['game_id', 'home_club_id'], how='left')
    df = df.merge(df_valeurs_away, on=['game_id', 'away_club_id'], how='left')

    # Remplacement par moyenne 2022 si saison == 2023
    mask_2023 = df['season'] == 2023
    df.loc[mask_2023 & df['home_team_value'].isna(), 'home_team_value'] = df.loc[mask_2023, 'home_club_id'].map(moyennes_2022)
    df.loc[mask_2023 & df['away_team_value'].isna(), 'away_team_value'] = df.loc[mask_2023, 'away_club_id'].map(moyennes_2022)

    # Remplissage final si aucune info
    df['home_team_value'] = df['home_team_value'].fillna(valeur_par_defaut)
    df['away_team_value'] = df['away_team_value'].fillna(valeur_par_defaut)

    # Application de la méthode choisie
    if methode == "diff":
        df["Difference value home et away"] = df["home_team_value"] - df["away_team_value"]
        df = df.drop(columns=["home_team_value","away_team_value"])
    elif methode == "ratio":
        df["Ratio value home par away"] = df["home_team_value"] / df["away_team_value"]
        df = df.drop(columns=["home_team_value","away_team_value"])
    elif methode == "log_ratio":
        df["LOG Ratio value home par away"] = np.log(df["home_team_value"] / df["away_team_value"])
    else:
        raise ValueError("Méthode non reconnue : choisir 'diff', 'ratio' ou 'log_ratio'.")

    return df

import numpy as np

def remplir_valeurs_2023_depuis_2022(df):
    # Séparer les saisons
    df_2022 = df[df['season'] == 2022]
    df_2023 = df[df['season'] == 2023].copy()

    # Moyennes par club pour home et away en 2022
    moy_home = df_2022.groupby('home_club_id')[['home_team_value']].mean().rename(columns={"home_team_value": "home_team_value_2022"})
    moy_away = df_2022.groupby('away_club_id')[['away_team_value']].mean().rename(columns={"away_team_value": "away_team_value_2022"})

    # Merge des moyennes sur les lignes de 2023
    df_2023 = df_2023.merge(moy_home, on='home_club_id', how='left')
    df_2023 = df_2023.merge(moy_away, on='away_club_id', how='left')

    # Remplacement direct des valeurs par les moyennes
    df_2023['home_team_value'] = df_2023['home_team_value_2022'].fillna(30000000)
    df_2023['away_team_value'] = df_2023['away_team_value_2022'].fillna(30000000)

    # Calculs des ratios et log-ratios
    df_2023["Difference value home et away"] = df_2023["home_team_value"] - df_2023["away_team_value"]
    df_2023['Ratio value home par away'] = df_2023['home_team_value'] / df_2023['away_team_value']
    df_2023['LOG Ratio value home par away'] = np.log(df_2023['Ratio value home par away'])

    # Nettoyage
    df_2023.drop(columns=['home_team_value_2022', 'away_team_value_2022'], inplace=True)

    # Concat avec les autres saisons
    df_autres = df[df['season'] != 2023]
    df_final = pd.concat([df_autres, df_2023], ignore_index=True).sort_values(by='game_id')

    return df_final






def ajout_bool_nouveau_club(df):
    est_nouveau_home = []
    est_nouveau_away = []

    for idx, row in df.iterrows():
        saison_precedente = row['season'] - 1
        home_id = row['home_club_id']
        away_id = row['away_club_id']

        # Vérifie la présence du club à domicile l’année précédente
        home_a_joue = not df[((df['season'] == saison_precedente) & 
                              ((df['home_club_id'] == home_id) | (df['away_club_id'] == home_id)))].empty
        est_nouveau_home.append(0 if home_a_joue else 1)

        # Vérifie la présence du club à l’extérieur l’année précédente
        away_a_joue = not df[((df['season'] == saison_precedente) & 
                              ((df['home_club_id'] == away_id) | (df['away_club_id'] == away_id)))].empty
        est_nouveau_away.append(0 if away_a_joue else 1)

    df['nouveau club home'] = est_nouveau_home
    df['nouveau club away'] = est_nouveau_away

    return df

def ajout_bool_nouveau_club_multi_annees(df, x):
    est_nouveau_home = []
    est_nouveau_away = []

    for idx, row in df.iterrows():
        saison_courante = row['season']
        home_id = row['home_club_id']
        away_id = row['away_club_id']

        # Sélection des saisons à vérifier
        saisons_precedentes = [saison_courante - i for i in range(1, x+1)]

        # Vérifie si le club à domicile a joué au moins une fois dans les x saisons précédentes
        home_a_joue = not df[
            (df['season'].isin(saisons_precedentes)) &
            ((df['home_club_id'] == home_id) | (df['away_club_id'] == home_id))
        ].empty
        est_nouveau_home.append(0 if home_a_joue else 1)

        # Vérifie pour le club à l’extérieur
        away_a_joue = not df[
            (df['season'].isin(saisons_precedentes)) &
            ((df['home_club_id'] == away_id) | (df['away_club_id'] == away_id))
        ].empty
        est_nouveau_away.append(0 if away_a_joue else 1)

    df[f'nouveau club home {x} ans'] = est_nouveau_home
    df[f'nouveau club away {x} ans'] = est_nouveau_away

    return df



def calculer_diffbut_moyenne_club(df_resultat_matchs, club_id, saison_match, x):
    saisons_precedentes = [saison_match - i for i in range(1, x + 1)]

    # Filtrer les matchs du club pendant ces saisons
    matchs_club = df_resultat_matchs[df_resultat_matchs['season'].isin(saisons_precedentes)]
    
    # Séparer domicile et extérieur
    matchs_domicile = matchs_club[matchs_club["home_club_id"] == club_id]
    matchs_exterieur = matchs_club[matchs_club["away_club_id"] == club_id]

    #Calculer la différence de but

    if "home_club_goals" in matchs_domicile.columns and "away_club_goals" in matchs_domicile.columns:
        diffbut_dom = matchs_domicile["home_club_goals"] - matchs_domicile["away_club_goals"]
    else:
        diffbut_dom = pd.Series(dtype='float64')
    
    if "away_club_goals" in matchs_exterieur.columns and "home_club_goals" in matchs_exterieur.columns:
        diffbut_ext = matchs_exterieur["away_club_goals"] - matchs_exterieur["home_club_goals"]
    else:
        diffbut_ext = pd.Series(dtype='float64')

    # Concatener le tout
    diffbut = pd.concat([
        diffbut_dom,
        diffbut_ext
    ])

    if diffbut.empty:
        return 0
    else:
        return diffbut.mean()


def ajout_diffbut_moyen_historique(df_resultat_matchs, x):
    diffbut_moyennes = []
    for index, row in df_resultat_matchs.iterrows():
        home_club_id = row['home_club_id']
        away_club_id = row['away_club_id']
        saison = row['season']

        diffbut_home = calculer_diffbut_moyenne_club(df_resultat_matchs, home_club_id, saison, x)
        diffbut_away = calculer_diffbut_moyenne_club(df_resultat_matchs, away_club_id, saison, x)

        diffbut_moyennes.append((diffbut_home, diffbut_away))

    df_resultat_matchs['diffbut_moy_home_'+str(x)+'_ans'] = [p[0] for p in diffbut_moyennes]
    df_resultat_matchs['diffbut_moy_away_'+str(x)+'_ans'] = [p[1] for p in diffbut_moyennes]

    return df_resultat_matchs

def calculer_diffbut_moyenne_confrontation(df_resultat_matchs, club_id_home,club_id_away, saison_match, x):
    saisons_precedentes = [saison_match - i for i in range(1, x + 1)]

    # Filtrer les matchs du club pendant ces saisons
    matchs_confrontation = df_resultat_matchs[
    (df_resultat_matchs['season'].isin(saisons_precedentes)) & (
        ((df_resultat_matchs['home_club_id'] == club_id_home) & (df_resultat_matchs['away_club_id'] == club_id_away)) |
        ((df_resultat_matchs['home_club_id'] == club_id_away) & (df_resultat_matchs['away_club_id'] == club_id_home)))]


    if not all(col in matchs_confrontation.columns for col in ["home_club_goals", "away_club_goals"]):
        return 0

    matchs_domicile_clubdom = matchs_confrontation[matchs_confrontation["home_club_id"] == club_id_home]
    matchs_domicile_clubext = matchs_confrontation[matchs_confrontation["home_club_id"] == club_id_away ]

    diffbut_dom = matchs_domicile_clubdom["home_club_goals"]-matchs_domicile_clubdom["away_club_goals"]
    diffbut_ext = matchs_domicile_clubext["away_club_goals"]-matchs_domicile_clubext["home_club_goals"]

    # Concatener le tout
    diffbut = pd.concat([
        diffbut_dom,
        diffbut_ext
    ])

    if diffbut.empty:
        return 0
    else:
        return diffbut.mean()


def ajout_diffbut_moyenne_confrontation_historique(df_resultat_matchs, x):
    diffbut_moyennes = []
    for index, row in df_resultat_matchs.iterrows():
        home_club_id = row['home_club_id']
        away_club_id = row['away_club_id']
        saison = row['season']

        diffbut_confrontation = calculer_diffbut_moyenne_confrontation(df_resultat_matchs, home_club_id,away_club_id, saison, x)


        diffbut_moyennes.append(diffbut_confrontation)

    df_resultat_matchs['diffbut_moy_confrontation_'+str(x)+'_ans'] = diffbut_moyennes

    return df_resultat_matchs