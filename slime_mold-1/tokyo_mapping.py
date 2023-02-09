"""36 Food sources (cities)
City list based on empirical evidence...:
- Maebashi
- Takasaki
- Kiryu
- Ashikaga
- Oyama
- Mito
- Kumagaya
- Kamonomiya
- Saitama
- Tokyo
- Tsuchiara
- Kashiwa
- Funabashi

Bottom right
- Chiba
- Ichihara
- Kisarazu
- Tateyama
- Katsuura
- Ichinomiya
- Togane
- Asahi
- Choshi
- Katori
- Narita
- Sakura

Bottom left
- Yokosuka
- Kamakura
- Yokohama
- Chigasaki
- Hiratsuka
- Odawara
- Sagamihara
- Hachioji

(Not on drawn map from paper)
- Ito
- Utsonomiya
- Hitachi
"""
import numpy as np
import matplotlib.pyplot as plt
import utm

# Handpicked by Robbie :)
STATION_GEO_COORDS = {
    "Maebashi": (36.383184, 139.073217),
    "Takasaki": (36.322827, 139.012662),
    "Kiryu": (36.411145, 139.333079),
    "Ashikaga": (36.331824, 139.455877),
    "Oyama": (36.313121, 139.806324),
    "Mito": (36.370733, 140.476279),
    "Kumagaya": (36.13939, 139.390033),
    "Kamonomiya": (35.93579, 139.616935),
    "Saitama": (35.905377, 139.62322),
    "Tokyo": (35.681236, 139.767125),
    "Tsuchiura": (36.078484, 140.206212),
    "Kashiwa": (35.86215, 139.970917),
    "Funabashi": (35.701736, 139.985382),
    "Chiba": (35.613134, 140.113359),
    "Goi": (35.519939, 140.082965),
    "Kisarazu": (35.381252, 139.924887),
    "Tateyama": (34.995957, 139.861896),
    "Katsuura": (35.152563, 140.311936),
    "Ichinomiya": (35.37254, 140.368552),
    "Togane": (35.560158, 140.363609),
    "Asahi": (35.722009, 140.654939),
    "Choshi": (35.734004, 140.826746),
    "Katori": (35.897903, 140.532304),
    "Narita": (35.776659, 140.318742),
    "Sakura": (35.723598, 140.223939),
    "Yokosuka": (35.836005, 139.912986),
    "Kamakura": (35.319213, 139.546673),
    "Yokohama": (35.443674, 139.637964),
    "Chigasaki": (35.330303, 139.406817),
    "Hiratsuka": (35.327645, 139.350466),
    "Odawara": (35.256445, 139.155393),
    "Sagamihara": (35.571257, 139.373427),
    "Hachioji": (35.655616, 139.338853),
    "Ito": (34.965605, 139.102465),
    "Utsonomiya": (36.555075, 139.882621),
    "Hitachi": (36.599127, 140.650471)
}


def coord_to_grid_coord(coord, hor_n, ver_n):
    x, y = coord

    x_index = np.ceil(hor_n * x)
    y_index = np.ceil(ver_n * y)

    if x_index >= hor_n:
        x_index = hor_n - 1

    if y_index >= ver_n:
        y_index = ver_n - 1

    return [int(x_index), int(y_index)]


def coords_to_grid_indices(coords, hor_n, ver_n):
    grid_indices = {}

    for node_id in coords:
        x, y = coords[node_id]

        grid_indices[node_id] = coord_to_grid_coord((x, y), hor_n, ver_n)

    return grid_indices


def convert_geo_to_relative_coords(geo_coords):
    station_locations = {}

    # Convert coordinates to 2D space coordinates
    for i in range(len(geo_coords)):
        station_id = list(geo_coords.keys())[i]
        latitude, longitude = geo_coords[station_id]
        x, y, _, _ = utm.from_latlon(latitude, longitude)

        station_locations[station_id] = (x, y)

    # Scale and translate 2D coordinates
    x_vals = [x for (x, _) in station_locations.values()]
    y_vals = [y for (_, y) in station_locations.values()]

    for i in range(len(geo_coords)):
        node_id = list(station_locations.keys())[i]
        x, y = station_locations[node_id]

        x_new = (x - np.min(x_vals)) / (np.max(x_vals) - np.min(x_vals))
        y_new = (y - np.min(y_vals)) / (np.max(y_vals) - np.min(y_vals))

        station_locations[node_id] = (x_new, y_new)

    return station_locations


def get_tokyo_grid(hor_n=100, ver_n=100):
    station_locations = convert_geo_to_relative_coords(STATION_GEO_COORDS)
    grid_indices = coords_to_grid_indices(station_locations, hor_n, ver_n)

    grid = np.zeros((hor_n, ver_n), dtype=int)
    for i in range(len(grid_indices)):
        x, y = grid_indices[i]

        grid[x, y] = 1

    return grid_indices, grid


if __name__ == "__main__":
    grid_indices, grid = get_tokyo_grid(100, 100)
    print(grid_indices)
    # Plot
    plt.imshow(np.rot90(grid))
    plt.show()
