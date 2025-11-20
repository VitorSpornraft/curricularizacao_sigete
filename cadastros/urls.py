# cadastros/urls.py

from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('', RedirectView.as_view(url='/login/', permanent=False)),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # --- ROTA DA DASHBOARD ---
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # --- ROTA DA FREQUÊNCIA ---
    path('frequencia/', views.frequencia_view, name='frequencia'),

    # --- ROTAS DE ALUNO ---
    path('cadastros/', views.gerenciamento_cadastros_view, name='cadastros'),
    path('cadastros/novo/', views.aluno_create_view, name='aluno_novo'),
    path('cadastros/arquivados/', views.aluno_arquivados_view, name='aluno_arquivados'),
    path('cadastros/<int:pk>/editar/', views.aluno_update_view, name='aluno_editar'),
    path('cadastros/<int:pk>/arquivar/', views.aluno_archive_view, name='aluno_arquivar'),
    path('cadastros/<int:pk>/restaurar/', views.aluno_restore_view, name='aluno_restaurar'),
    path('cadastros/<int:pk>/excluir-permanente/', views.aluno_delete_view, name='aluno_delete_permanente'),

    # --- ROTAS DE ESCOLA ---
    path('escolas/', views.escola_list_view, name='escola_list'),
    path('escolas/novo/', views.escola_create_view, name='escola_novo'),
    path('escolas/arquivados/', views.escola_arquivados_view, name='escola_arquivados'),
    path('escolas/<int:pk>/editar/', views.escola_update_view, name='escola_editar'),
    path('escolas/<int:pk>/arquivar/', views.escola_archive_view, name='escola_arquivar'),
    path('escolas/<int:pk>/restaurar/', views.escola_restore_view, name='escola_restaurar'),
    path('escolas/<int:pk>/excluir-permanente/', views.escola_delete_view, name='escola_delete_permanente'),

    # --- ROTAS DE TERAPIA ---
    path('terapias/', views.terapia_list_view, name='terapia_list'),
    path('terapias/novo/', views.terapia_create_view, name='terapia_novo'),
    path('terapias/arquivados/', views.terapia_arquivados_view, name='terapia_arquivados'),
    path('terapias/<int:pk>/editar/', views.terapia_update_view, name='terapia_editar'),
    path('terapias/<int:pk>/arquivar/', views.terapia_archive_view, name='terapia_arquivar'),
    path('terapias/<int:pk>/restaurar/', views.terapia_restore_view, name='terapia_restaurar'),
    path('terapias/<int:pk>/excluir-permanente/', views.terapia_delete_view, name='terapia_delete_permanente'),

    # --- ROTAS DE DIAGNÓSTICO ---
    path('diagnosticos/', views.diagnostico_list_view, name='diagnostico_list'),
    path('diagnosticos/novo/', views.diagnostico_create_view, name='diagnostico_novo'),
    path('diagnosticos/arquivados/', views.diagnostico_arquivados_view, name='diagnostico_arquivados'),
    path('diagnosticos/<int:pk>/editar/', views.diagnostico_update_view, name='diagnostico_editar'),
    path('diagnosticos/<int:pk>/arquivar/', views.diagnostico_archive_view, name='diagnostico_arquivar'),
    path('diagnosticos/<int:pk>/restaurar/', views.diagnostico_restore_view, name='diagnostico_restaurar'),
    path('diagnosticos/<int:pk>/excluir-permanente/', views.diagnostico_delete_view,
         name='diagnostico_delete_permanente'),
]