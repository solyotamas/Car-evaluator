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
    imputed_df['fuel_type'] = imputed_df['fuel_type'].fillna('Unknown')
    
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
    imputed_df['trunk_capacity'] = imputed_df['trunk_capacity'].fillna(imputed_df['trunk_capacity'].median())
    
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
    
    imputed_df['seats'] = imputed_df['seats'].fillna(5)
    
    return imputed_df

def impute_color(df: pd.DataFrame) -> pd.DataFrame:
    '''
        - Missing color - filled with Unknown
    '''
    imputed_df = df.copy()
    imputed_df['color'] = imputed_df['color'].fillna('Unknown')
    
    return imputed_df

def impute_engine_capacity(df: pd.DataFrame) -> pd.DataFrame:
    '''
        - Imputing missing engine capacities based on kw correlation
    '''
    imputed_df = df.copy()
    '''
    car_id	kw	    engine_capacity
    1	    130	    1798
    2	    210	    2998
    3	    40	    NaN
    4	    340	    4998
    5	    111	    NaN
    '''
    kw_bins = pd.cut(imputed_df['kw'], bins=30, include_lowest=True)
    '''
    car_id	kw_bin
    1	(100, 200]
    2	(200, 300]
    3	(0, 100]
    4	(300, 400]
    5	(100, 200]
    '''
    kw_to_cc_map = imputed_df.groupby(kw_bins, observed=False)['engine_capacity'].median()
    '''
    kw_bin	median_engine_capacity
    (0, 100]	NaN*
    (100, 200]	1798.0
    (200, 300]	2998.0
    (300, 400]	4998.0
    '''
    imputed_values = kw_bins.map(kw_to_cc_map)

    imputed_df['engine_capacity'] = imputed_df['engine_capacity'].fillna(imputed_values)
    imputed_df['engine_capacity'] = imputed_df['engine_capacity'].fillna(imputed_df['kw'] * 15)

    return imputed_df

def impute_drive_type(df: pd.DataFrame) -> pd.DataFrame:
    '''
        - Missing drive type - filled with Unknown
    '''
    imputed_df = df.copy()
    imputed_df['drive_type'] = imputed_df['drive_type'].fillna('Unknown')
    
    return imputed_df

def impute_transmission_type(df: pd.DataFrame) -> pd.DataFrame:
    '''
        - Missing transmission type - filled with Unknown
        
        + leaving Nans in transmission subtype because it will be merged in engineer_transmission
    '''
    imputed_df = df.copy()
    imputed_df['transmission_type'] = imputed_df['transmission_type'].fillna('Unknown')
     
    return imputed_df

def impute_number_of_gears(df: pd.DataFrame) -> pd.DataFrame:
    '''
        - Imputing missing gears with transmission type median
    '''
    imputed_df = df.copy()
    
    gears_median = imputed_df.groupby('transmission_type')['number_of_gears'].median()
    imputed_df['number_of_gears'] = imputed_df['number_of_gears'].fillna(
        imputed_df['transmission_type'].map(gears_median)
    )
    
    mask = (imputed_df['transmission_type'] == 'Fokozatmentes automata') & \
           (imputed_df['number_of_gears'].isna())
    imputed_df.loc[mask, 'number_of_gears'] = 0
    
    # Unknown
    imputed_df['number_of_gears'] = imputed_df['number_of_gears'].fillna(5)

    print(f"Imputed {df['number_of_gears'].isna().sum()} missing gear values")
    
    return imputed_df

# ========================================

def table_impute(df: pd.DataFrame, text: bool = True) -> pd.DataFrame:
    """
        - Complete imputating for car data
    """
    if text:
        print("\nIMPUTING\n")

    imputation_steps = [
        ("kilometers", impute_kilometers),
        ("fuel type", impute_fuel_type),
        ("trunk capacity", impute_trunk_capacity),
        ("seats", impute_seats),
        ("color", impute_color),
        ("engine capacity", impute_engine_capacity),
        ("drive type", impute_drive_type),
        ("transmission type", impute_transmission_type),
        ("number of gears", impute_number_of_gears),
    ]
    
    for step_name, impute_func in imputation_steps:
        if 'kilometers' in step_name:
            missing_before = df['kilometers'].isna().sum()
        elif 'fuel' in step_name:
            missing_before = df['fuel_type'].isna().sum()
        elif 'trunk' in step_name:
            missing_before = df['trunk_capacity'].isna().sum()
        elif 'seats' in step_name:
            missing_before = df['seats'].isna().sum()
        elif 'color' in step_name:
            missing_before = df['color'].isna().sum()
        elif 'engine' in step_name:
            missing_before = df['engine_capacity'].isna().sum()
        elif 'drive' in step_name:
            missing_before = df['drive_type'].isna().sum()
        elif 'transmission type' in step_name:
            missing_before = df['transmission_type'].isna().sum()
        elif 'gears' in step_name:
            missing_before = df['number_of_gears'].isna().sum()
        
        df = impute_func(df)
        
        if text:
            print(f"{step_name}: imputed {missing_before} missing values")
    
    if text:
        print("-" * 50)
        print(f"Imputation complete")
        
        remaining_nan = df.isna().sum()
        if remaining_nan.sum() > 0:
            print("\nRemaining missing values:")
            for col, count in remaining_nan[remaining_nan > 0].items():
                print(f"  {col}: {count}")
    
    return df