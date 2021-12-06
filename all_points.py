import pandas as pd
import folium
import time
from colour import Color
import os


if __name__ == '__main__':
    # Mapa base de Folium sobre el que se dibujarán los puntos y centroides
    zipmap = folium.Map(location=[41.878876, -87.635918], zoom_start=11)
    # Capa para mostrar el mapa en blanco y negro para mejorar el contraste con los colores de cada cluster
    folium.TileLayer('cartodbdark_matter').add_to(zipmap)

    # URL para añadir los distritos de chicago, utilizando un GeoJSON
    zipcodes = "https://data.cityofchicago.org/api/geospatial/gdcf-axmw?method=export&format=GeoJSON"

    # Dataframe con los centroides y radios de cada cluster
    centroids = pd.read_csv('../Datasets/circulos_mean.csv')
    # Dataframe con los puntos (delitos) y su ubicación
    points = pd.read_csv('../Datasets/poligonos.csv')
    # Dataframe con los KPI por clúser, utlizado para calcular el número de delitos de cada cluster
    kpis = pd.read_csv('../Datasets/df_kpi.csv')
    # Media para controlar el tiempo de ejecución
    start = time.time()
    # Dataframe auxiliar para colorear los puntos de cada cluster en función del número de delitos.
    clusters_crimes = pd.DataFrame(columns=['Cluster', 'Crimes'])
    # Se itera sobre el dataframe de centroides para dibujar cada centroide y su radio
    for indx, row in centroids.iterrows():
        # Cálculo del número de delitos
        cluster_data = kpis[kpis['Cluster'] == row['Cluster']]['num_crimes'].sum()
        clusters_crimes.loc[len(clusters_crimes)] = [row['Cluster'], cluster_data]
        # Se añade al mapa un marcador para cada centroide
        folium.Marker(location=(row['Latitude_C'], row['Longitude_C']),
                      popup=f"Centro del cluster: {row['Cluster']}, Número Delitos al año: {round(cluster_data / 21, 3)}",
                      icon=folium.Icon(color="red", icon="info-sign")).add_to(zipmap)

    # Se ordena el dataframe auxiliar de mayor número de delitos a menor
    clusters_crimes = clusters_crimes.sort_values('Crimes', ascending=False)
    # Se crea un grandiente de color que será asignado a cada cluster
    colors = list(Color('Red').range_to(Color("Purple"), 15))
    colors = [x.get_hex() for x in colors]
    # Se añade el color como una columna del Dataframe auxiliar
    clusters_crimes['Color'] = colors
    # Se crea un diccionario que será utilizado para controlar el número
    # de puntos que se han dibujado para cada cluster
    clusters_points = {}
    for i in range(15):
        clusters_points[i] = 0

    # Se itera sobre el Dataframe de puntos
    for indx, row in points.iterrows():
        cluster = row['Cluster'].astype('int')
        # En función del cluster al que pertenezca el punto se selecciona el color del gradiente previamente creado
        point_color = clusters_crimes[clusters_crimes['Cluster'] == cluster]['Color'].values[0]
        # Para cada cluster se dibujan únicamente 500 puntos
        # con esto se logra una visualización correcta de la forma de cada clúser, con un rendimiento adecuado
        if clusters_points[cluster] < 500:
            # Cada punto se representa como un círculo pequeño en el mapa.
            folium.CircleMarker(location=(row['Latitude'], row['Longitude']), radius=5,
                                color=point_color, fill=True,
                                fill_color=point_color,
                                fill_opacity=0.7,
                                parse_html=False).add_to(zipmap)

        clusters_points[cluster] += 1

    # Se añade al mapa el GeoJSON con los distritos
    folium.GeoJson(zipcodes, name="Chicago Zipcodes").add_to(zipmap)
    # Se vuelve a iterar sobre el dataframe de centroides para dibujar los círculos de radio la distancia media
    for indx, row in centroids.iterrows():
        folium.Circle((row['Latitude_C'], row['Longitude_C']), radius=row['Distances'], color='#cf0a0a').add_to(zipmap)

    # Se exporta el mapa a HTML para poder visualizarlo correctamente
    os.makedirs('../html/', exist_ok=True)
    zipmap.save('../html/all_points.html')
    end = time.time()
    print('Tiempo transcurrido para la creación del mapa: ', end - start)
