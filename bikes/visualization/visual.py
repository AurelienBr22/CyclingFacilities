from folium.plugins import HeatMap, MeasureControl
import folium


def create_heatmap(locations, lat=48.8566, long=2.3522):

    paris_map_heatmap = folium.Map(location=[lat, long], zoom_start=16)

    heatmap_layer = HeatMap(
        data=locations,
        name='My Heatmap',
        min_opacity=0.6,
        max_opacity=0.9,
        radius=10,
        blur=10,
        gradient={0.2: 'blue', 0.4: 'green', 0.6: 'yellow', 0.8: 'orange', 1: 'red'}
    )

    heatmap_layer.add_to(paris_map_heatmap)

    # Add a marker for the user's location if available
    if lat and long:
        folium.Marker(
            location=[lat, long],
            icon=folium.Icon(color='red', icon='bicycle', prefix='fa', size='small'),
            popup='Point d\'intérêt'
        ).add_to(paris_map_heatmap)
        folium.Circle(
            location=[lat, long],
            radius=100,
            color='red',
            fill=False,
            popup='Point d\'intérêt'
        ).add_to(paris_map_heatmap)

    return paris_map_heatmap
