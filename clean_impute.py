import pandas as pd
from datetime import datetime
# ==================== CLEANING FUNCTIONS ====================

def clean_price(df: pd.DataFrame) -> pd.DataFrame:
    '''
        - Dropping cars with no price 
        - Dropping cars worth less than 300k and more than 100m huf
    '''
    clean_df = df.copy()
    clean_df = clean_df.dropna(subset=['price'])
    clean_df = clean_df[(clean_df['price'] >= 300_000) & (clean_df['price'] <= 100_000_000)]

    return clean_df

def clean_year(df:pd.DataFrame) -> pd.DataFrame:
    '''
        - Dropping cars with no year 
        - Dropping cars manufactured before 2000
    '''
    clean_df = df.copy()
    clean_df = clean_df.dropna(subset=['year'])
    clean_df = clean_df[(clean_df['year'] >= 2000)]

    return clean_df

def clean_manufacturer_model(df:pd.DataFrame) -> pd.DataFrame:
    '''
        - Dropping cars without a manufacturer or model
        - Dropping cars with a manufacturer less than 10 cars in the db - 2 much noise
    '''
    clean_df = df.copy()
    clean_df = clean_df.dropna(subset=['model', 'manufacturer'])

    manufacturer_counts = clean_df['manufacturer'].value_counts()
    rare_manufacturers = manufacturer_counts[manufacturer_counts <= 10].index
    clean_df = clean_df[~clean_df['manufacturer'].isin(rare_manufacturers)]

    return clean_df

def clean_kilometers(df: pd.DataFrame) -> pd.DataFrame:
    '''
        - Dropping cars with more than 1 million kilometers on them
        - Cars without kilometers on them will be imputed + flagged ...
    '''
    clean_df = df.copy()
    clean_df = clean_df[clean_df['kilometers'] <= 1_000_000]
    
    return clean_df

def clean_fuel_type(df: pd.DataFrame) -> pd.DataFrame:
    '''
        - Dropping weird fuel types: 
            - LPG, CNG, Etanol
        - Merging gas variants into base
        - keeping hybrid seperate for now
    '''
    clean_df = df.copy()

    removable_gas_types = ['LPG', 'CNG', 'Etanol']
    clean_df = clean_df[~clean_df['fuel_type'].isin(removable_gas_types)]

    fuel_mapping = {
        'Benzin': 'Benzin',
        'Dízel' : 'Dízel',
        'Elektromos' : 'Elektromos',

        'Hibrid (Benzin)': 'Hibrid-Benzin',
        'Hibrid (Dízel)': 'Hibrid-Dízel',
        'Hibrid': 'Hibrid',
        
        'Benzin/Gáz': 'Benzin',
        'Dízel/Gáz': 'Dízel',
        'LPG/dízel' : 'Dízel',
        'Biodízel': 'Dízel',
    }
    clean_df['fuel_type'] = clean_df['fuel_type'].replace(fuel_mapping)

    return clean_df

def clean_kw_le(df: pd.DataFrame) -> pd.DataFrame:
    '''
        - Keeping only kw feature - dropping le since its redundant
        - Dropping unrealistic kw values
            - under 30
            - over 1000
        - Dropping NAN too hard to impute and its too crucial
    '''
    clean_df = df.copy()

    clean_df = clean_df.drop(columns=['le'])
    
    clean_df = clean_df[clean_df['kw'] >= 30]
    clean_df = clean_df[clean_df['kw'] <= 1000]
    clean_df = clean_df.dropna(subset=['kw'])
    
    return clean_df

def clean_condition(df: pd.DataFrame) -> pd.DataFrame:
    '''
        - Dropping missing conditions if any appear in the future
    '''
    clean_df = df.copy()
    clean_df = clean_df.dropna(subset=['condition'])

    return clean_df

def clean_trunk_capacity(df: pd.DataFrame) -> pd.DataFrame:
    '''
        - Dropping cars with high trunk capacity
            - x their body types capacity, generally 5x median
        Kisbusz: 15x median, huge differences
        Pickup: 5x median
        Kombi: 15x median, lot of minibuses here mistakenly
        Ferdehátú: 5x median
        Sedan: 5x median
        Városi terepjáró (crossover): 10x median
        Terepjáró: 10x median
        Cabrio: 5x median
        Coupe: 5x median
        Egyterű: 20x median
        Egyéb: 20x median
        Buggy: No data, keep all for the time being
        Hot rod: No data, keep all for the time being
        Modepautó: 5x median
        Sport: 5x median
        Lépcsőshátú: 5x median
    '''
    clean_df = df.copy()

    trunk_medians = clean_df.groupby('body_type')['trunk_capacity'].median()




# ==================== IMPUTING FUNCTIONS ====================

def impute_kilometers(df: pd.DataFrame) -> pd.DataFrame:
    '''
        - Imputing kilometers for cars which are missing them
        - Also flagging imputed values

        ~ Level 1: Same Manufacturer + Model + Year - median (if 5+ cars)
        ~ Level 2: Same Manufacturer + Model - median (if 10+ cars)
        ~ Level 3: Age based estimate - 15,000 km/year
    '''

    imputed_df = df.copy()
    imputed_df['km_imputed'] = imputed_df['kilometers'].isna().astype(int)
    
    # Level 1
    grouped = imputed_df.groupby(['manufacturer', 'model', 'year'])['kilometers'].transform('median')
    mask = imputed_df.groupby(['manufacturer', 'model', 'year'])['kilometers'].transform('count') >= 5
    imputed_df.loc[imputed_df['kilometers'].isna() & mask, 'kilometers'] = grouped[imputed_df['kilometers'].isna() & mask]
    
    # Level 2
    grouped = imputed_df.groupby(['manufacturer', 'model'])['kilometers'].transform('median')
    mask = imputed_df.groupby(['manufacturer', 'model'])['kilometers'].transform('count') >= 10
    imputed_df.loc[imputed_df['kilometers'].isna() & mask, 'kilometers'] = grouped[imputed_df['kilometers'].isna() & mask]
    
    # Level 3
    now = datetime.now()
    decimal_year = now.year + (now.month - 1) / 12
    decimal_year = round(decimal_year, 2)

    car_age = decimal_year  - imputed_df['year']
    car_age = car_age.clip(lower=0.0)
    imputed_df.loc[imputed_df['kilometers'].isna(), 'kilometers'] = car_age * 15000
    
    return imputed_df

def impute_fuel_type(df: pd.DataFrame) -> pd.DataFrame:
    '''
        - Missing fuel types - filled with Unknown
    '''
    imputed_df = df.copy()
    imputed_df['fuel_type'].fillna('Unknown', inplace=True)
    
    return imputed_df



def clean_features(df: pd.DataFrame) -> pd.DataFrame:
    clean_df = df.copy()
    



