# cadastros/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import IntegrityError
from django.db.models import ProtectedError
from django.views.decorators.http import require_POST
from datetime import time, date, datetime
from .models import Aluno, Matricula, Escola, Terapia, Diagnostico, Falta
from .forms import AlunoForm, MatriculaFormSet, EscolaForm, DiagnosticoForm, TerapiaForm
from django.contrib.auth.decorators import login_required


def home(request):
    """
    View para a página inicial do sistema.
    """
    return render(request, 'home.html')


def login_view(request):
    """
    View para a página de login.
    """
    return render(request, 'login.html')

@login_required
def dashboard_view(request):
    """
    View para a dashboard principal de consultas.
    Agora com filtros de nome, ESCOLA, dia e turno.
    """

    lista_de_atendimentos = Matricula.objects.filter(aluno__ativo=True).order_by('dia_da_semana', 'horario_inicio')

    filtro_nome = request.GET.get('busca_nome')
    filtro_escola = request.GET.get('filtro_escola')
    filtro_dia = request.GET.get('filtro_dia')
    filtro_turno = request.GET.get('filtro_turno')

    if filtro_nome:
        lista_de_atendimentos = lista_de_atendimentos.filter(
            aluno__nome_completo__icontains=filtro_nome
        )

    if filtro_escola:
        lista_de_atendimentos = lista_de_atendimentos.filter(
            aluno__escola__id=filtro_escola
        )

    if filtro_dia:
        lista_de_atendimentos = lista_de_atendimentos.filter(
            dia_da_semana__exact=filtro_dia
        )

    if filtro_turno == 'manha':
        lista_de_atendimentos = lista_de_atendimentos.filter(
            horario_inicio__lt=time(12, 0)
        )
    elif filtro_turno == 'tarde':
        lista_de_atendimentos = lista_de_atendimentos.filter(
            horario_inicio__gte=time(12, 0)
        )

    escolas = Escola.objects.filter(ativo=True)

    context = {
        'atendimentos': lista_de_atendimentos,
        'escolas': escolas,
        'busca_nome_selecionado': filtro_nome,
        'filtro_escola_selecionado': filtro_escola,
        'filtro_dia_selecionado': filtro_dia,
        'filtro_turno_selecionado': filtro_turno,
    }

    return render(request, 'dashboard_consultas.html', context)

@login_required
def frequencia_view(request):
    """
    View para a página de registro de frequência.
    Filtra por DATA (que define o dia), TERAPIA e TURNO.
    """
    terapias = Terapia.objects.all()

    filtro_data_str = request.GET.get('data') or request.POST.get('data')

    if filtro_data_str:
        try:
            data_chamada = datetime.strptime(filtro_data_str, '%Y-%m-%d').date()
        except ValueError:
            data_chamada = date.today()
    else:
        data_chamada = date.today()

    mapa_dias = {0: 'SEG', 1: 'TER', 2: 'QUA', 3: 'QUI', 4: 'SEX', 5: 'SAB', 6: 'DOM'}
    dia_automatico = mapa_dias.get(data_chamada.weekday())

    filtro_terapia_id = request.GET.get('terapia') or request.POST.get('terapia_id')
    filtro_turno = request.GET.get('turno') or request.POST.get('turno')

    lista_de_chamada = Matricula.objects.filter(
        aluno__ativo=True,
        status=Matricula.StatusMatricula.ATIVO,
        dia_da_semana=dia_automatico

    ).order_by('horario_inicio', 'aluno__nome_completo')

    if filtro_terapia_id:
        lista_de_chamada = lista_de_chamada.filter(terapia__id=filtro_terapia_id)

    if filtro_turno == 'manha':
        lista_de_chamada = lista_de_chamada.filter(horario_inicio__lt=time(12, 0))
    elif filtro_turno == 'tarde':
        lista_de_chamada = lista_de_chamada.filter(horario_inicio__gte=time(12, 0))

    if request.method == 'POST':
        count_salvos = 0
        for matricula in lista_de_chamada:
            status_form = request.POST.get(f'status_{matricula.id}')
            if status_form:
                Falta.objects.update_or_create(
                    matricula=matricula,
                    data=data_chamada,
                    defaults={'status': status_form}
                )
                count_salvos += 1

        messages.success(request, f'Chamada salva para {count_salvos} alunos em {data_chamada.strftime("%d/%m/%Y")}!')
        return redirect(
            f'/frequencia/?data={data_chamada}&terapia={filtro_terapia_id or ""}&turno={filtro_turno or ""}')

    registros_de_falta = Falta.objects.filter(data=data_chamada)
    faltas_dict = {f.matricula_id: f.status for f in registros_de_falta}

    for matricula in lista_de_chamada:
        matricula.status_hoje = faltas_dict.get(matricula.id)

    bloqueado = (data_chamada != date.today())

    context = {
        'terapias': terapias,
        'lista_de_chamada': lista_de_chamada,
        'data_chamada_str': data_chamada.isoformat(),
        'filtro_terapia_selecionado': filtro_terapia_id,
        'filtro_turno_selecionado': filtro_turno,
        'bloqueado': bloqueado,
    }
    return render(request, 'frequencia.html', context)

@login_required
def gerenciamento_cadastros_view(request):
    """
    View para a página de gerenciamento de cadastros (lista de alunos).
    """
    filtro_nome = request.GET.get('busca_nome')
    filtro_escola = request.GET.get('filtro_escola')
    filtro_terapia = request.GET.get('filtro_terapia')

    alunos_list = Aluno.objects.filter(ativo=True)

    if filtro_nome:
        alunos_list = alunos_list.filter(
            nome_completo__icontains=filtro_nome
        )
    if filtro_escola:
        alunos_list = alunos_list.filter(
            escola__id=filtro_escola
        )
    if filtro_terapia:
        alunos_list = alunos_list.filter(
            matricula__terapia__id=filtro_terapia
        ).distinct()

    todas_as_escolas = Escola.objects.filter(ativo=True)
    todas_as_terapias = Terapia.objects.filter(ativo=True)

    context = {
        'alunos': alunos_list,
        'escolas': todas_as_escolas,
        'terapias': todas_as_terapias,
        'busca_nome_selecionado': filtro_nome,
        'filtro_escola_selecionado': filtro_escola,
        'filtro_terapia_selecionado': filtro_terapia,
    }
    return render(request, 'gerenciamento_cadastros.html', context)

@login_required
def aluno_arquivados_view(request):
    """
    View para a página de alunos arquivados.
    """
    alunos_list = Aluno.objects.filter(ativo=False)
    context = {
        'alunos': alunos_list,
    }
    return render(request, 'aluno_arquivados.html', context)

@login_required
def aluno_create_view(request):
    """
    View para cadastrar um novo aluno E suas matrículas.
    """
    form = AlunoForm()
    formset = MatriculaFormSet(instance=Aluno())
    if request.method == 'POST':
        form = AlunoForm(request.POST)
        formset = MatriculaFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            aluno_novo = form.save(commit=False)
            aluno_novo.save()
            formset.instance = aluno_novo
            formset.save()
            return redirect('cadastros')

    context = {
        'form': form,
        'formset': formset
    }
    return render(request, 'aluno_form.html', context)

@login_required
def aluno_update_view(request, pk):
    """
    View para ATUALIZAR um aluno existente e suas matrículas.
    """
    aluno = get_object_or_404(Aluno, pk=pk)

    if request.method == 'POST':
        form = AlunoForm(request.POST, instance=aluno)
        formset = MatriculaFormSet(request.POST, instance=aluno)

        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('cadastros')
    else:
        form = AlunoForm(instance=aluno)
        formset = MatriculaFormSet(instance=aluno)

    context = {
        'form': form,
        'formset': formset,
        'aluno': aluno
    }
    return render(request, 'aluno_form.html', context)

@login_required
@require_POST
def aluno_archive_view(request, pk):
    """
    View para arquivar um aluno (soft delete).
    """
    aluno = get_object_or_404(Aluno, pk=pk)
    aluno.ativo = False
    aluno.save()
    return redirect('cadastros')

@login_required
@require_POST
def aluno_restore_view(request, pk):
    """
    View para restaurar um aluno (reativar).
    """
    aluno = get_object_or_404(Aluno, pk=pk)
    aluno.ativo = True
    aluno.save()
    return redirect('aluno_arquivados')

@login_required
def aluno_delete_view(request, pk):
    """
    View para DELETAR PERMANENTEMENTE um aluno (hard delete).
    """
    aluno = get_object_or_404(Aluno, pk=pk)

    if request.method == 'POST':
        aluno.delete()
        messages.success(request, f'O aluno "{aluno.nome_completo}" foi excluído permanentemente.')
        return redirect('aluno_arquivados')

    context = {
        'aluno': aluno
    }
    return render(request, 'aluno_confirm_delete.html', context)

@login_required
def escola_list_view(request):
    """
    View para a página de gerenciamento de escolas.
    """
    filtro_nome = request.GET.get('busca_nome')
    escolas_list = Escola.objects.filter(ativo=True).order_by('nome')

    if filtro_nome:
        escolas_list = escolas_list.filter(nome__icontains=filtro_nome)

    context = {
        'escolas': escolas_list,
        'busca_nome_selecionado': filtro_nome,
    }
    return render(request, 'escola_list.html', context)

@login_required
def escola_arquivados_view(request):
    """
    View para a lista de escolas arquivadas.
    """
    escolas_list = Escola.objects.filter(ativo=False).order_by('nome')
    context = {
        'escolas': escolas_list,
    }
    return render(request, 'escola_arquivados.html', context)

@login_required
def escola_create_view(request):
    """
    View para criar uma nova escola.
    """
    if request.method == 'POST':
        form = EscolaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Escola cadastrada com sucesso.')
            return redirect('escola_list')
    else:
        form = EscolaForm()

    context = {
        'form': form
    }
    return render(request, 'escola_form.html', context)

@login_required
def escola_update_view(request, pk):
    """
    View para editar uma escola existente.
    """
    escola = get_object_or_404(Escola, pk=pk)
    if request.method == 'POST':
        form = EscolaForm(request.POST, instance=escola)
        if form.is_valid():
            form.save()
            messages.success(request, 'Escola atualizada com sucesso.')
            return redirect('escola_list')
    else:
        form = EscolaForm(instance=escola)

    context = {
        'form': form,
        'escola': escola
    }
    return render(request, 'escola_form.html', context)

@login_required
@require_POST
def escola_archive_view(request, pk):
    """
    View para arquivar uma escola (soft delete).
    """
    escola = get_object_or_404(Escola, pk=pk)
    escola.ativo = False
    escola.save()
    messages.info(request, f'A escola "{escola.nome}" foi arquivada.')
    return redirect('escola_list')

@login_required
@require_POST
def escola_restore_view(request, pk):
    """
    View para restaurar uma escola.
    """
    escola = get_object_or_404(Escola, pk=pk)
    escola.ativo = True
    escola.save()
    messages.success(request, f'A escola "{escola.nome}" foi restaurada.')
    return redirect('escola_arquivados')

@login_required
def escola_delete_view(request, pk):
    """
    View para DELETAR PERMANENTEMENTE uma escola.
    """
    escola = get_object_or_404(Escola, pk=pk)

    if request.method == 'POST':
        try:
            escola.delete()
            messages.success(request, f'A escola "{escola.nome}" foi excluída permanentemente.')
            return redirect('escola_arquivados')
        except ProtectedError:
            messages.error(request,
                           f'Erro: A escola "{escola.nome}" não pode ser excluída, pois ainda existem alunos vinculados a ela.'
                           )
            return redirect('escola_arquivados')

    context = {
        'escola': escola
    }
    return render(request, 'escola_confirm_delete.html', context)

@login_required
def diagnostico_list_view(request):
    """
    View para a página de gerenciamento de diagnósticos.
    """
    filtro_nome = request.GET.get('busca_nome')
    diagnosticos_list = Diagnostico.objects.filter(ativo=True).order_by('nome')

    if filtro_nome:
        diagnosticos_list = diagnosticos_list.filter(nome__icontains=filtro_nome)

    context = {
        'diagnosticos': diagnosticos_list,
        'busca_nome_selecionado': filtro_nome,
    }
    return render(request, 'diagnostico_list.html', context)

@login_required
def diagnostico_arquivados_view(request):
    """
    View para a lista de diagnósticos arquivados.
    """
    diagnosticos_list = Diagnostico.objects.filter(ativo=False).order_by('nome')
    context = {
        'diagnosticos': diagnosticos_list,
    }
    return render(request, 'diagnostico_arquivados.html', context)

@login_required
def diagnostico_create_view(request):
    """
    View para criar um novo diagnóstico.
    """
    if request.method == 'POST':
        form = DiagnosticoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Diagnóstico cadastrado com sucesso.')
            return redirect('diagnostico_list')
    else:
        form = DiagnosticoForm()

    context = {
        'form': form
    }
    return render(request, 'diagnostico_form.html', context)

@login_required
def diagnostico_update_view(request, pk):
    """
    View para editar um diagnóstico existente.
    """
    diagnostico = get_object_or_404(Diagnostico, pk=pk)
    if request.method == 'POST':
        form = DiagnosticoForm(request.POST, instance=diagnostico)
        if form.is_valid():
            form.save()
            messages.success(request, 'Diagnóstico atualizado com sucesso.')
            return redirect('diagnostico_list')
    else:
        form = DiagnosticoForm(instance=diagnostico)

    context = {
        'form': form,
        'diagnostico': diagnostico
    }
    return render(request, 'diagnostico_form.html', context)

@login_required
@require_POST
def diagnostico_archive_view(request, pk):
    """
    View para arquivar um diagnóstico (soft delete).
    """
    diagnostico = get_object_or_404(Diagnostico, pk=pk)
    diagnostico.ativo = False
    diagnostico.save()
    messages.info(request, f'O diagnóstico "{diagnostico.nome}" foi arquivado.')
    return redirect('diagnostico_list')

@login_required
@require_POST
def diagnostico_restore_view(request, pk):
    """
    View para restaurar um diagnóstico.
    """
    diagnostico = get_object_or_404(Diagnostico, pk=pk)
    diagnostico.ativo = True
    diagnostico.save()
    messages.success(request, f'O diagnóstico "{diagnostico.nome}" foi restaurado.')
    return redirect('diagnostico_arquivados')

@login_required
def diagnostico_delete_view(request, pk):
    diagnostico = get_object_or_404(Diagnostico, pk=pk)

    if request.method == 'POST':
        try:
            diagnostico.delete()
            messages.success(request, f'O diagnóstico "{diagnostico.nome}" foi excluído permanentemente.')
            return redirect('diagnostico_arquivados')
        except ProtectedError:
            messages.error(request,
                           f'Erro: O diagnóstico "{diagnostico.nome}" não pode ser excluído, pois existem alunos vinculados a ele.'
                           )
            return redirect('diagnostico_arquivados')

    context = {'diagnostico': diagnostico}
    return render(request, 'diagnostico_confirm_delete.html', context)

@login_required
def terapia_list_view(request):
    """
    View para a página de gerenciamento de terapias.
    """
    filtro_nome = request.GET.get('busca_nome')
    terapias_list = Terapia.objects.filter(ativo=True).order_by('nome')

    if filtro_nome:
        terapias_list = terapias_list.filter(nome__icontains=filtro_nome)

    context = {
        'terapias': terapias_list,
        'busca_nome_selecionado': filtro_nome,
    }
    return render(request, 'terapia_list.html', context)

@login_required
def terapia_arquivados_view(request):
    """
    View para a lista de terapias arquivadas.
    """
    terapias_list = Terapia.objects.filter(ativo=False).order_by('nome')
    context = {
        'terapias': terapias_list,
    }
    return render(request, 'terapia_arquivados.html', context)

@login_required
def terapia_create_view(request):
    """
    View para criar uma nova terapia.
    """
    if request.method == 'POST':
        form = TerapiaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Terapia cadastrada com sucesso.')
            return redirect('terapia_list')
    else:
        form = TerapiaForm()

    context = {
        'form': form
    }
    return render(request, 'terapia_form.html', context)

@login_required
def terapia_update_view(request, pk):
    """
    View para editar uma terapia existente.
    """
    terapia = get_object_or_404(Terapia, pk=pk)
    if request.method == 'POST':
        form = TerapiaForm(request.POST, instance=terapia)
        if form.is_valid():
            form.save()
            messages.success(request, 'Terapia atualizada com sucesso.')
            return redirect('terapia_list')
    else:
        form = TerapiaForm(instance=terapia)

    context = {
        'form': form,
        'terapia': terapia
    }
    return render(request, 'terapia_form.html', context)

@login_required
@require_POST
def terapia_archive_view(request, pk):
    """
    View para arquivar uma terapia (soft delete).
    """
    terapia = get_object_or_404(Terapia, pk=pk)
    terapia.ativo = False
    terapia.save()
    messages.info(request, f'A terapia "{terapia.nome}" foi arquivada.')
    return redirect('terapia_list')

@login_required
@require_POST
def terapia_restore_view(request, pk):
    """
    View para restaurar uma terapia.
    """
    terapia = get_object_or_404(Terapia, pk=pk)
    terapia.ativo = True
    terapia.save()
    messages.success(request, f'A terapia "{terapia.nome}" foi restaurada.')
    return redirect('terapia_arquivados')

@login_required
def terapia_delete_view(request, pk):
    terapia = get_object_or_404(Terapia, pk=pk)

    if request.method == 'POST':
        try:
            terapia.delete()
            messages.success(request, f'A terapia "{terapia.nome}" foi excluída permanentemente.')
            return redirect('terapia_arquivados')
        except ProtectedError:
            messages.error(request,
                           f'Erro: A terapia "{terapia.nome}" não pode ser excluída, pois existem matrículas vinculadas a ela.'
                           )
            return redirect('terapia_arquivados')

    context = {'terapia': terapia}
    return render(request, 'terapia_confirm_delete.html', context)