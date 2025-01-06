import folium
import pandas as pd 
import requests
from folium.plugins import HeatMap
from kaggle.api.kaggle_api_extended import KaggleApi
import streamlit as st
from streamlit_folium import folium_static
st.set_page_config(
    page_title="Chicago Traffic Crashes",
    layout="wide",
    initial_sidebar_state="expanded",
)
if 'kaggle' in st.secrets:
    os.environ['KAGGLE_USERNAME'] = st.secrets["kaggle"]["username"]
    os.environ['KAGGLE_KEY'] = st.secrets["kaggle"]["key"]
else:
    st.error("Kaggle credentials not found. Please set them in Streamlit secrets.")
    st.stop()
@st.cache_data
def load_data():
    api = KaggleApi()
    api.authenticate()
    dataset_identifier = 'anoopjohny/traffic-crashes-crashes'  
    DATA_DIR = 'data'
    os.makedirs(DATA_DIR, exist_ok=True)

    
    api.dataset_download_files(dataset_identifier, path=DATA_DIR, unzip=True)

    
    crash_path = os.path.join(DATA_DIR, 'red-light-camera-violations.csv')

   
    crash_pd = pd.read_csv(crash_path)


    return crash_pd

crash_data = load_data()



crash_data['CRASH_DATE'] = pd.to_datetime(crash_data['CRASH_DATE'], format='%m/%d/%Y %I:%M:%S %p')  

for idx, row in crash_data.iterrows():
    if pd.isnull(row['LATITUDE']):
        url = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress?address={num}+{street_name},+Chicago,+IL&benchmark=Public_AR_Current&format=json"
        #strname_plus = row['STREET_DIRECTION'] + '+' + '+'.join(row['STREET_NAME'].split(" ")).lower()
        try:    
            strname_plus = row['STREET_DIRECTION'] + '+' + '+'.join(row['STREET_NAME'].split(" ")).lower()
            response = requests.get(url.format(num=row['STREET_NO'], street_name=strname_plus))
            print(url.format(num=row['STREET_NO'], street_name=strname_plus))
            query_result = response.json()
            lat = query_result["result"]["addressMatches"][0]["coordinates"]["x"]
            long = query_result["result"]["addressMatches"][0]["coordinates"]["y"]
            crash_data.at[idx, 'LATITUDE'] = lat
            crash_data.at[idx, 'LONGITUDE'] = long
            
        except:
            pass

years = crash_data['CRASH_DATE'].dt.year.unique()
m = folium.Map(location=(41.8781, -87.6298), tiles = 'https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png', attr = 'mine')
for year in years:
    year_data = crash_data[crash_data['CRASH_DATE'].dt.year == year]
    lat_long = year_data[['LATITUDE','LONGITUDE']].dropna().values.tolist()
    group = folium.FeatureGroup(name=str(year))
    HeatMap(lat_long, radius = 7, blur = .5).add_to(group)
    group.add_to(m)


folium.LayerControl(collapsed=False).add_to(m)
folium_static(m, width = 1400, height = 1000)
#HeatMap(lat_long_intensity, radius = 7, blur = .5).add_to(m)
#m.save("index.html")



