# coding: utf-8

from django import forms
from tempus_dominus.widgets import DateTimePicker
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from . import models
from . import utils

date_time_options = {
    'useCurrent': True,
    'format': 'YYYY-MM-D HH:mm'
    }


class MaterialCreateForm(forms.ModelForm):
    s0 = forms.IntegerField(label='0', required=True)
    s1 = forms.IntegerField(label='1', required=True)
    s2 = forms.IntegerField(label='2', required=True)
    s3 = forms.IntegerField(label='3', required=True)
    s4 = forms.IntegerField(label='4', required=True)
    s5 = forms.IntegerField(label='5', required=True)
    s6 = forms.IntegerField(label='6', required=True)
    s7 = forms.IntegerField(label='7', required=True)
    s8 = forms.IntegerField(label='8', required=True)
    s9 = forms.IntegerField(label='9', required=True)
    s10 = forms.IntegerField(label='10', required=True)
    s11 = forms.IntegerField(label='11', required=True)
    s12 = forms.IntegerField(label='12', required=True)
    s13 = forms.IntegerField(label='13', required=True)

    class Meta:
        model = models.Material
        fields = '__all__'
        exclude = 'serials_data',

        widgets = {
            'created': DateTimePicker(options=date_time_options),
            'updated': DateTimePicker(options=date_time_options),
            'smiles': forms.Textarea(attrs={'rows': 2})
            }

    def clean_mz_int(self):
        mz_int = self.cleaned_data.get('mz_int')
        try:
            utils.parse_mz_intensity(mz_int)
        except:
            raise forms.ValidationError("Cannot parse the data you typed.")
        return mz_int

    def clean_smiles(self):
        smiles: str = self.cleaned_data.get('smiles')
        if smiles:
            smiles = smiles.replace('\r', '').replace('\n', '').replace('\t', '')
        return smiles

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for i in range(14):
            self.fields[f's{i}'].widget.attrs.update({'placeholder': ''})
        if self.instance.id:
            for i, v in enumerate(self.instance.serials_data.split(',')):
                self.fields[f's{i}'].widget.attrs.update({'value': v})
                v = v.strip()
                if v != 'nan':
                    try:
                        float(v)
                        self.fields[f's{i}'].widget.attrs.update({'value': v})
                    except ValueError:
                        pass


class MaterialEditForm(forms.ModelForm):
    s0 = forms.IntegerField(label='0', required=True)
    s1 = forms.IntegerField(label='1', required=True)
    s2 = forms.IntegerField(label='2', required=True)
    s3 = forms.IntegerField(label='3', required=True)
    s4 = forms.IntegerField(label='4', required=True)
    s5 = forms.IntegerField(label='5', required=True)
    s6 = forms.IntegerField(label='6', required=True)
    s7 = forms.IntegerField(label='7', required=True)
    s8 = forms.IntegerField(label='8', required=True)
    s9 = forms.IntegerField(label='9', required=True)
    s10 = forms.IntegerField(label='10', required=True)
    s11 = forms.IntegerField(label='11', required=True)
    s12 = forms.IntegerField(label='12', required=True)
    s13 = forms.IntegerField(label='13', required=True)

    class Meta:
        model = models.Material
        fields = '__all__'
        exclude = 'serials_data',

        widgets = {
            'created': DateTimePicker(options=date_time_options),
            'updated': DateTimePicker(options=date_time_options), 
            'smiles': forms.Textarea(attrs={'rows': 2})
            }

    def clean_mz_int(self):
        mz_int = self.cleaned_data.get('mz_int')
        try:
            utils.parse_mz_intensity(mz_int)
        except:
            raise forms.ValidationError("Cannot parse the data you typed.")
        return mz_int
    
    def clean_smiles(self):
        smiles: str = self.cleaned_data.get('smiles')
        if smiles:
            smiles = smiles.replace('\r', '').replace('\n', '').replace('\t', '')
        return smiles

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for i in range(14):
            self.fields[f's{i}'].widget.attrs.update({'placeholder': ''})
        if self.instance.id:
            for i, v in enumerate(self.instance.serials_data.split(',')):
                self.fields[f's{i}'].widget.attrs.update({'value': v})
                v = v.strip()
                if v != 'nan':
                    try:
                        float(v)
                        self.fields[f's{i}'].widget.attrs.update({'value': v})
                    except ValueError:
                        pass


class MaterialSearchForm(forms.Form):
    ''''''
    formula = forms.CharField(required=True, max_length=255)
    mz = forms.FloatField(required=True, min_value=0)
    ion_mode = forms.ChoiceField(choices=models.ion_mode_choices, required=True)
    tolerance = forms.FloatField(min_value=0, required=True)


class MaterialAdvancedSearchForm(forms.Form):
    ''''''
    mz = forms.FloatField(required=True, min_value=0)
    ion_mode = forms.ChoiceField(choices=models.ion_mode_choices, required=True)
    tolerance = forms.FloatField(min_value=0, required=True)
    mz_int = forms.CharField(required=True, widget=forms.Textarea())
    mt = forms.FloatField(required=True, min_value=0)
    threshold = forms.FloatField(required=True, min_value=0, max_value=1)

    def clean_mz_int(self):
        mz_int = self.cleaned_data.get('mz_int')
        try:
            utils.parse_mz_intensity(mz_int)
        except:
            raise forms.ValidationError("Cannot parse the data you typed.")
        return mz_int


class AboutProjectEditForm(forms.ModelForm):
    class Meta:
        model = models.AboutProject
        fields = '__all__'
        widgets = {
            'overview': CKEditorUploadingWidget(),
            'mtb': CKEditorUploadingWidget(),
            # 'lpd': CKEditorUploadingWidget(),
            # 'mal': CKEditorUploadingWidget(),
            'cite': CKEditorUploadingWidget(),
            }


class ContactEditForm(forms.ModelForm):
    class Meta:
        model = models.Contact
        fields = '__all__'
        widgets = {
            'content': CKEditorUploadingWidget()
            }
