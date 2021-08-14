from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from scale import all_scales, neighbors, ComparedScale
import config
import util

chromatic_notes_set = set(config.chromatic_notes)


app = FastAPI()
app.mount("/static/", StaticFiles(directory="static"), name="static")

css = f'''
<style>
{open('static/main.css').read()}
</style>
'''

@app.get("/scale_not_found", response_class=HTMLResponse)
def scale_not_found():
    return f'''
    <a href='/'>home</a>
    <h1>404: scale not found</h1>
    '''

@app.get("/", response_class=HTMLResponse)
async def root(): return RedirectResponse('/diatonic/C/major')

@app.get("/favicon.ico", response_class=HTMLResponse)
async def root(): return FileResponse('static/favicon.ico')

@app.get("/{kind}", response_class=HTMLResponse)
async def root(kind: str): return RedirectResponse(f'/{kind}/C/{getattr(config, kind)[0]}')

@app.get("/{kind}/{root}", response_class=HTMLResponse)
async def root(kind: str, root: str): return RedirectResponse(f'/{kind}/{root}/{getattr(config, kind)[0]}')


@app.get("/{kind}/{root}/{name}", response_class=HTMLResponse)
async def root_name_scale(kind: str, root: str, name: str):

    if root not in chromatic_notes_set:
        return RedirectResponse('/scale_not_found')

    roots = ' '.join(f"<a href='/{kind}/{note}/{name}'>{note}</a>" for note in config.chromatic_notes)

    initial = []
    for _name in util.iter_scales(kind):
        scale = all_scales[kind][root, _name]
        if _name == name:
            initial.append(scale.selected_repr())
            selected_scale = scale
        else:
            initial.append(repr(scale))
    initial = '\n'.join(initial)

    neighs = neighbors(selected_scale)
    neighs_html = ''

    for n_intersect in sorted(neighs.keys(), reverse=True):
        print(n_intersect)
        if n_intersect < config.neighsbors_min_intersect[kind]:
            break
        neighs_html += f'''
        <h3>{n_intersect} note intersection scales</h3>
        <div class="neighbors">
        {''.join(repr(n) for n in neighs[n_intersect])}
        </div>
        <hr>
        '''

    kind_links = f"<a href='/diatonic/{root}/major'>diatonic</a>"
    kind_links += f" <a href='/pentatonic/{root}/p_major'>pentatonic</a>"

    return f'''
    <link rel="stylesheet" href="/static/main.css">
    <a href='/'>home</a> <a href='https://github.com/tandav/piano_scales'>github</a> | root: {roots} | {kind_links}
    <hr>
    <div class='initial'>{initial}</div>
    <hr>
    {neighs_html}
    '''

@app.get("/{kind}/{left_root}/{left_name}/compare_to/{right_root}/{right_name}", response_class=HTMLResponse)
async def compare_scales(kind: str, left_root: str, left_name: str, right_root: str, right_name: str):
    left = all_scales[kind][left_root, left_name]
    right = ComparedScale(left, all_scales[kind][right_root, right_name])


    for i, chord in enumerate(left.chords, start=1):
        chord.number = i
        if chord in right.shared_chords:
            chord.label = f'left_{chord.str_chord}'

    for i, chord in enumerate(right.chords, start=1):
        chord.number = i
        if chord in right.shared_chords:
            chord.label = f'right_{chord.str_chord}'

    js = '\n'
    for chord in right.shared_chords:
        js += f"new LeaderLine(document.getElementById('left_{chord.str_chord}'), document.getElementById('right_{chord.str_chord}')).setOptions({{startSocket: 'bottom', endSocket: 'top'}});\n"

    return f'''
    <link rel="stylesheet" href="/static/main.css">
    <script src="/static/leader-line.min.js"></script>
    
    <a href='/'>home</a> <a href='https://github.com/tandav/piano_scales'>github</a>
    <h1>compare scales</h1>
    <div class='compare_scales'>{left!r}{right!r}</div>
    <h1>chords</h1>
    <div class='compare_scales'>
    <ol class='chords_row left'>{''.join(f'{chord!r}' for chord in left.chords)}</ol>
    <ol class='chords_row right'>{''.join(f'{chord!r}' for chord in right.chords)}</ol>
    <script>
    {js}
    </script>
    </div>
    '''