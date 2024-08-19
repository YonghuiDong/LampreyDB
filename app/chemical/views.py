from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.http import Http404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage, PageNotAnInteger
from django.conf import settings
from urllib.parse import quote
from . import models
from . import forms
from . import utils


def index(request):
    return render(request, template_name='chemical/index.html')


@login_required
def material_create(request):

    if request.method == 'POST':
        form = forms.MaterialCreateForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            data = []
            for i in range(14):
                _ = form.cleaned_data[f's{i}']
                if isinstance(_, (float, int)):
                    data.append(str(_))
                else:
                    data.append('nan')
            material.serials_data = ','.join(data)
            if material.serials_data:
                material.generate_fish_map_html()

            material.save()
            messages.success(request, 'The Chemical Material Created')
            return redirect(reverse('chemical:material_view', args=[material.id]))
    else:
        form = forms.MaterialCreateForm()

    return render(request, 'chemical/material_create.html', context=dict(
        title='Create Chemical Material', form=form
        ))


@login_required
def material_edit(request, material_id):
    material = get_object_or_404(klass=models.Material, id=material_id)
    if request.method == 'POST':
        form = forms.MaterialCreateForm(data=request.POST, files=request.FILES, instance=material)
        if form.is_valid():
            material = form.save(commit=False)
            data = []
            for i in range(14):
                _ = form.cleaned_data[f's{i}']
                if isinstance(_, (float, int)):
                    data.append(str(_))
                else:
                    data.append('nan')
            data = ','.join(data)
            if material.serials_data != data:
                material.serials_data = data

            if 'smiles' in form.changed_data:
                material.generate_smiles_image()
            material.generate_fish_map_html()

            material.save()

            messages.success(request, 'The Chemical Material Updated')
            return redirect(reverse('chemical:material_view', args=[material.id]))
    else:
        form = forms.MaterialCreateForm(instance=material)
    return render(request, 'chemical/material_create.html', context=dict(title='Update Chemical Material', form=form))


def material_view(request, material_id):
    material = get_object_or_404(klass=models.Material, id=material_id)

    user_mz_int = request.GET.get('mz_int')
    try:
        utils.parse_mz_intensity(user_mz_int)
        plot = utils.plot_complex_bar(data=material.mz_int, user_data=user_mz_int)
        plot_title = 'Compared MSE Spectrum'
    except:
        plot = utils.plot_mz_intensity_bar(data=material.mz_int)
        plot_title = 'MS/MS Spectrum'

    return render(request, 'chemical/material_view.html', context=dict(
        title='Material Details', material=material, plot=plot, plot_title=plot_title
        ))


def material_list(request,):
    page, per_page, sort, order = paginator_helper(request)

    if order == 'asc':
        pass
    else:
        sort = f'-{sort}'
    ls = models.Material.objects.order_by(sort)
    form = forms.MaterialSearchForm(data=request.GET, initial={'tolerance': 0.05})
    if form.is_valid():
        formula = form.cleaned_data['formula']
        mz = form.cleaned_data['mz']
        ion_mode = form.cleaned_data['ion_mode']
        tolerance = form.cleaned_data['tolerance']

        if formula:
            ls = ls.filter(formula__icontains=formula)
        if isinstance(mz, (float, int)) and isinstance(tolerance, (float, int)):
            ls = ls.filter(ion_mode=ion_mode)
            ls = ls.filter(mz__gte=mz-tolerance)
            ls = ls.filter(mz__lte=mz+tolerance)

    ls = ls.all()
    paginator = Paginator(object_list=ls, per_page=per_page)
    try:
        ls = paginator.page(page)
    except PageNotAnInteger:
        ls = paginator.page(1)
    except EmptyPage:
        ls = paginator.page(paginator.num_pages)
    q_url = f'/material/list?sort={sort}&order={order}'
    return render(request, 'chemical/material_list.html', context=dict(title='Metabolite List', ls=ls, q_url=q_url, form=form))


@login_required
def material_delete(request, material_id):
    material = get_object_or_404(klass=models.Material, id=material_id)
    material.delete()
    messages.warning(request, message='Chemical Material Deleted')
    return redirect(reverse('chemical:material_list'))


def paginator_helper(request) -> (int, int, str, str):
    page = request.GET.get('page', '1')
    try:
        page = int(page)
    except (TypeError, ValueError):
        page = 1
    per_page = request.GET.get('per_page', settings.PAGINATE_PER_PAGE)
    try:
        per_page = int(per_page)
    except (TypeError, ValueError):
        per_page = settings.PAGINATE_PER_PAGE
    order = request.GET.get('order', 'asc')
    if order != 'asc':
        order = 'desc'
    sort = request.GET.get('sort', 'code')
    if sort not in ['code', 'name', 'rt', 'mz', 'adduct_ion', 'formula', 'ms_level']:
        sort = 'code'
    return page, per_page, sort, order


def about(request):
    ab = models.AboutProject.objects.first()
    return render(request, 'about.html', context=dict(
        title='About This Project', ab=ab
        ))


def contact(request):
    ct = models.Contact.objects.first()
    return render(request, 'contact.html', context=dict(
        title='Contact Us', ct=ct
        ))


def material_search(request):
    ''''''
    data = []
    user_mz_int = ''
    form = forms.MaterialAdvancedSearchForm(request.GET)
    if form.is_valid():
        mz = form.cleaned_data['mz']
        ion_mode = form.cleaned_data['ion_mode']
        tolerance = form.cleaned_data['tolerance']
        mt = form.cleaned_data['mt']
        threshold = form.cleaned_data['threshold']
        mz_int = form.cleaned_data['mz_int']
        user_mz_int = quote(mz_int)
        code_arr, score_arr = models.filter_data(
            mz=mz, mz_int_raw=mz_int, tolerance=tolerance, iod_mod=ion_mode, mt=mt,
            threshold=threshold)
        data = []
        for i, code in enumerate(code_arr):
            m = models.Material.objects.filter(code=code).first()
            score = score_arr[i]
            data.append((m, score))
    print(data)
    return render(request, 'chemical/material_search.html', context=dict(
        title='MS/MS Search',
        form=form,
        data=data,
        user_mz_int=user_mz_int
        ))


@login_required
def about_update(request):
    if not request.user.is_superuser:
        raise Http404
    ab = models.AboutProject.objects.first()
    if request.method == 'POST':
        form = forms.AboutProjectEditForm(data=request.POST, files=request.FILES, instance=ab)
        if form.is_valid():
            form.save()
            messages.success(request, 'Content Updated')
            return redirect(reverse('chemical:about'))
    else:
        form = forms.AboutProjectEditForm(instance=ab)
    return render(request, 'info/about_project_edit.html', context=dict(
        title='Update About Project Content', form=form, db=ab
        ))


@login_required
def contact_update(request):
    if not request.user.is_superuser:
        raise Http404
    ct = models.Contact.objects.first()
    if request.method == 'POST':
        form = forms.ContactEditForm(data=request.POST, files=request.FILES, instance=ct)
        if form.is_valid():
            form.save()
            messages.success(request, 'Content Updated')
            return redirect(reverse('chemical:contact'))
    else:
        form = forms.ContactEditForm(instance=ct)
    return render(request, 'info/contact_edit.html', context=dict(
        title='Update Contact', form=form, ct=ct
        ))