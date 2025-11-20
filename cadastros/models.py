from django.db import models
from django.db.models import Max

class Escola(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

class Diagnostico(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    sigla = models.CharField(max_length=20, blank=True, null=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

class Terapia(models.Model):
    class ColorChoices(models.TextChoices):
        PRIMARY = 'primary', 'Azul'
        SUCCESS = 'success', 'Verde'
        WARNING = 'warning', 'Amarelo'
        DANGER = 'danger', 'Vermelho'
        INFO = 'info', 'Ciano'
        SECONDARY = 'secondary', 'Cinza'
        DARK = 'dark', 'Preto'
    nome = models.CharField(max_length=100, unique=True)
    sigla = models.CharField(max_length=30, blank=True, null=True)
    ativo = models.BooleanField(default=True)
    cor = models.CharField(
        max_length=20,
        choices=ColorChoices.choices,
        default=ColorChoices.PRIMARY,
        blank=True, null=True
    )

    def __str__(self):
        return self.nome

class Aluno(models.Model):
    class SerieEscolar(models.TextChoices):
        BERCARIO_I = 'BERÇÁRIO I', 'Berçário I'
        BERCARIO_II = 'BERÇÁRIO II', 'Berçário II'
        MATERNAL_I = 'MATERNAL I', 'Maternal I'
        MATERNAL_II = 'MATERNAL II', 'Maternal II'
        PRE_I = 'PRE I', 'Pré I'
        PRE_II = 'PRE II', 'Pré II'
        PRIMEIRO_ANO = '1ANO', '1º Ano'
        SEGUNDO_ANO = '2ANO', '2º Ano'
        TERCEIRO_ANO = '3ANO', '3º Ano'
        QUARTO_ANO = '4ANO', '4º Ano'
        QUINTO_ANO = '5ANO', '5º Ano'
        NAO_DEFINIDO = 'ND', 'Não Definido'


    nome_completo = models.CharField(max_length=200)
    escola = models.ForeignKey(Escola, on_delete=models.PROTECT)
    ano_escolar = models.CharField(
        max_length=20,
        choices=SerieEscolar.choices,
        default=SerieEscolar.NAO_DEFINIDO
    )

    transporte_escolar = models.BooleanField(default=False)
    ativo = models.BooleanField(default=True)
    numero_vaga = models.PositiveIntegerField(unique=True, null=True, blank=True, editable=False)
    diagnostico = models.ForeignKey(Diagnostico, on_delete=models.PROTECT, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            max_vaga = Aluno.objects.aggregate(Max('numero_vaga'))['numero_vaga__max']

            if max_vaga is None:
                self.numero_vaga = 1
            else:
                self.numero_vaga = max_vaga + 1

        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome_completo

class Matricula(models.Model):

    class DiaSemana(models.TextChoices):
        SEGUNDA = 'SEG', 'Segunda-feira'
        TERCA = 'TER', 'Terça-feira'
        QUARTA = 'QUA', 'Quarta-feira'
        QUINTA = 'QUI', 'Quinta-feira'
        SEXTA = 'SEX', 'Sexta-feira'

    class StatusMatricula(models.TextChoices):
        ATIVO = 'ATIVO', 'Ativo'
        INATIVO = 'INATIVO', 'Inativo'
        LISTA_ESPERA = 'LISTA', 'Lista de Espera'
        CONCLUIDO = 'CONCL', 'Concluído'

    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)
    terapia = models.ForeignKey(Terapia, on_delete=models.PROTECT)
    dia_da_semana = models.CharField(
        max_length=3,
        choices=DiaSemana.choices,
    )
    horario_inicio = models.TimeField()
    horario_fim = models.TimeField()
    data_matricula = models.DateField(auto_now_add=True)
    status = models.CharField(
        max_length=10,
        choices=StatusMatricula.choices,
        default=StatusMatricula.ATIVO
    )

    def __str__(self):
        return f"{self.aluno.nome_completo} - {self.terapia.nome} ({self.get_dia_da_semana_display()})"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['aluno', 'terapia'],
                name='matricula_unica_por_aluno'
            )
        ]


class Falta(models.Model):
    class StatusFalta(models.TextChoices):
        PRESENTE = 'P', 'Presente'
        FALTA = 'F', 'Falta'
        FALTA_JUSTIFICADA = 'FJ', 'Falta Justificada'

    matricula = models.ForeignKey(Matricula, on_delete=models.CASCADE)

    data = models.DateField()

    status = models.CharField(
        max_length=2,
        choices=StatusFalta.choices,
        default=StatusFalta.PRESENTE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['matricula', 'data'],
                name='registro_unico_por_dia'
            )
        ]

    def __str__(self):
        return f"{self.matricula.aluno.nome_completo} - {self.data} ({self.get_status_display()})"