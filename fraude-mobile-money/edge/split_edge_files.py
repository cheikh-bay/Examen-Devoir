import os
import pandas as pd

# Dossier data
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")

# Charger le dataset original
df = pd.read_csv(os.path.join(DATA_DIR, "creditcard.csv"))

# Mélanger le dataset
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

# Découpage en 3 parties
n = len(df)
df_nouakchott = df[:n//3]
df_rosso = df[n//3:2*n//3]
df_kaedi = df[2*n//3:]

# Sauvegarde des fichiers Edge Nodes
df_nouakchott.to_csv(os.path.join(DATA_DIR, "transactions_nouakchott.csv"), index=False)
df_rosso.to_csv(os.path.join(DATA_DIR, "transactions_rosso.csv"), index=False)
df_kaedi.to_csv(os.path.join(DATA_DIR, "transactions_kaedi.csv"), index=False)

print("✅ Fichiers Edge Node créés avec succès !")
