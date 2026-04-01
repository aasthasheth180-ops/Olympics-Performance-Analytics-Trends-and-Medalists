import pandas as pd

def preprocess(athletes_df, region_df):
    # merge with region_df
    df = athletes_df.merge(region_df, on='NOC', how='left')
    # dropping duplicates
    df.drop_duplicates(inplace=True)
    # one hot encoding medals
    df = pd.concat([df, pd.get_dummies(df['Medal'])], axis=1)
    
    # Ensure columns exist to prevent errors if a season has no medals of a certain type
    for medal in ['Gold', 'Silver', 'Bronze']:
        if medal not in df.columns:
            df[medal] = 0
            
    return df


