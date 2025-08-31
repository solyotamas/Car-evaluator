import pandas as pd

class Engineer:
    def __init__(self):
        self.stats = {}

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        steps = [
            ("Fuel Type", engineer_fuel_type, 'fuel_type'),
            ("Transmission Type", engineer_transmission, 'transmission_type'),
            ("Color", engineer_color, 'color')
        ]

        for feature, func, column_name in steps:
            unique_before = df[column_name].nunique()
            df = func(df)
            unique_after = df[column_name].nunique()
            
            self.stats[feature] = {
                'unique_before': unique_before,
                'unique_after': unique_after
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
                'Unqiue Before': stats['unique_before'],
                'Unqiue After': stats['unique_after']
            })
        
        return pd.DataFrame(summary_df)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  

def engineer_fuel_type(df: pd.DataFrame) -> pd.DataFrame:
    '''
        - Merging weird gas variants to Unknown like ['LPG', 'CNG', 'Etanol']
        - Merging gas variants into base, mapping
        - keeping hybrid seperate for now
    '''
    engineered_df = df.copy()

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

    # Map everything not in the mapping to 'Unknown'
    engineered_df['fuel_type'] = engineered_df['fuel_type'].apply(
        lambda x: fuel_mapping.get(x, 'Unknown')
    )

    return engineered_df

def engineer_transmission(df: pd.DataFrame) -> pd.DataFrame:
    '''
        - Simplifying transmission types, merging subtype
    '''
    engineered_df = df.copy()
    

    mask = (engineered_df['transmission_type'] == 'Automata') & \
           (engineered_df['transmission_subtype'] == 'tiptronic')
    engineered_df.loc[mask, 'transmission_type'] = 'Automata tiptronic'
    
    engineered_df = engineered_df.drop(columns=['transmission_subtype'])
    
    
    transmission_mapping = {
        'Unknown' : 'Unknown',

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
    engineered_df['transmission_type'] = engineered_df['transmission_type'].replace(transmission_mapping)
     
    return engineered_df

def engineer_color(df: pd.DataFrame) -> pd.DataFrame:
    '''
        - Color split into two new features: 
            - color
            - metallic
        - metallic is 1 or 0
        - color is the color name without the (metál)
    '''
    engineered_df = df.copy()
    
    engineered_df['metallic'] = engineered_df['color'].str.contains('(metál)', na=False, regex=False).astype(int)
    engineered_df['color'] = engineered_df['color'].str.replace('(metál)', '', regex=False).str.strip()
    
    engineered_df.loc[engineered_df['color'] == '', 'color'] = 'Unknown'
    
    return engineered_df
