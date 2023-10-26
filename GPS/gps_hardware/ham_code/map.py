import folium

# Create a map centered at a specific location
m = folium.Map(location=[48.858093,2.294694], zoom_start=12)

# Add a marker to the map
folium.Marker(
    location=[51.5074, -0.1278],
    popup='Hello, London!',
).add_to(m)

# Save the map to an HTML file
m.save('my_map.html')

