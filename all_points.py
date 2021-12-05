import pandas as pd
import folium
import time
from colour import Color
import os


if __name__ == '__main__':
    colors = [
        '#f6511d',
        '#ffb400',
        '#00a6ed',
        '#7fb800',
        '#43bc14',
        '#662e9b',
        '#af7ff2',
        '#92b51d',
        '#9b6400',
        '#646aed',
        '#1b5400',
        '#a7e414',
        '#ca920f',
        '#4bbb2a',
        '#c458cc',
        '#e07070',
        '#f6511d',
        '#ffb400',
        '#00a6ed',
        '#7fb800',
        '#43bc14',
        '#662e9b',
        '#af7ff2',
        '#92b51d',
        '#9b6400',
        '#646aed',
        '#1b5400',
        '#a7e414',
        '#ca920f',
        '#4bbb2a',
        '#c458cc',
        '#e07070'
    ]
    icon_url = 'https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.iconfinder.com%2Ficons%2F1185067%2Farrows_center_direction_inward_arrows_middle_icon&psig=AOvVaw1aATIxqkUBsTX5dqo6S3Kn&ust=1638805723483000&source=images&cd=vfe&ved=0CAsQjRxqFwoTCKDZh52BzfQCFQAAAAAdAAAAABAD'
    zipmap = folium.Map(location=[41.878876, -87.635918], zoom_start=11)
    folium.TileLayer('cartodbdark_matter').add_to(zipmap)

    zipcodes = "https://data.cityofchicago.org/api/geospatial/gdcf-axmw?method=export&format=GeoJSON"

    centroids = pd.read_csv('../Datasets/circulos_mean.csv')
    points = pd.read_csv('../Datasets/prueba.csv')
    kpis = pd.read_csv('../Datasets/df_kpi.csv')
    start = time.time()
    clusters_crimes = pd.DataFrame(columns=['Cluster', 'Crimes'])
    # PARA OPTIMIZAR LOS FORS
    cluster_circles = []
    for indx, row in centroids.iterrows():
        cluster_data = kpis[kpis['Cluster'] == row['Cluster']]['num_crimes'].sum()
        clusters_crimes.loc[len(clusters_crimes)] = [row['Cluster'], cluster_data]
        folium.Marker(location=(row['Latitude_C'], row['Longitude_C']),
                      popup=f"Centro del cluster: {row['Cluster']}, Número Delitos al año: {round(cluster_data / 21, 3)}",
                      icon=folium.Icon(color="red", icon="info-sign")).add_to(zipmap)
    clusters_crimes = clusters_crimes.sort_values('Crimes', ascending=False)
    colors = list(Color('Red').range_to(Color("Purple"), 15))
    colors = [x.get_hex() for x in colors]
    clusters_crimes['Color'] = colors
    clusters_points = {}
    for i in range(15):
        clusters_points[i] = 0

    for indx, row in points.iterrows():
        cluster = row['Cluster'].astype('int')
        point_color = clusters_crimes[clusters_crimes['Cluster'] == cluster]['Color'].values[0]
        if clusters_points[cluster] < 500:
            folium.CircleMarker(location=(row['Latitude'], row['Longitude']), radius=5,
                                color=point_color, fill=True,
                                fill_color=point_color,
                                fill_opacity=0.7,
                                parse_html=False).add_to(zipmap)

        clusters_points[cluster] += 1

    folium.GeoJson(zipcodes, name="Chicago Zipcodes").add_to(zipmap)
    for indx, row in centroids.iterrows():
        folium.Circle((row['Latitude_C'], row['Longitude_C']), radius=row['Distances'], color='#cf0a0a').add_to(zipmap)

    os.makedirs('../html/', exist_ok=True)
    zipmap.save('../html/all_points.html')
    end = time.time()
    print('Tiempo transcurrido para la creación del mapa: ', end - start)
