# This file contains a list of levels that the user may choose from.

# An easy level, with no obstacles at all.
EASY = {
    'name': "EASY",
    'level': [

        # Column 1
        ['stone block',
         'stone block',
         'grass block',
         'grass block',
         'grass block',
         'stone block',
         'stone block',
         ],

        # Column 2
        ['stone block',
         'stone block',
         'grass block',
         'grass block',
         'water block',
         'grass block',
         'stone block',
         ],

        # Column 3
        ['dirt block',
         'grass block',
         'grass block',
         'dirt block',
         'stone block',
         'stone block',
         'grass block',
         ],

        # Column 4
        ['stone block',
         'dirt block',
         'dirt block',
         'stone block',
         'stone block',
         'wall block',
         'grass block',
         ],

        # Column 5
        ['grass block',
         'stone block',
         'grass block',
         'ramp block',
         'dirt block',
         'dirt block',
         'stone block',
         ],

        # Column 6
        ['grass block',
         'grass block',
         'water block',
         'stone block',
         'stone block',
         'stone block',
         'dirt block',
         ],

        # Column 7
        ['grass block',
         'grass block',
         'grass block',
         'stone block',
         'stone block',
         'ramp block',
         'stone block',
         ]
    ],

    'player': [300, 400],
    'enemy': [[50, 100], [650, 100], [50, 600], [650, 600]],
    'min_enemys': 2
}

# A hard level, that is, has many obstacles.
HARD = {
    'name': 'HARD',
    'level': [

        # Column 1
        ['grass block',
         'grass block',
         'water block',
         'water block',
         'stone block',
         'dirt block',
         'dirt block',
         ],

        # Column 2
        ['grass block',
         'grass block',
         'ramp block',
         'ramp block',
         'dirt block',
         'dirt block',
         'dirt block',
         ],

        # Column 3
        ['water block',
         'grass block',
         'water block',
         'ramp block',
         'dirt block',
         'wall block',
         'dirt block',
         ],

        # Column 4
        ['water block',
         'dirt block',
         'ramp block',
         'dirt block',
         'dirt block',
         'dirt block',
         'dirt block',
         ],

        # Column 5
        ['stone block',
         'stone block',
         'water block',
         'ramp block',
         'dirt block',
         'water block',
         'ramp block',
         ],

        # Column 6
        ['stone block',
         'wall block',
         'stone block',
         'grass block',
         'dirt block',
         'grass block',
         'grass block',
         ],

        # Column 7
        ['grass block',
         'grass block',
         'dirt block',
         'water block',
         'water block',
         'grass block',
         'grass block',
         ]
    ],

    'player': [300, 400],
    'enemy': [[50, 100], [650, 100], [50, 600], [650, 600]],
    'min_enemys': 5
}

# A moderate difficulty level.
MEDIUM = {

    'name': "MEDIUM",
    'level': [

        # Column 1
        ['dirt block',
         'dirt block',
         'wall block',
         'grass block',
         'grass block',
         'grass block',
         'grass block',
         ],

        # Column 2
        ['dirt block',
         'dirt block',
         'dirt block',
         'stone block',
         'stone block',
         'grass block',
         'wall block',
         ],

        # Column 3
        ['water block',
         'dirt block',
         'grass block',
         'stone block',
         'stone block',
         'grass block',
         'grass block',
         ],

        # Column 4
        ['water block',
         'ramp block',
         'water block',
         'stone block',
         'dirt block',
         'wall block',
         'grass block',
         ],

        # Column 5
        ['dirt block',
         'ramp block',
         'water block',
         'dirt block',
         'stone block',
         'grass block',
         'grass block',
         ],

        # Column 6
        ['dirt block',
         'ramp block',
         'ramp block',
         'stone block',
         'stone block',
         'stone block',
         'stone block',
         ],

        # Column 7
        ['dirt block',
         'dirt block',
         'dirt block',
         'stone block',
         'stone block',
         'grass block',
         'stone block',
         ]
    ],

    'player': [300, 400],
    'enemy': [[50, 100], [650, 100], [50, 600], [650, 600]],
    'min_enemys': 3
}
