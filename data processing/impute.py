import pandas as pd
from datetime import datetime

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

def impute_trunk_capacity(df: pd.DataFrame) -> pd.DataFrame:
    '''
        - Imputing missing trunk capacities with body type median
    '''
    imputed_df = df.copy()
    
    trunk_medians = imputed_df.groupby('body_type')['trunk_capacity'].median()
    for body_type in trunk_medians.index:
        mask = (imputed_df['body_type'] == body_type) & (imputed_df['trunk_capacity'].isna())
        imputed_df.loc[mask, 'trunk_capacity'] = trunk_medians[body_type]
    

    # for like hot rod etc
    imputed_df['trunk_capacity'].fillna(imputed_df['trunk_capacity'].median(), inplace=True)
    
    print(f"Imputed {df['trunk_capacity'].isna().sum()} missing trunk capacities")
    
    return imputed_df

def impute_seats(df: pd.DataFrame) -> pd.DataFrame:
    '''
        - Imputing missing seats with body type median
    '''
    imputed_df = df.copy()
    
    seat_medians = imputed_df.groupby('body_type')['seats'].median()
    for body_type in seat_medians.index:
        mask = (imputed_df['body_type'] == body_type) & (imputed_df['seats'].isna())
        imputed_df.loc[mask, 'seats'] = seat_medians[body_type]
    
    imputed_df['seats'].fillna(5, inplace=True)
    
    print(f"Imputed {df['seats'].isna().sum()} missing seat values")
    
    return imputed_df

def impute_color(df: pd.DataFrame) -> pd.DataFrame:
    '''
        - Missing color - filled with Unknown
    '''
    imputed_df = df.copy()
    imputed_df['color'].fillna('Unknown', inplace=True)
    
    print(f"Filled {df['color'].isna().sum()} missing colors with 'Unknown'")
    
    return imputed_df


def impute_engine_capacity(df: pd.DataFrame) -> pd.DataFrame:
    imputed_df = df.copy()
    
    has_both = imputed_df[(imputed_df['kw'] > 0) & 
                          (imputed_df['engine_capacity'] > 0)]
    
    # kw max - kw min / 30
    has_both['kw_range'] = pd.cut(has_both['kw'], bins=30)
    kw_to_cc = has_both.groupby('kw_range')['engine_capacity'].median()
    
    missing_mask = imputed_df['engine_capacity'].isna()
    
    for idx in imputed_df[missing_mask].index:
        kw_val = imputed_df.loc[idx, 'kw']
        imputed = False
        
        # bucket
        for kw_range in kw_to_cc.index:
            if kw_val in kw_range:
                imputed_df.loc[idx, 'engine_capacity'] = kw_to_cc[kw_range]
                imputed = True
                break
        
        # fallback if no bucket
        if not imputed:
            imputed_df.loc[idx, 'engine_capacity'] = kw_val * 15
    
    return imputed_df


def impute_drive_type(df: pd.DataFrame) -> pd.DataFrame:
    '''
        - Missing drive type - filled with Unknown
    '''
    imputed_df = df.copy()
    imputed_df['drive_type'].fillna('Unknown', inplace=True)
    
    print(f"Filled {df['drive_type'].isna().sum()} missing drive types with 'Unknown'")
    
    return imputed_df


def impute_transmission_type(df: pd.DataFrame) -> pd.DataFrame:
    '''
        - Missing transmission type - filled with Unknown
    '''
    imputed_df = df.copy()
    
    imputed_df['transmission_type'].fillna('Unknown', inplace=True)
    
    print(f"Filled {df['transmission_type'].isna().sum()} missing transmission types with 'Unknown'")
    
    return imputed_df


def impute_number_of_gears(df: pd.DataFrame) -> pd.DataFrame:
    '''
        - Imputing missing gears with transmission type median
    '''
    imputed_df = df.copy()
    
    gears_median = imputed_df.groupby('transmission_type')['number_of_gears'].median()
    for trans_type in gears_median.index:
        if pd.notna(gears_median[trans_type]):
            mask = (imputed_df['transmission_type'] == trans_type) & \
                   (imputed_df['number_of_gears'].isna())
            imputed_df.loc[mask, 'number_of_gears'] = gears_median[trans_type]
    
    mask = (imputed_df['transmission_type'] == 'Fokozatmentes automata') & \
           (imputed_df['number_of_gears'].isna())
    imputed_df.loc[mask, 'number_of_gears'] = 0
    
    # Unknown
    imputed_df['number_of_gears'].fillna(5, inplace=True)

    print(f"Imputed {df['number_of_gears'].isna().sum()} missing gear values")
    
    return imputed_df

# ========================================

def table_impute(df: pd.DataFrame) -> pd.DataFrame:
    ...