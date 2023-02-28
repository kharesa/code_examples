import pandas as pd
import numpy as np
from pyproj import Transformer

# read in xlsx workbook sheet 'Distance_Matrix_Concat_Lumo' file into a dataframe
df = pd.read_excel('filename.xlsx', sheet_name='Distance_Matrix_Concat_Lumo')

# define function to check for missing values and data types of each column
def check_missing_data_types(df):
    print("Missing values:\n", df.isnull().sum())
    print("\nData types:\n", df.dtypes)

# execute function to check for missing values and data types of each column
check_missing_data_types(df)

# define function to convert Easting and Northing coordinates into latitude longitude
def lat_lon_conversion(df):
    transformer = Transformer.from_crs('epsg:27700', 'epsg:4326') # define coordinate reference systems
    df[['O_Lon', 'O_Lat']] = pd.DataFrame(transformer.transform(df['O_Easting'].values, df['O_Northing'].values)).T
    df[['D_Lon', 'D_Lat']] = pd.DataFrame(transformer.transform(df['D_Easting'].values, df['D_Northing'].values)).T
    df = df.drop(['O_Easting', 'O_Northing', 'D_Easting', 'D_Northing'], axis=1) # drop old columns
    return df.rename(columns={'O_Lon': 'O_Lon', 'O_Lat': 'O_Lat', 'D_Lon': 'D_Lon', 'D_Lat': 'D_Lat'}) # rename new columns

# execute function to convert Easting and Northing coordinates into latitude longitude and rename columns
df = lat_lon_conversion(df)
