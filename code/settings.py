import pygame
from os.path import join 
from os import walk

WINDOW_WIDTH, WINDOW_HEIGHT = 1280,720 

COLORS = {
    'black': '#000000',
    'red': '#ee1a0f',
    'gray': 'gray',
    'white': '#ffffff',
    'dark_gray': '#404040',
    'light_gray': '#CCCCCC',
    'dark_red': '#8B0000'
}

MONSTER_DATA = {
    # Plant Monsters (High Health, High Defense, Low Attack)
    'Larvea':    {'element': 'plant', 'health': 180, 'attack': 40, 'defense': 70},
    'Pouch':     {'element': 'plant', 'health': 200, 'attack': 55, 'defense': 90},
    'Plumette':  {'element': 'plant', 'health': 210, 'attack': 60, 'defense': 95},
    'Cleaf':     {'element': 'plant', 'health': 210, 'attack': 65, 'defense': 90},
    'Draem':     {'element': 'plant', 'health': 225, 'attack': 70, 'defense': 110},
    'Ivieron':   {'element': 'plant', 'health': 245, 'attack': 75, 'defense': 120},
    'Pluma':     {'element': 'plant', 'health': 260, 'attack': 80, 'defense': 130},

    # Fire Monsters (Low Health, Strong Attack, Weak Defense)
    'Atrox':     {'element': 'fire',  'health': 90,  'attack': 75, 'defense': 40},
    'Jacana':    {'element': 'fire',  'health': 100, 'attack': 85, 'defense': 45},
    'Sparchu':   {'element': 'fire',  'health': 110, 'attack': 90, 'defense': 50},
    'Cindrill':  {'element': 'fire',  'health': 130, 'attack': 105, 'defense': 65},
    'Charmadillo': {'element': 'fire',  'health': 145, 'attack': 120, 'defense': 70},

    # Water Monsters (Average Health, Balanced Stats)
    'Finsta':    {'element': 'water', 'health': 140, 'attack': 60, 'defense': 60},
    'Friolera':  {'element': 'water', 'health': 155, 'attack': 70, 'defense': 70},
    'Gulfin':    {'element': 'water', 'health': 165, 'attack': 75, 'defense': 75},
    'Finiette':  {'element': 'water', 'health': 180, 'attack': 85, 'defense': 85},
}

ABILITIES_DATA = {
	'scratch': {'damage': 20,  'element': 'normal', 'animation': 'scratch'},
	'spark':   {'damage': 35,  'element': 'fire',   'animation': 'fire'},
	'nuke':    {'damage': 50,  'element': 'fire',   'animation': 'explosion'},
	'splash':  {'damage': 30,  'element': 'water',  'animation': 'splash'},
	'shards':  {'damage': 50,  'element': 'water',  'animation': 'ice'},
    'spiral':  {'damage': 40,  'element': 'plant',  'animation': 'green'},
    'earthquake': {'damage': 55,  'element': 'plant',  'animation': 'green'}
}

ELEMENT_DATA = {
    'fire':   {'water': 0.5, 'plant': 2,   'fire': 1,   'normal': 1},
    'water':  {'water': 1,   'plant': 0.5, 'fire': 2,   'normal': 1},
    'plant':  {'water': 2,   'plant': 1,   'fire': 0.5, 'normal': 1},
    'normal': {'water': 1,   'plant': 1,   'fire': 1,   'normal': 1},
}