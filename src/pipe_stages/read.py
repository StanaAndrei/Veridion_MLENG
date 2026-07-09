import pandas as pd

def read(ifile):
    df = pd.read_json(ifile, lines=True)
    return df