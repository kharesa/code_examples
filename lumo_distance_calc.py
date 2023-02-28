import pandas as pd
import numpy as np
from pyproj import Transformer
import geocoder # pip install geocoder
import geopy
from geopy.geocoders import Nominatim

# define function to check for missing values and data types of each column
def check_missing_data_types(df):
    print("Missing values:\n", df.isnull().sum())
    print("\nData types:\n", df.dtypes)


# define function to convert Easting and Northing coordinates into latitude longitude
def lat_lon_conversion(df):
    transformer = Transformer.from_crs('epsg:27700', 'epsg:4326') # define coordinate reference systems
    df[['O_Easting', 'O_Northing']] = pd.DataFrame(transformer.transform(df['O_Easting'].values, df['O_Northing'].values)).T
    df[['D_Easting', 'D_Northing']] = pd.DataFrame(transformer.transform(df['D_Easting'].values, df['D_Northing'].values)).T
    return df.rename(columns={'O_Easting': 'OLat', 'O_Northing': 'OLon', 'D_Easting': 'DLat', 'D_Northing':'DLon'}, inplace=True) # rename new columns


def looper(df, df_transit, df_road):
    #loop through the dataframe
    for index, row in df.iterrows():

        route = str(row["Concat"])
        OLat = row["OLat"]
        OLon = row["OLon"]
        DLat = row["DLat"]
        DLon = row["DLon"]

        #filling out driving table
        df_road = df_road.append(
        {'OLon': OLon, 
        'OLat': OLat, 
        'DLon': DLon, 
        'DLat': DLat,
        'mode': 'driving',
        'route': route,
        'origin_station': row['O_Station'],
        'destination_station': row['D_Station']
        }, ignore_index=True)


        if row['Interchange_at'] == 'direct':
            
            df_transit = df_transit.append(
            {'OLon': OLon, 
            'OLat': OLat, 
            'DLon': DLon, 
            'DLat': DLat, 
            'route': route, 
            'origin_station': row['O_Station'],
            'destination_station': row['D_Station']
            }, ignore_index=True)

        else:
            if row['Interchange_TUBE'] in ('', '-'):
                #if no value for tube interchange

                #origin to interchange
                    #get interchange coords and set them as the destination
                DLat, DLon = get_origin_station_coords(df, str(row['Interchange_at']))

                #fill in the row in df_transit
                df_transit = df_transit.append(
                {'OLon': OLon, 
                'OLat': OLat, 
                'DLon': DLon, 
                'DLat': DLat, 
                'route': route,
                'leg': (route+'_1'), 
                'origin_station': row['O_Station'],
                'destination_station': row['Interchange_at']
                }, ignore_index=True)

                #interchange to destination
                    #get destination lat
                DLat, DLon = get_destination_station_coords(df, str(row['D_Station']))

                df_transit = df_transit.append(
                {'OLon': OLon, 
                'OLat': OLat, 
                'DLon': DLon,
                'DLat': DLat, 
                'route': route,
                'leg': (route+'_2'), 
                'origin_station': str(row['Interchange_at']),
                'destination_station': str(row['D_Station'])
                }, ignore_index=True)

            else:
                print('Via London')

                #origin to interchange
                    #get interchange coords
                DLat, DLon = get_origin_station_coords(df, str(row['Interchange_at']))

                #fill in the row in df_transit
                df_transit = df_transit.append(
                {'OLon': OLon, 
                'OLat': OLat, 
                'DLon': DLon, 
                'DLat': DLat, 
                'route': route,
                'leg': (route+'_1'), 
                'origin_station': row['O_Station'],
                'destination_station': row['Interchange_at']
                }, ignore_index=True)

                #interchange to tube interchange
                OLat, OLon = get_origin_station_coords(df, str(row['Interchange_at']))
                latt, lonn = get_tube_station_coords(df, str(row['Interchange_TUBE']))


                df_transit = df_transit.append(
                {'OLon': OLon, 
                'OLat': OLat, 
                'DLon': lonn,
                'DLat': latt, 
                'route': route,
                'leg': (route+'_2'), 
                'origin_station': str(row['Interchange_at']),
                'destination_station': str(row['Interchange_TUBE'])
                }, ignore_index=True)


                #get destination lat
                DLat, DLon = get_destination_station_coords(df, str(row['D_Station']))

                df_transit = df_transit.append(
                {'OLon': lonn, 
                'OLat': latt, 
                'DLon': DLon,
                'DLat': DLat, 
                'route': route,
                'leg': (route+'_3'), 
                'origin_station': str(row['Interchange_TUBE']),
                'destination_station': str(row['D_Station'])
                }, ignore_index=True)
            
    return df, df_transit, df_road



def get_origin_station_coords(df, lookup_val):
    row=df.loc[df['Interchange_at']==lookup_val]
    lat = row.iloc[0]['OLat']
    lon = row.iloc[0]['OLon']
    return lat, lon

def get_destination_station_coords(df, lookup_val):
    row=df.loc[df['D_Station']==lookup_val]
    lat = row.iloc[0]['DLat']
    lon = row.iloc[0]['DLon']
    return lat, lon

def get_tube_station_coords(df, lookup_val):
    #create the station name to look up
    station_name = 'London '+lookup_val+' Station, Greater London, UK'

    try:
        #passing the station name to Nominatim to return location data from OSM
        geolocator = Nominatim(user_agent='myapplication')
        location = geolocator.geocode(station_name)
        
        #returns a dict of location details 
        loc_dict = location.raw

        #extracting from the lat, lon and bounding box data from the dict and appending it to the lists
        lat = loc_dict['lat']
        lon = loc_dict['lon']

    except:
        lat = np.null
        lon = np.null

    return lat, lon


#main

# read in xlsx workbook sheet 'Distance_Matrix_Concat_Lumo' file into a dataframe
df = pd.read_excel('230203 First Rail_Lumo Distances.xlsx', sheet_name='Distance_Matrix_Concat_Lumo')
#prepping output dfs
df_transit = pd.DataFrame(columns=['route','leg','OLat','OLon','DLat','DLon','mode','transit_mode','interchange_stat'])
df_road = pd.DataFrame(columns=['route','origin_station','OLat','OLon','destination_station','DLat','DLon','mode'])

check_missing_data_types(df)
# execute function to convert Easting and Northing coordinates into latitude longitude and rename columns
df = lat_lon_conversion(df)

df, df_transit, df_road = looper(df, df_transit, df_road)



df_road['mode']='driving'
df_transit['mode']='rail'
