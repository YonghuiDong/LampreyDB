# coding: utf-8
from django.conf import settings
from rdkit import Chem
from rdkit.Chem.Draw import rdMolDraw2D
from rdkit.Chem import PandasTools
from rdkit import DataStructs
import plotly.graph_objects as go
from plotly.offline import plot
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import re
from bs4 import BeautifulSoup
from .fish_svg import svg_model

pattern = re.compile("<\?xml.*\?>")
molSize = settings.RDKIT_SMILE_SIZE
kekulize = settings.RDKIT_SMILE_KEKULIZE


def DrawMol(mol, molSize=molSize, kekulize=kekulize) -> str:
    '''将分子式输出到svg文本'''
    mc = Chem.MolFromSmiles(mol)
    if kekulize:
        try:
            Chem.Kekulize(mc)
        except:
            mc = Chem.Mol(mol.ToBinary())
    if not mc.GetNumConformers():
        Chem.rdDepictor.Compute2DCoords(mc)

    drawer = rdMolDraw2D.MolDraw2DSVG(*molSize)
    drawer.DrawMolecule(mc)
    drawer.FinishDrawing()
    svg = drawer.GetDrawingText().replace('svg:', '')
    svg = re.sub(pattern, '', svg)
    return svg


def generate_chemical_smiles(smiles_string: str, svg_path):
    '''生成分子式svg图片'''
    with open(svg_path, 'w', encoding='utf-8', newline='') as f:
        f.write(DrawMol(mol=smiles_string))


def generate_heat_map(data: str, pic_path):
    '''画热图'''
    Value = parse_serial_data(data)
    Value = np.log2(Value)
    Stage = np.tile(np.repeat(['MG', 'Orange', 'MR'], 3), 3)
    Tissue = np.repeat(['Peel', 'Flesh', 'Seed'], 9)
    df = pd.DataFrame({'Stage': Stage, 'Tissue': Tissue, 'Value': Value})
    ##(3.2) 计算重复之间的平均值和方差，并建立平均值±方差为标签
    mymean = np.round(df.groupby(['Stage', 'Tissue']).mean().reset_index(), 1)
    mysd = np.round(df.groupby(['Stage', 'Tissue']).std().reset_index(), 1)

    ### 均值和方差重排序
    mymean['Stage'] = pd.Categorical(mymean['Stage'], ['MG', 'Orange', 'MR'])
    mymean['Tissue'] = pd.Categorical(mymean['Tissue'], ['Peel', 'Flesh', 'Seed'])
    mymean = mymean.sort_values(['Stage', 'Tissue'])

    mysd['Stage'] = pd.Categorical(mysd['Stage'], ['MG', 'Orange', 'MR'])
    mysd['Tissue'] = pd.Categorical(mysd['Tissue'], ['Peel', 'Flesh', 'Seed'])
    mysd = mysd.sort_values(['Stage', 'Tissue'])

    ### 建立新的标签
    Label = []
    for mean, std in zip(mymean['Value'], mysd['Value']):
        Label.append(f"{mean:.1f} ± {std:.1f}")

    mylabel = np.array(Label).reshape(3, 3).T  ## 需转置

    ##(3.3) 画图, 你可以在plt.rcParams参数中自行调节图片大小
    plt.rcParams['figure.figsize'] = (8, 6)
    result = mymean.pivot(index='Tissue', columns='Stage', values='Value')

    sns.heatmap(result, annot=mylabel, square=True, fmt="", cmap="Reds", linewidths=0.5, robust=True)
    plt.xlabel('Tissue Type')
    plt.ylabel('Log2 Transformed Intensity')
    plt.savefig(pic_path)  # 保存图片
    plt.clf()


def _parse_mz_intensity(data: str) -> (np.ndarray, np.ndarray):
    ''' 解析 验证 数据
    :param data:
    :return:
    '''
    data = data.replace('\t', ' ')
    nz_data = data.split('\n')
    nz_data = [row.split(' ') for row in nz_data if row.strip()]
    arr = np.array(nz_data, dtype=np.float32)
    mz = arr[:, 0]
    intensity = arr[:, 1]
    return mz, intensity


def parse_mz_intensity(data: str) -> (np.ndarray, np.ndarray):
    ''' 解析 验证 数据
    :param data:
    :return:
    '''
    mz, intensity = _parse_mz_intensity(data)
    intensity = np.round(intensity / np.max(intensity) * 100, 1)
    return mz, intensity


def parse_serial_data(data: str) -> [int]:
    '''解析 验证 数据
    :param data: 参考数据 100, 120, 120, 230, 246, 233, 709, 780, 680, 50, 40, 37, 144, 143, 156, 344, 330, 290, 3, 6, 7, 21, 18, 19, 44, 43, 33
    :return:
    '''
    data = [i.strip() for i in data.split(',') if i.strip()]
    if len(data) != 14:
        raise ValueError('number of elements must be 14')
    try:
        data = [int(i) for i in data]
    except (TypeError, ValueError):
        raise ValueError('Only accept int')
    return data


def plot_mz_intensity_bar(data: str):
    mz, intensity = parse_mz_intensity(data=data)
    s_width = 0.003 * (np.max(mz) - np.min(mz))
    fig = go.Figure(data=[go.Bar(x=mz, y=intensity, width=s_width)])
    fig.update_layout(xaxis=dict(range=[np.min(mz) - 10 * s_width, np.max(mz) + 10 * s_width]), autosize=False, width=1024, height=600,
        paper_bgcolor='white', xaxis_title='m/z', yaxis_title='Intensity')
    return plot(fig, output_type='div', include_plotlyjs=False)


def plot_complex_bar(data: str, user_data: str):
    matchedmz, matchedint = parse_mz_intensity(data)
    usermz, userint = parse_mz_intensity(user_data)

    # 确保线条的宽度一致
    mzs = np.concatenate([matchedmz, usermz])
    s_width = 0.003 * (np.max(mzs) - np.min(mzs))
    # plotly
    fig = go.Figure()
    fig.add_trace(go.Bar(x=matchedmz, y=matchedint, width=s_width, name='MTDB'))
    fig.add_trace(go.Bar(x=usermz, y=userint * -1, width=s_width, name='User'))

    fig.update_layout(xaxis=dict(range=[np.min(mzs) - 10 * s_width, np.max(mzs) + 10 * s_width]), autosize=False,
                      width=990, height=600, paper_bgcolor='white', xaxis_title='m/z', yaxis_title='Intensity',
                      barmode='relative')
    return plot(fig, output_type='div', include_plotlyjs=False)


def generate_fish_html(params):
    """

    """
    # (1) color scheme, last color (black) is for the default
    colors = ["#f7f7f7", "#fcbba1", "#fc9272", "#fb6a4a", "#de2d26", "#a50f15", "#000000"]

    # (2) 示例数据，14个组织
    d = {
        'eyes': params[0],
        'buccalGland': params[1],
        'brain': params[2],
        'gills': params[3],
        'muscle': params[4],
        'heart': params[5],
        'liver': params[6],
        'blood': params[7],
        'supraneuralBody': params[8],
        'notochord': params[9],
        'kidney': params[10],
        'ovary': params[11],
        'intestine': params[12],
        'testis': params[13]
        }
    # 归一化数据，每列除以该数据的最大值
    myInt = pd.Series(data=d)
    ## Max-scaling, and avoid dzero division error
    if np.all((myInt == 0)):
        myInt = myInt
    else:
        myInt = myInt / max(myInt)

    # (3) load the SVG image
    # svg = open('data/Fish_Name.svg', 'r').read()
    svg = svg_model
    soup = BeautifulSoup(svg, features="html.parser")
    paths = soup.findAll('path')

    # (4) Change colors accordingly
    path_style = 'font-size:12px; fill-rule:nonzero; stroke:#000000; stroke-opacity:1; stroke-width:0.2; stroke-miterlimit:4; stroke-dasharray:none; stroke-linecap:butt; marker-start:none; stroke-linejoin:bevel; fill:'
    for p in paths:
        # assign intensity
        if p['id'] == 'eyeball':
            tissueInt = 2
        elif p['id'] not in myInt:
            tissueInt = 0
        else:
            tissueInt = myInt[p['id']]
        # assign color to different tissues
        if tissueInt == 2:
            color_class = 6
        elif 0.8 <= tissueInt <= 1:
            color_class = 5
        elif 0.6 <= tissueInt < 0.8:
            color_class = 4
        elif 0.4 <= tissueInt < 0.6:
            color_class = 3
        elif 0.2 <= tissueInt < 0.4:
            color_class = 2
        elif 0.1 <= tissueInt < 0.2:
            color_class = 1
        else:
            color_class = 0
        # get color
        color = colors[color_class]
        p['style'] = path_style + color

    # (5) Save the heatmap in HTML format
    html = soup.prettify()
    return str(html)
