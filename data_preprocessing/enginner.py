import pandas as pd

def engineer_fuel_type(df: pd.DataFrame) -> pd.DataFrame:
    '''
        - Merging weird gas variants to Unknown like ['LPG', 'CNG', 'Etanol']
        - Merging gas variants into base, mapping
        - keeping hybrid seperate for now
    '''
    engineered_df = df.copy()

    # mark_as_unknown = ['LPG', 'CNG', 'Etanol']
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
    #clean_df['fuel_type'] = clean_df['fuel_type'].replace(fuel_mapping)

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



def table_engineer(df: pd.DataFrame, text: bool = True) -> pd.DataFrame:
    """
        - Complete feature engineering for car data
    """
    if text:
        print("\nENGINEERING\n")
    engineered_df = df.copy()
    
    engineering_steps = [
        ("fuel_type", engineer_fuel_type),
        ("transmission_type", engineer_transmission),
        ("color", engineer_color),
    ]
    
    for step_name, engineer_func in engineering_steps:
        if text:
            print(f"{step_name}:")
            if step_name in engineered_df.columns:
                print(f"Before engineering, '{step_name}' has {engineered_df[step_name].nunique()} unique values.")

        engineered_df = engineer_func(engineered_df)
        
        if text:
            print(f"After engineering, '{step_name}' has {engineered_df[step_name].nunique()} unique values.")
            if step_name == "color":
                print(f"Also created a new column 'is_metallic'")

            print("-" * 50)
        
    return engineered_df