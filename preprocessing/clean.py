import pandas as pd

class Cleaner:

    def __init__(self, **kwargs):
        self.price_lower = kwargs.get('price_lower', 200_000)
        self.price_upper = kwargs.get('price_upper', 100_000_000)
        self.year_lower = kwargs.get('year_lower', 2000)
        self.year_upper = kwargs.get('year_upper', None)
        self.manufacturer_min_count = kwargs.get('manufacturer_min_count', 10)
        self.km_upper = kwargs.get('km_threshold', 1_000_000)
        self.kw_lower = kwargs.get('kw_lower', 30)
        self.kw_upper = kwargs.get('kw_upper', 1000)
        self.seats_lower = kwargs.get('seats_lower', 2)
        self.seats_upper = kwargs.get('seats_upper', 15)
        self.engine_lower = kwargs.get('engine_lower', 500)
        self.engine_upper = kwargs.get('engine_upper', 10_000)

        self.stats = {}

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:

        steps = [
            ("Price", clean_price, self.price_lower, self.price_upper),
            ("Year", clean_year, self.year_lower, self.year_upper),
            ("Manufacturer/Model", clean_manufacturer_model, self.manufacturer_min_count),
            ("Kilometers", clean_kilometers, self.km_upper),
            ("Fuel Type", clean_fuel_type),
            ("KW/LE", clean_kw_le, self.kw_lower, self.kw_upper),
            ("Condition", clean_condition),
            ("Trunk Capacity", clean_trunk_capacity),
            ("Body Type", clean_body_type),
            ("Seats", clean_seats, self.seats_lower, self.seats_upper),
            ("Color", clean_color),
            ("Engine Capacity", clean_engine_capacity, self.engine_lower, self.engine_upper),
            ("Drive Type", clean_drive_type),
            ("Transmission", clean_transmission),
        ]


        
        for feature, func, *params in steps:
            length_before = len(df)
            df = func(df, *params)
            length_after = len(df)

            self.stats[feature] = {
                'length_before': length_before,
                'length_after': length_after,
                'dropped': length_before - length_after
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
                'Length Before': stats['length_before'],
                'Length After': stats['length_after'],
                'Dropped': stats['dropped']
            })
        
        return pd.DataFrame(summary_df)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def clean_price(df: pd.DataFrame, lower: int = 200_000, upper: int = 100_000_000) -> pd.DataFrame:
    '''
        - Dropping cars:
            - without price
            - cheaper than 'lower' parameter
            - more expensive than 'upper' paramter
    '''
    clean_df = df.copy()
    clean_df = clean_df.dropna(subset=['price'])
    clean_df = clean_df[(clean_df['price'] >= lower) & (clean_df['price'] <= upper)]

    return clean_df

def clean_year(df:pd.DataFrame, lower: int = 2000, upper: int = None) -> pd.DataFrame:
    '''
        - Dropping cars:
            - without year
            - older than 'lower' parameter
            - newer than 'upper' parameter
    '''
    clean_df = df.copy()
    clean_df = clean_df.dropna(subset=['year'])
    clean_df = clean_df[(clean_df['year'] >= lower)]

    if upper is not None:
        clean_df = clean_df[clean_df['year'] <= upper]

    return clean_df

def clean_manufacturer_model(df:pd.DataFrame, manufacturer_minimum_car_count: int = 10) -> pd.DataFrame:
    '''
        - Dropping cars: 
            - without manufacturer
            - without model
            - with a manufacturer who has less than 'manufacturer_minimum_car_count' cars in the db
                ~ too much noise
    '''
    clean_df = df.copy()
    clean_df = clean_df.dropna(subset=['model', 'manufacturer'])

    manufacturer_counts = clean_df['manufacturer'].value_counts()
    rare_manufacturers = manufacturer_counts[manufacturer_counts <= manufacturer_minimum_car_count].index
    clean_df = clean_df[~clean_df['manufacturer'].isin(rare_manufacturers)]

    return clean_df

def clean_kilometers(df: pd.DataFrame, km_upper: int = 1_000_000) -> pd.DataFrame:
    '''
        - Dropping cars:
            - with more than 'km_upper' kilometers

        + Cars without kilometers on them will be imputed + flagged
    '''
    clean_df = df.copy()
    clean_df = clean_df[(clean_df['kilometers'] <= km_upper) | 
                        (clean_df['kilometers'].isna())]


    return clean_df

def clean_fuel_type(df: pd.DataFrame) -> pd.DataFrame:
    '''
        - Dropping cars:
            - None

        + Will impute missing with Unknown
        + Will feature engineer, merge weird variants
    '''
    clean_df = df.copy()

    return clean_df

def clean_kw_le(df: pd.DataFrame, lower: int = 30, upper: int = 1000) -> pd.DataFrame:
    '''
        - Keeping only kw feature - dropping le since its redundant
        - Dropping cars:
            - without kw feature ~ too hard to impute and its crucial price determiner
            - under 'lower' kw
            - over 'upper' kw
    '''
    clean_df = df.copy()

    clean_df = clean_df.drop(columns=['le'])

    clean_df = clean_df.dropna(subset=['kw'])
    clean_df = clean_df[clean_df['kw'] >= lower]
    clean_df = clean_df[clean_df['kw'] <= upper]
    
    return clean_df

def clean_condition(df: pd.DataFrame) -> pd.DataFrame:
    '''
        - Dropping cars:
            - without condition
    '''
    clean_df = df.copy()
    clean_df = clean_df.dropna(subset=['condition'])

    return clean_df

def clean_trunk_capacity(df: pd.DataFrame) -> pd.DataFrame:
    '''
        - Dropping cars: 
            - with high trunk capacity
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

        + Will impute missing trunk capacity based on body type median
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
    
    rows_to_drop = []
    for body_type, multiplier in multipliers.items():
        if body_type in trunk_medians.index and pd.notna(trunk_medians[body_type]):
            threshold = trunk_medians[body_type] * multiplier
            mask = (clean_df['body_type'] == body_type) & \
                    (clean_df['trunk_capacity'] > threshold)
            rows_to_drop.extend(clean_df[mask].index.tolist())
    
    clean_df = clean_df.drop(index=rows_to_drop)

    return clean_df

def clean_body_type(df: pd.DataFrame) -> pd.DataFrame:
    '''
        - Dropping cars:
            - without a body type
            - with an extremely rare body type
    '''
    clean_df = df.copy()
    clean_df = clean_df.dropna(subset=['body_type'])
    
    
    rare_body_types = ['Hot rod', 'Buggy']
    clean_df = clean_df[~clean_df['body_type'].isin(rare_body_types)]

    return clean_df

def clean_seats(df: pd.DataFrame, lower:int = 2, upper: int = 15) -> pd.DataFrame:
    '''
        - Dropping cars: 
            - with more seats than 'upper'
            - with less seats than 'lower'

        + Cars with missing seats will be imputed based on body type median
    '''
    clean_df = df.copy()
    clean_df = clean_df[((clean_df['seats'] >= 2) & (clean_df['seats'] <= 15)) | 
                        (clean_df['seats'].isna())]
    
    return clean_df

def clean_color(df: pd.DataFrame) -> pd.DataFrame:
    '''
        - Dropping cars:
            - None

        + Cars with missing color will be imputed with an Unknown category
        + Possible feature engineering into 2 seperate features in the future: base color and is_metallic
    '''
    clean_df = df.copy()

    return clean_df

def clean_engine_capacity(df: pd.DataFrame, lower: int = 500, upper: int = 10_000) -> pd.DataFrame:
    '''
        - Dropping cars: 
            - below 'lower' cc
            - over 'upper' cc
        - Setting Electric car's cc to 0

        + Cars without engine capacity will be imputed based on kw correlation
    '''
    clean_df = df.copy()

    clean_df.loc[clean_df['fuel_type'] == 'Elektromos', 'engine_capacity'] = 0 

    valid_range = ((clean_df['engine_capacity'] >= lower) & (clean_df['engine_capacity'] <= upper))
    keep_rows = (valid_range | (clean_df['engine_capacity'] == 0) | (clean_df['engine_capacity'].isna()))

    clean_df = clean_df[keep_rows]
    
    return clean_df

def clean_drive_type(df: pd.DataFrame) -> pd.DataFrame:
    '''
        - Dropping cars:
            - None

        + Cars with missing drive types will be imputed with Unknown category
        + Could merge Állando osszkerek + Kapcsolhato osszekerek + osszkerek
            + maybe in the future
    '''
    clean_df = df.copy()

    return clean_df

def clean_transmission(df: pd.DataFrame) -> pd.DataFrame:
    '''
        - Dropping cars:
            - None

        + Will be simplifying transmission types, merging subtype
        + Cars with missing transmission types will be marked with Unknown
        + Cars with missing gearcount will be imputed with transmission type average 
    '''
    clean_df = df.copy()
     
    return clean_df

