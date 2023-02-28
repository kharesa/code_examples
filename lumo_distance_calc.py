import pandas as pd
import numpy as np
from pyproj import Transformer

# read in xlsx workbook sheet 'Distance_Matrix_Concat_Lumo' file into a dataframe
df = pd.read_excel('230203 First Rail_Lumo Distances.xlsx', sheet_name='Distance_Matrix_Concat_Lumo')
#prepping output dfs
df_transit = pd.DataFrame(columns=['route','OLat','OLon','DLat','DLon','mode'])
df_road = pd.DataFrame(columns=['route','OLat','OLon','DLat','DLon','mode'])

# define function to check for missing values and data types of each column
def check_missing_data_types(df):
    print("Missing values:\n", df.isnull().sum())
    print("\nData types:\n", df.dtypes)

# execute function to check for missing values and data types of each column
check_missing_data_types(df)

# define function to convert Easting and Northing coordinates into latitude longitude
def lat_lon_conversion(df):
    transformer = Transformer.from_crs('epsg:27700', 'epsg:4326') # define coordinate reference systems
    df[['O_Easting', 'O_Northing']] = pd.DataFrame(transformer.transform(df['O_Easting'].values, df['O_Northing'].values)).T
    df[['D_Easting', 'D_Northing']] = pd.DataFrame(transformer.transform(df['D_Easting'].values, df['D_Northing'].values)).T
    return df.rename(columns={'O_Easting': 'OLat', 'O_Northing': 'OLon', 'D_Easting': 'DLat', 'D_Northing':'DLon'}, inplace=True) # rename new columns

# execute function to convert Easting and Northing coordinates into latitude longitude and rename columns
df = lat_lon_conversion(df)


#loop through the dataframe
for index, row in df.iterrows():

    route = row["Concat"]
    OLat = row["OLat"]
    OLon = row["OLon"]
    DLat = row["DLat"]
    DLon = row["DLon"]
    
    
    if row['interchange_at'] == 'direct':
        print('Direct')
    else:
        if row['interchange_TUBE'] in ('', '-'):
            print('Only interchange with rail')
        else:
            print('Via London')


