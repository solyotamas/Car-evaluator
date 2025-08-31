import pandas as pd
from datetime import datetime

class Imputer:
    def __init__(self, **kwargs):
        
        self.km_per_year = kwargs.get('km_per_year_', 15_000)
        self.km_age_only = kwargs.get('km_age_only', False)
        self.default_seats = kwargs.get('default_seats', 5)
        self.default_gears = kwargs.get('default_gears', 5)

        self.stats = {}

    def impute(self, df: pd.DataFrame) -> pd.DataFrame:

        steps = [
            ("Kilometers", impute_kilometers, 'kilometers', self.km_per_year, self.km_age_only),
            ("Fuel Type", impute_fuel_type, 'fuel_type'),
            ("Trunk Capacity", impute_trunk_capacity, 'trunk_capacity'),
            ("Seats", impute_seats, 'seats', self.default_seats),
            ("Color", impute_color, 'color'),
            ("Engine Capacity", impute_engine_capacity, 'engine_capacity'),
            ("Drive Type", impute_drive_type, 'drive_type'),
            ("Transmission Type", impute_transmission_type, 'transmission_type'),
            ("Number of Gears", impute_number_of_gears, 'number_of_gears', self.default_gears),
        ]
        
        for feature, func, column_name, *params in steps:
            missing_before = df[column_name].isna().sum()
            df = func(df, *params)
            missing_after = df[column_name].isna().sum()
            
            self.stats[feature] = {
                'missing_before': missing_before,
                'missing_after': missing_after,
                'imputed': missing_before - missing_after
            }
            
        
        return df
    
    def get_stats(self) -> dict:
        return self.stats
    
    def get_summary(self) -> pd.DataFrame:
        if not self.stats:
            return pd.DataFrame()
        
        summary_df = []
        for feature, stats in self.stats.items():
            summary_df.append({
                'Feature': feature,
                'Missing Before': stats['missing_before'],
                'Missing After': stats['missing_after'],
                'Imputed': stats['imputed']
            })
        
        return pd.DataFrame(summary_df)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~   
    
def impute_kilometers(df: pd.DataFrame, km_per_year: int = 15_000, km_age_only : bool = False) -> pd.DataFrame:
    '''
        - Imputing kilometers for cars which are missing them
        - Also flagging imputed values

        ~ Level 1: Same Manufacturer + Model + Year - median (if 5+ cars)
        ~ Level 2: Same Manufacturer + Model - median (if 10+ cars)
        ~ Level 3: Age based estimate - 'km_per_year' * age
    '''

    imputed_df = df.copy()
    imputed_df['km_imputed'] = imputed_df['kilometers'].isna().astype(int)
    
    # Level 1
    if not km_age_only:
        grouped = imputed_df.groupby(['manufacturer', 'model', 'year'])['kilometers'].transform('median')
        mask = imputed_df.groupby(['manufacturer', 'model', 'year'])['kilometers'].transform('count') >= 5
        imputed_df.loc[imputed_df['kilometers'].isna() & mask, 'kilometers'] = grouped[imputed_df['kilometers'].isna() & mask]
    
    # Level 2
    if not km_age_only:
        grouped = imputed_df.groupby(['manufacturer', 'model'])['kilometers'].transform('median')
        mask = imputed_df.groupby(['manufacturer', 'model'])['kilometers'].transform('count') >= 10
        imputed_df.loc[imputed_df['kilometers'].isna() & mask, 'kilometers'] = grouped[imputed_df['kilometers'].isna() & mask]
    
    # Level 3
    now = datetime.now()
    decimal_year = now.year + (now.month - 1) / 12
    decimal_year = round(decimal_year, 2)

    car_age = decimal_year  - imputed_df['year']
    car_age = car_age.clip(lower=0.0)
    imputed_df.loc[imputed_df['kilometers'].isna(), 'kilometers'] = car_age * km_per_year
    
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

def impute_seats(df: pd.DataFrame, default_seats : int = 5) -> pd.DataFrame:
    '''
        - Imputing missing seats with body type median
    '''
    imputed_df = df.copy()
    
    seat_medians = imputed_df.groupby('body_type')['seats'].median()
    for body_type in seat_medians.index:
        mask = (imputed_df['body_type'] == body_type) & (imputed_df['seats'].isna())
        imputed_df.loc[mask, 'seats'] = seat_medians[body_type]
    
    imputed_df['seats'] = imputed_df['seats'].fillna(default_seats)
    
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

def impute_number_of_gears(df: pd.DataFrame, default_gears = 5) -> pd.DataFrame:
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
    imputed_df['number_of_gears'] = imputed_df['number_of_gears'].fillna(default_gears)

    return imputed_df
