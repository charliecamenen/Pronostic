from Equipe import Equipe
import pandas as pd

class CollectionEquipe:

    def __init__(self):
        self.collection_equipe = []

    def add(self, equipe):
        self.collection_equipe.append(equipe)

    def toDataFrame(self):
        headers = ['id_match', 'jour_semaine', 'date', 'heure', 'statut_match', 'dom_ext', 'saison',
                             'journee', 'competition', 'resultat', 'equipe', 'buts', 'classement', 'pts', 'joue',
                             'gagne', 'nul', 'perdu', 'bp', 'bc','diff','compo', 'cartons', 'changement', 'butteur', 'buts_mt']
        # création du dataframe
        return pd.DataFrame(self.collection_equipe, columns=headers)

    def cleanDataFrame(cls,df):
        # Suppression des doublons
        #df.drop_duplicates(keep='first', inplace=True)
        # Supprimer les étoiles
        df['equipe'] = df['equipe'].str.replace('*', '')
        # Supprimer les equipes nan
        df = df.loc[df['equipe'].isna() == False]
        return df

    cleanDataFrame = classmethod(cleanDataFrame)