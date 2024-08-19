from django.db import models
from django.conf import settings
import os
import numpy as np
import heapq
from . import utils
import json

ion_mode_choices = (
    (1, 'Positive'),
    (2, 'Negative'),
)


class Material(models.Model):
    code = models.CharField(verbose_name='ID', max_length=128)
    name = models.CharField(verbose_name='Name', max_length=255)
    rt = models.FloatField(verbose_name='RT')
    mz = models.FloatField(verbose_name='m/z')
    adduct_ion = models.CharField(verbose_name='Adduct Ion', max_length=128)
    ion_mode = models.SmallIntegerField(verbose_name='Ion Mode', default=1, choices=ion_mode_choices, null=False, blank=False)
    formula = models.CharField(verbose_name='Formula', max_length=255)

    # ms_level = models.IntegerField(verbose_name='MS Level')
    ms_level = models.CharField(verbose_name='Class', max_length=255, blank=True, null=True)  # 20200608 用户变更改需求
    smiles = models.CharField(verbose_name='Smiles', max_length=1024, null=True, blank=True)
    in_chi_key = models.CharField(verbose_name='inChiKey', max_length=1024, null=True, blank=True)
    created = models.DateTimeField(verbose_name='Creation Date', auto_now_add=True)
    updated = models.DateTimeField(verbose_name='Modification Date', auto_now=True)
    mz_int = models.TextField(verbose_name='mz/Int')
    note = models.TextField(verbose_name='Note', null=True, blank=True)

    # mg = models.ImageField(verbose_name='MG', upload_to='mg/%Y/%m/%d', null=True, blank=True)
    # orange = models.ImageField(verbose_name='Orange', upload_to='orange/%Y/%m/%d', null=True, blank=True)
    # mr = models.ImageField(verbose_name='MR', upload_to='mr/%Y/%m/%d', null=True, blank=True)
    #
    # maldi_note = models.TextField(verbose_name='MALDI Images Note', null=True, blank=True)
    serials_data = models.CharField(verbose_name='For Fish Map', max_length=512)
    fish_map_content = models.TextField(verbose_name='fish_map_content', null=True, blank=True)

    class Meta:
        ordering = '-created', 'code',
        verbose_name = 'Material'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    @property
    def smiles_url(self):
        if not self.id:
            return ''
        if not self.smiles:
            return ''
        svg_path = os.path.join(settings.MEDIA_ROOT, 'smiles', f'{self.id}.svg')
        if not os.path.exists(svg_path):
            self.generate_smiles_image()
        return f'/media/smiles/{self.id}.svg'

    def generate_smiles_image(self):
        if not self.id:
            return False
        if not self.smiles:
            return False
        if not self.smiles.strip():
            return False
        svg_path = os.path.join(settings.MEDIA_ROOT, 'smiles', f'{self.id}.svg')
        svg_dir = os.path.dirname(svg_path)
        if not os.path.exists(svg_dir):
            os.makedirs(svg_dir, exist_ok=True)
        utils.generate_chemical_smiles(smiles_string=self.smiles, svg_path=svg_path)
        return True

    def generate_heat_map(self):
        svg_path = os.path.join(settings.MEDIA_ROOT, 'heatmap', f'{self.id}.png')
        svg_dir = os.path.dirname(svg_path)
        if not os.path.exists(svg_dir):
            os.makedirs(svg_dir, exist_ok=True)
        utils.generate_heat_map(data=self.serials_data, pic_path=svg_path)
        return True

    def generate_fish_map_html(self):
        if self.serials_data:
            html = utils.generate_fish_html(
                utils.parse_serial_data(self.serials_data)
                )
        else:
            html = '<p>No Content</p>'
        self.fish_map_content = json.dumps({'key': self.serials_data, 'html': html})
        return html

    def get_fish_map_html(self):
        html = None
        if self.fish_map_content:
            html = json.loads(self.fish_map_content).get('html')
        return html or '<p>Image Does Not Exist</p>'

    @property
    def heat_map_url(self):
        svg_path = os.path.join(settings.MEDIA_ROOT, 'heatmap', f'{self.id}.png')
        if not os.path.exists(svg_path):
            self.generate_heat_map()
        return f'/media/heatmap/{self.id}.png'

    @property
    def ion_mode_verbose(self):
        for k, v in ion_mode_choices:
            if k == self.ion_mode:
                return v
        return 'Unknown'


def filter_data(mz: float, mz_int_raw: str,
                tolerance: float, iod_mod: int, mt: float,
                threshold: float) -> (np.ndarray, np.ndarray):
    '''
    :param mz: Precursor m/z
    :param mz_int_raw: Peaks
    :param tolerance: Precursor Tolerance
    :param iod_mod: Ion Mode
    :param mt: MS/MS Tolerance
    :param threshold: Score Threshold
    :return:
    '''
    id_arr = []
    precursor_db = []
    mse_db = []
    int_db = []

    for m in Material.objects.filter(ion_mode=iod_mod).all():  # 过滤用户选择的 ion mode， 1 P， 2 N
        # 查询数据库，搜集必要的数据
        print(m.code)
        id_arr.append(m.code)
        __mz, __intensity = utils._parse_mz_intensity(m.mz_int)
        mse_db.append(__mz)
        int_db.append(__intensity)
        precursor_db.append(m.mz)

    ID = np.array(id_arr)  # 是化合物的ID
    precursorDB = np.array(precursor_db)  # 就是每个化合物的 mz
    mseDB = np.array(mse_db)  # 就是用来画质谱图的那一串 mz
    intDB = np.array(int_db)  # 就是用来画质谱图的那一串 mz 对应的 intensity

    # 预处理数据库例子，只选取前 10 个最大的 intensity 所对应的 mz
    topn = [heapq.nlargest(10, range(len(L)), key=L.__getitem__) for L in intDB]
    mseDB_sub = []
    for m, n in zip(topn, mseDB):
        mseDB_sub.append([n[i] for i in m])
    mseDB_sub = np.array(mseDB_sub)

    # #######################
    # 用户输入要检索的数据
    precursormz = mz
    usermz, userint = utils._parse_mz_intensity(mz_int_raw)
    # 只选取前 10 最大的 intensity 对应的 mz。
    user_inx = heapq.nlargest(10, range(len(userint)), key=userint.__getitem__)
    usermz_sub = usermz[user_inx]

    P_tolerance = tolerance  # 默认值，允许用户自定义
    index1 = np.where(np.abs(precursorDB - precursormz) <= P_tolerance)

    ## 选择符合条件1的mseDB
    mseDB_filter = mseDB_sub[index1]
    ID_filter = ID[index1]

    msms_tolerance = mt

    index2 = [[] for i in range(len(mseDB_filter))]
    for i in range(len(mseDB_filter)):
        # 计算匹配的mz百分比，用它作为得分
        index2[i] = len(usermz_sub[(np.abs(usermz_sub[:, None] - mseDB_filter[i]) <= msms_tolerance).any(1)]) / len(
            mseDB_filter[i])

    index2 = np.round(index2, 2)
    # 找到符合调节的化合物的ID
    score_threshold = threshold
    ID_filter2 = ID_filter[index2 > score_threshold]
    return ID_filter2, index2[index2 > score_threshold]


class AboutProject(models.Model):
    overview = models.TextField(verbose_name='OverView', null=False, blank=False)
    mtb = models.TextField(verbose_name='Metabolomics', null=False, blank=False)
    mtb_attach = models.FileField(verbose_name='Metabolomics Attach', upload_to='', null=True, blank=True)
    # lpd = models.TextField(verbose_name='Lipidomics', null=False, blank=False)
    # lpd_attach = models.FileField(verbose_name='Lipidomics Attach', upload_to='', null=True, blank=True)
    # mal = models.TextField(verbose_name='MALDI Imaging', null=False, blank=False)
    # mal_attach = models.FileField(verbose_name='MALDI Imaging Attach', upload_to='', null=True, blank=True)
    cite = models.TextField(verbose_name='Cite', null=False, blank=False)


class Contact(models.Model):
    content = models.TextField(verbose_name='Contact Content', blank=False, null=False)

