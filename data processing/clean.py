import pandas as pd

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

    multipliers = {
        'Kisbusz': 15,
        'Pickup': 5,
        'Kombi': 15,
        'Ferdehátú': 5,
        'Sedan': 5,
        'Városi terepjáró (crossover)': 10,
        'Terepjáró': 10,
        'Cabrio': 5,
        'Coupe': 5,
        'Egyterű': 20,
        'Egyéb': 20,
        'Mopedautó': 5,
        'Sport': 5,
        'Lépcsőshátú': 5
    }
    
    # Apply threshold for each body type
    rows_to_drop = []
    for body_type, multiplier in multipliers.items():
        if body_type in trunk_medians.index and pd.notna(trunk_medians[body_type]):
            threshold = trunk_medians[body_type] * multiplier
            mask = (clean_df['body_type'] == body_type) & \
                    (clean_df['trunk_capacity'] > threshold)
            rows_to_drop.extend(clean_df[mask].index.tolist())
    
    # Drop the outliers
    clean_df = clean_df.drop(index=rows_to_drop)
    
    print(f"Removed {len(rows_to_drop)} cars with excessive trunk capacity")
    
    return clean_df

def clean_body_type(df: pd.DataFrame) -> pd.DataFrame:
    '''
        - Removing rare body types, 
    '''
    clean_df = df.copy()
    clean_df = clean_df.dropna(subset=['body_type'])
    
    
    rare_body_types = ['Hot rod', 'Buggy']
    clean_df = clean_df[~clean_df['body_type'].isin(rare_body_types)]
    
    print(f"Removed {len(df) - len(clean_df)} cars with missing or rare body types (Hot rod, Buggy)")
    
    return clean_df

def clean_seats(df: pd.DataFrame) -> pd.DataFrame:
    '''
        - Dropping cars with seats
            - more than 15
            - less than 2
        - Cars with missing seats will be imputed based on body type median and possibly a general 5 seat fallback
    '''
    clean_df = df.copy()
    
    clean_df = clean_df[(clean_df['seats'] >= 2) & (clean_df['seats'] <= 15)]
    
    print(f"Removed {len(df) - len(clean_df)} cars with seats <2 or >15")
    
    return clean_df

def clean_color(df: pd.DataFrame) -> pd.DataFrame:
    '''
        - Not doing anything here for now
        - Cars with missing color will be imputed with an Unknown category
        - Possible feature engineering into 2 seperate features in the future: base color and is_metallic
    '''
    clean_df = df.copy()
    
    return clean_df

def clean_engine_capacity(df: pd.DataFrame) -> pd.DataFrame:
    '''
        - Dropping cars
            - below 500cc
            - over 10 000 cc
        - Setting Electric car's cc to 0
        - Cars without engine capacity will be imputed based on kw correlation
    '''
    clean_df = df.copy()

    clean_df.loc[clean_df['fuel_type'] == 'Elektromos', 'engine_capacity'] = 0
    
    clean_df = clean_df[(clean_df['engine_capacity'] >= 500) | 
                        (clean_df['engine_capacity'] == 0) |
                        (clean_df['engine_capacity'].isna())]
    
    clean_df = clean_df[clean_df['engine_capacity'] <= 10000]
    
    print(f"Removed {len(df) - len(clean_df)} cars with invalid engine capacity")
    
    return clean_df

def clean_drive_type(df: pd.DataFrame) -> pd.DataFrame:
    '''
        - Not doing anything with them for now
        - Cars with missing drive types will be imputed with Unknown category
        - Could merge Állando osszkerek + Kapcsolhato osszekerek + osszkerek
            - maybe in the future
    '''
    clean_df = df.copy()
    
    return clean_df

def clean_transmission(df: pd.DataFrame) -> pd.DataFrame:
    '''
        - Simplifying transmission types, merging subtype
        - Cars with missing transmission types will be marked with Unknown
        - Cars with missing gearcount will be imputed with transmission type average
        - no dropping 
    '''
    clean_df = df.copy()
    

    mask = (clean_df['transmission_type'] == 'Automata') & \
           (clean_df['transmission_subtype'] == 'tiptronic')
    clean_df.loc[mask, 'transmission_type'] = 'Automata tiptronic'
    
    clean_df = clean_df.drop(columns=['transmission_subtype'])
    
    
    transmission_mapping = {
        'Manuális' : 'Manuális',
        'Automata' : 'Automata',
        'Fokozatmentes automata' : 'Fokozatmentes automata',
        'Automata tiptronic' : 'Automata tiptronic',
        'Szekvenciális' : 'Szekvenciális',

        'Automata felező váltóval': 'Automata',
        'Manuális felező váltóval': 'Manuális',
        'Fokozatmentes automata felező váltóval': 'Fokozatmentes automata',
        'Félautomata': 'Manuális',
        'Tiptronic': 'Automata tiptronic'
    }
    clean_df['transmission_type'] = clean_df['transmission_type'].replace(transmission_mapping)
    
    print(f"Simplified transmission types to: {clean_df['transmission_type'].nunique()} categories")
    
    return clean_df
# ========================================

def table_clean(df: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    """
        - Complete cleaning pipeline for car data
    """
    if verbose:
        print(f"Starting with {len(df)} cars")
        print("-" * 50)
    
    initial_count = len(df)
    
    # Track rows after each step for debugging
    cleaning_steps = [
        ("price", clean_price),
        ("year", clean_year),
        ("manufacturer/model", clean_manufacturer_model),
        ("kilometers", clean_kilometers),
        ("fuel type", clean_fuel_type),
        ("power (kw/le)", clean_kw_le),
        ("condition", clean_condition),
        ("trunk capacity", clean_trunk_capacity),
        ("body type", clean_body_type),
        ("seats", clean_seats),
        ("color", clean_color),
        ("engine capacity", clean_engine_capacity),
        ("drive type", clean_drive_type),
        ("transmission", clean_transmission),
    ]
    
    for step_name, clean_func in cleaning_steps:
        before = len(df)
        df = clean_func(df)
        after = len(df)
        
        if verbose and before != after:
            print(f"{step_name}: {before} → {after} (-{before-after})")
    
    if verbose:
        print("-" * 50)
        print(f"Final: {len(df)} cars ({len(df)/initial_count*100:.1f}% retained)")
    
    return df

# ======================

df = pd.read_csv('data/raw/car_details.csv')
df = table_clean(df = df)
df.to_csv('data/clean/car_details.csv', index=False)