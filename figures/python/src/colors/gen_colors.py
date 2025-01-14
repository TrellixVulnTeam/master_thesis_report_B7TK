"""
gen_colors_tex.py

Defines color palettes based on 'std_colors.csv'
If executed by itself, generates/overwrites tex files 'colors.tex' and 'prev_content.tex'
"""

__author__ = "Roman Rüttimann"
# %%
try:
    import numpy as np
    import matplotlib.pyplot as plt
    import pandas as pd
    from pathlib import Path

    from utils import get_project_root
    from colors.colpal import Colpal
except Exception as e:
    print("Not all Modules have been loaded. {}".format(e))

dir_path = Path(__file__).parent


def seperate_df(df):
    m = np.invert(df.ColorName.isnull().to_numpy())
    srows = np.where(m)
    s = np.append(srows, m.size)
    list_of_dfs = [df.iloc[s[i]:s[i+1]] for i in range(s.size-1)]
    return list_of_dfs

def create_palette_list(df):
    name_ext = ('STD', 'L', 'UL')
    m = len(name_ext)
    dfs = seperate_df(df)
    n = len(dfs)
    palettes = [None]*m*n
    for i in range(len(palettes)):
        palettes[i] = Colpal(dfs[int(i/m)])
        palettes[i].set_name(palettes[i].get_name() + name_ext[i % m])
        if i % m == 1:
            palettes[i].set_darkness(0.7)
        elif i % m == 2:
            palettes[i].set_darkness(0.25)
    return palettes

def colname_fmt(pal, idx=None):
    fmt_str = '{name}{len:d}{type}'
    if not (idx == None or idx==len(pal)):
        fmt_str = fmt_str+'{num:d}'
    out = fmt_str.format(name=pal.name, len=len(pal), type=pal.type, num=idx)
    if idx==len(pal):
        out = out+'{num:d}'
    return out

def write_colors(palettes, outfile):
    for pal in palettes:
        definecol_fmt = ['\\definecolor{', colname_fmt(pal,len(pal)), '}{RGB}{', ','.join(3*['{:d}']), '}\n']
        for i in range(len(pal)):
            out_list = definecol_fmt[:]
            out_list[1] = out_list[1].format(num=i)
            out_list[-2] = out_list[-2].format(*pal.rgb(i))
            outfile.write(''.join(out_list))
    outfile.write('\n')

def write_colorpals(palettes, outfile):
    for pal in palettes:
        definepal_fmt = ['\\definecolorseries{', colname_fmt(pal), 'P}{rgb}{step}[rgb]', len(pal)*['{', ','.join(3*['{:f}']), '}']]
        out_list = definepal_fmt[:]
        for i in range(len(pal)):
            out_list[3][i*3+1] = out_list[3][i*3+1].format(*pal.rgb_rel(i))
        out_list[3] = ''.join(out_list[3])
        outfile.write(''.join([*out_list, '\n']))
    outfile.write('\n')
#     for pal in palettes:
#         definepal_fmt = ['\\definecolorseries{', colname_fmt(pal), 'P}{rgb}{step}[rgb]', len(pal)*['{', ','.join(3*['{:d}']), '}']]
#     for sub


def write_colormaps(palettes, outfile, cond=None):
    if cond == None:
        cond = ('qual','seq','div')
    elif isinstance(cond,str):
        cond = tuple([cond])
    for pal in palettes:
        if any(item == pal.type for item in cond):
            definecol_fmt = [
                '\\pgfplotsset{/pgfplots/colormap={', colname_fmt(pal), '}{%\n',
                len(pal)*['\trgb255=(' + ','.join(3*['{:d}']) + ')\n'],
                '}}\n'
            ]
            for i in range(len(pal)):
                out_list = definecol_fmt[:]
                out_list[-2][i] = out_list[-2][i].format(*pal.rgb(i))
            out_list[-2] = ''.join(out_list[-2])
            outfile.write(''.join(out_list))
    outfile.write('\n')

def write_colpalprev(palettes, outfile):
    outfile.write('\\section*{Color Palettes}\n')
    for pal in palettes:
        colpalprev_fmt = ['\\prevColpal{', colname_fmt(pal),'}{', '{len:d}', '}\n']
        out_list = colpalprev_fmt[:]
        out_list[-2] = out_list[-2].format(len=len(pal))
        outfile.write(''.join(out_list))
    outfile.write('\n')

def write_colmapprev(palettes, outfile, cond=None):
    if cond == None:
        cond = ('qual','seq','div')
    elif isinstance(cond,str):
        cond = tuple([cond])
    outfile.write('\\section*{Color Maps}\n')
    for pal in palettes:
        if any(item == pal.type for item in cond):
            out_list = ['\\prevColmap{', colname_fmt(pal),'}\n\n']
            outfile.write(''.join(out_list))
    outfile.write('\n')

#%%
df = pd.read_csv(dir_path / 'std_colors.csv', sep=';')
colpalettes = create_palette_list(df)

#%%
#if __name__ == '__main__':
out_dir = get_project_root().parent / 'presets' / 'colors'
outfiles = [out_dir / 'colors.tex', out_dir / 'prev_content.tex']
print('Accessing files in folder\n{}:\n'.format(out_dir))
with outfiles[0].open('w') as out:
    write_colors(colpalettes, out)
    #write_colorpals(colpalettes, out)
    write_colormaps(colpalettes, out)
print('File "{}" has been overwritten.'.format(outfiles[0].name))

with outfiles[1].open('w') as out:
    write_colpalprev(colpalettes, out)
    write_colmapprev(colpalettes, out)
print('File "{}" has been overwritten.'.format(outfiles[1].name))

#%%
import subprocess
runfile = out_dir / 'preview.tex'
print('Start compiling "{}".'.format(runfile.name))
cwd = fr"{str(out_dir)}"
args = ['latexmk',
    '-synctex=1',
    '-interaction=nonstopmode',
    '-file-line-error',
    '-pdf',
    '-output-directory={}'.format(cwd),
    'preview.tex']
subout = subprocess.run(args, cwd=cwd, stdout=subprocess.PIPE)
if not subout.returncode:
    print('Latex compiler failed. {}'.format(subout.stderr))
else:
    print('"{}.pdf" successfully compiled.'.format(runfile.stem))
print(subout)
# %%

# %%
