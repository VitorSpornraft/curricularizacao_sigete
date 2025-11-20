# cadastros/forms.py

from django import forms
from .models import Aluno, Matricula, Escola, Diagnostico, Terapia
from django.forms import inlineformset_factory, BaseInlineFormSet
from django.core.exceptions import ValidationError

class AlunoForm(forms.ModelForm):
    escola = forms.ModelChoiceField(
        queryset=Escola.objects.filter(ativo=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Escola"
    )
    diagnostico = forms.ModelChoiceField(
        queryset=Diagnostico.objects.filter(ativo=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False,
        label="Diagnóstico"
    )

    class Meta:
        model = Aluno
        fields = ['nome_completo', 'escola', 'ano_escolar', 'transporte_escolar', 'diagnostico']
        widgets = {
            'nome_completo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: João da Silva'}),
            'ano_escolar': forms.Select(attrs={'class': 'form-select'}),
            'transporte_escolar': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'nome_completo': 'Nome do Aluno',
            'ano_escolar': 'Série/Ano',
        }

class EscolaForm(forms.ModelForm):
    class Meta:
        model = Escola
        fields = ['nome']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: EMEF Prof. João Leão'}),
        }
        labels = {
            'nome': 'Nome da Escola',
        }

class DiagnosticoForm(forms.ModelForm):
    class Meta:
        model = Diagnostico
        fields = ['nome', 'sigla']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Transtorno do Espectro Autista'}),
            'sigla': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: TEA'}),
        }
        labels = {
            'nome': 'Nome do Diagnóstico',
            'sigla': 'Sigla (ex: TEA, TDAH)',
        }

class TerapiaForm(forms.ModelForm):
    class Meta:
        model = Terapia
        # 'ativo' é controlado pelos botões
        fields = ['nome', 'sigla', 'cor']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Equoterapia'}),
            'sigla': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Equo'}),
            'cor': forms.Select(attrs={'class': 'form-select'}), # O campo 'cor' já usa 'choices'
        }
        labels = {
            'nome': 'Nome da Terapia',
            'sigla': 'Sigla / Nome Curto (para a tabela)',
            'cor': 'Cor da Etiqueta (Badge)',
        }

class MatriculaForm(forms.ModelForm):
    terapia = forms.ModelChoiceField(
        queryset=Terapia.objects.filter(ativo=True),
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )

    class Meta:
        model = Matricula
        fields = ['terapia', 'dia_da_semana', 'horario_inicio', 'horario_fim', 'status']
        widgets = {
            'dia_da_semana': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'horario_inicio': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control form-control-sm'}),
            'horario_fim': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control form-control-sm'}),
            'status': forms.Select(attrs={'class': 'form-select form-select-sm'}),
        }

class BaseMatriculaFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return
        horarios = []
        for form in self.forms:
            if not form.cleaned_data or form.cleaned_data.get('DELETE'):
                continue
            dia = form.cleaned_data.get('dia_da_semana')
            inicio = form.cleaned_data.get('horario_inicio')
            fim = form.cleaned_data.get('horario_fim')
            if dia and inicio and fim:
                horarios.append((dia, inicio, fim, form))
        for i in range(len(horarios)):
            dia_a, inicio_a, fim_a, form_a = horarios[i]
            for j in range(i + 1, len(horarios)):
                dia_b, inicio_b, fim_b, form_b = horarios[j]
                if dia_a != dia_b:
                    continue
                if inicio_a < fim_b and fim_a > inicio_b:
                    raise ValidationError(
                        f"Conflito de horário detectado! A terapia "
                        f"'{form_a.cleaned_data.get('terapia')}' ({dia_a} {inicio_a}-{fim_a}) "
                        f"está colidindo com '{form_b.cleaned_data.get('terapia')}' ({dia_b} {inicio_b}-{fim_b})."
                    )

MatriculaFormSet = inlineformset_factory(
    Aluno,
    Matricula,
    form=MatriculaForm,
    extra=1,
    formset=BaseMatriculaFormSet,
    can_delete=True
)