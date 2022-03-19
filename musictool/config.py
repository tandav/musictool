from collections import defaultdict

chromatic_notes = 'CdDeEFfGaAbB'  # todo make variable here, delete from config, reimport everywhere, maybe circular imports
note_i = {note: i for i, note in enumerate(chromatic_notes)}
is_black = {note: bool(int(x)) for note, x in zip(chromatic_notes, '010100101010')}

neighsbors_min_shared = {'diatonic': 0, 'pentatonic': 0}


diatonic = 'major', 'dorian', 'phrygian', 'lydian', 'mixolydian', 'minor', 'locrian'
pentatonic = 'p_major', 'p_dorian', 'p_phrygian', 'p_mixolydian', 'p_minor'
harmonic = 'h_minor', 'h_locrian', 'h_major', 'h_dorian', 'h_phrygian', 'h_lydian', 'h_mixolydian'
melodic = 'm_minor', 'm_locrian', 'm_major', 'm_dorian', 'm_phrygian', 'm_lydian', 'm_mixolydian'
sudu = 's_major', 's_dorian', 's_phrygian', 's_lydian', 's_mixolydian', 's_minor'
kinds = (
    {k: 'diatonic' for k in diatonic} |
    {k: 'harmonic' for k in harmonic} |
    {k: 'melodic' for k in melodic} |
    {k: 'pentatonic' for k in pentatonic} |
    {k: 'sudu' for k in sudu}
)


# if change: also change in static/main.css
scale_colors = dict(
    major='FFFFFF',
    dorian='54E346',
    phrygian='00FFCC',
    lydian='68A6FC',
    mixolydian='FFF47D',
    minor='D83A56',
    locrian='B980F0',
)

scale_colors['h_major'] = scale_colors['major']
scale_colors['h_dorian'] = scale_colors['dorian']
scale_colors['h_phrygian'] = scale_colors['phrygian']
scale_colors['h_lydian'] = scale_colors['lydian']
scale_colors['h_mixolydian'] = scale_colors['mixolydian']
scale_colors['h_minor'] = scale_colors['minor']
scale_colors['h_locrian'] = scale_colors['locrian']

scale_colors['m_major'] = scale_colors['major']
scale_colors['m_dorian'] = scale_colors['dorian']
scale_colors['m_phrygian'] = scale_colors['phrygian']
scale_colors['m_lydian'] = scale_colors['lydian']
scale_colors['m_mixolydian'] = scale_colors['mixolydian']
scale_colors['m_minor'] = scale_colors['minor']
scale_colors['m_locrian'] = scale_colors['locrian']

scale_colors['p_major'] = scale_colors['major']
scale_colors['p_dorian'] = scale_colors['dorian']
scale_colors['p_phrygian'] = scale_colors['phrygian']
scale_colors['p_mixolydian'] = scale_colors['mixolydian']
scale_colors['p_minor'] = scale_colors['minor']

scale_colors['s_major'] = scale_colors['major']
scale_colors['s_dorian'] = scale_colors['dorian']
scale_colors['s_phrygian'] = scale_colors['phrygian']
scale_colors['s_lydian'] = scale_colors['lydian']
scale_colors['s_mixolydian'] = scale_colors['mixolydian']
scale_colors['s_minor'] = scale_colors['minor']

WHITE_COLOR = (0xaa,) * 3
BLACK_COLOR = (0x50,) * 3
WHITE = 0xFF, 0xFF, 0xFF
BLACK = 0, 0, 0
RED_COLOR = 0xff, 0, 0
GREEN_COLOR = 0, 0xff, 0
BLUE_COLOR = 0, 0, 0xff

chord_colors = {
    'minor': scale_colors['minor'],
    'major': scale_colors['major'],
    'diminished': scale_colors['locrian'],
}

default_octave = 5
DEFAULT_TUNING = 440  # default A hz tuning
RANDOM_TUNING_RANGE = 420, 510
tuning = DEFAULT_TUNING


# piano_img_size = 14 * 60, 280
piano_img_size = 14 * 18, 85
beats_per_minute = 120
beats_per_second = beats_per_minute / 60
beats_per_bar = 4
bar_seconds = beats_per_bar / beats_per_second
