from tokyo_mapping import *


def tokyo_coords_to_text(width=100, height=100):
    coords, _ = get_tokyo_grid(width, height)
    with open('tokyo_coords.txt', 'w') as f:
        for x, y in coords:
            f.write(f'{x} {y}\n')

def text_to_coords(file_name):
    coords = []
    with open(file_name, 'r') as f:
        for coord in f:
            x, y = coord.split()
            coords.append((int(x), int(y)))
    return coords


if __name__ == '__main__':
    tokyo_coords_to_text()