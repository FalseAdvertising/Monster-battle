import pygame
from os.path import join 
from os import walk

WINDOW_WIDTH, WINDOW_HEIGHT = 1280,720 

COLORS = {
    'black': '#000000',
    'red': '#ee1a0f',
    'gray': '#808080',  # Changed from 'gray' to hex code
    'white': '#ffffff',
    'dark_gray': '#404040',
    'light_gray': '#CCCCCC',
    'dark_red': '#8B0000',
    'green': '#00FF00',
}

MONSTER_DATA = {
    # Plant Monsters (High Health, High Defense, Low Attack)
    'Larvea':    {'element': 'plant', 'health': 450, 'attack': 40, 'defense': 70},
    'Pouch':     {'element': 'plant', 'health': 500, 'attack': 55, 'defense': 90},
    'Plumette':  {'element': 'plant', 'health': 525, 'attack': 60, 'defense': 95},
    'Cleaf':     {'element': 'plant', 'health': 525, 'attack': 65, 'defense': 90},
    'Draem':     {'element': 'plant', 'health': 560, 'attack': 70, 'defense': 110},
    'Ivieron':   {'element': 'plant', 'health': 610, 'attack': 75, 'defense': 120},
    'Pluma':     {'element': 'plant', 'health': 650, 'attack': 80, 'defense': 130},

    # Fire Monsters (Low Health, Strong Attack, Weak Defense)
    'Atrox':     {'element': 'fire',  'health': 225, 'attack': 75, 'defense': 40},
    'Jacana':    {'element': 'fire',  'health': 250, 'attack': 85, 'defense': 45},
    'Sparchu':   {'element': 'fire',  'health': 275, 'attack': 90, 'defense': 50},
    'Cindrill':  {'element': 'fire',  'health': 325, 'attack': 105, 'defense': 65},
    'Charmadillo': {'element': 'fire',  'health': 360, 'attack': 120, 'defense': 70},

    # Water Monsters (Average Health, Balanced Stats)
    'Finsta':    {'element': 'water', 'health': 350, 'attack': 60, 'defense': 60},
    'Friolera':  {'element': 'water', 'health': 390, 'attack': 70, 'defense': 70},
    'Gulfin':    {'element': 'water', 'health': 410, 'attack': 75, 'defense': 75},
    'Finiette':  {'element': 'water', 'health': 450, 'attack': 85, 'defense': 85},
}

ABILITIES_DATA = {
	'scratch': {'damage': 20,  'element': 'normal', 'animation': 'scratch'},
	'spark':   {'damage': 35,  'element': 'fire',   'animation': 'fire'},
	'nuke':    {'damage': 50,  'element': 'fire',   'animation': 'explosion'},
	'splash':  {'damage': 30,  'element': 'water',  'animation': 'splash'},
	'shards':  {'damage': 50,  'element': 'water',  'animation': 'ice'},
    'spiral':  {'damage': 40,  'element': 'plant',  'animation': 'green'},
    'earthquake': {'damage': 55,  'element': 'plant',  'animation': 'green'},
    
    # Special Moves (one-time use only)
    'reflect_shield': {'damage': 0,   'element': 'plant', 'animation': 'green', 'type': 'special'},
    'healing_wave':   {'damage': -80, 'element': 'water', 'animation': 'splash', 'type': 'special'},
    'burning_fury':   {'damage': 45,  'element': 'fire',  'animation': 'fire', 'type': 'special'}
}

ELEMENT_DATA = {
    'fire':   {'water': 0.5, 'plant': 2,   'fire': 1,   'normal': 1},
    'water':  {'water': 1,   'plant': 0.5, 'fire': 2,   'normal': 1},
    'plant':  {'water': 2,   'plant': 1,   'fire': 0.5, 'normal': 1},
    'normal': {'water': 1,   'plant': 1,   'fire': 1,   'normal': 1},
}