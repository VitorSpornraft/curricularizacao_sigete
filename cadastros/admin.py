from django.contrib import admin
from .models import Escola, Diagnostico, Terapia, Aluno, Matricula

class MatriculaInline(admin.TabularInline):
    model = Matricula
    extra = 1

class AlunoAdmin(admin.ModelAdmin):
    inlines = [MatriculaInline]

admin.site.register(Escola)
admin.site.register(Diagnostico)
admin.site.register(Terapia)
admin.site.register(Aluno, AlunoAdmin)
