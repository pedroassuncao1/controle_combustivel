from django.urls import path
from App_Combustivel import views
from django.contrib.auth import views as auth_views
from django.contrib import admin


urlpatterns = [
    path('admin/', admin.site.urls),
    path('cadastrar_usuario/', views.cadastrar_usuario, name='cadastrar_usuario'),
    # path('usuarios/', views.usuarios, name='listagem_usuarios'),
    path('', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('home/', views.login_sucesso, name='home'),
    path('cadastrar_veiculo/', views.cadastrar_veiculo, name='cadastrar_veiculo'),
    path('cadastrar_abastecimento/', views.cadastrar_abastecimento, name='cadastrar_abastecimento'),
    path('veiculos/', views.listar_veiculos, name='listar_veiculos'),
    path('veiculos/<int:veiculo_id>/abastecimento/', views.cadastrar_abastecimento, name='cadastrar_abastecimento'),
    path('remover_veiculo/', views.remover_veiculo_view, name='remover_veiculo_view'),
    path('remover_veiculo/<int:veiculo_id>/remover/', views.remover_veiculo, name='remover_veiculo'),
    path('listar_veiculos_informacoes/', views.listar_veiculos_para_informacoes, name='listar_veiculos_informacoes'),
    path('exibir_informacoes/<int:veiculo_id>/', views.exibir_informacoes_veiculo, name='exibir_informacoes_veiculo'),
    path('grafico/', views.grafico_consumo, name='grafico_consumo'),
    path('mais_opcoes/', views.mais_opcoes, name='mais_opcoes'),
    path('trocar_senha/', views.TrocarSenhaView.as_view(), name='trocar_senha'),
    path('senha_trocada/', views.SenhaTrocadaComSucessoView.as_view(), name='senha_trocada_com_sucesso'),
    path('apagar_usuario', views.apagar_usuario, name='apagar_usuario'),
    path('detalhes_veiculo/<int:veiculo_id>/', views.detalhes_veiculo, name='detalhes_veiculo'),
    path('troca_oleo/', views.troca_oleo, name='troca_oleo'),
    path('detalhes_consumo/<int:veiculo_id>/<str:tipo>/', views.detalhes_consumo, name='detalhes_consumo'),
    
    
]


handler404 = 'App_Combustivel.views.error_404_view'
handler500 = 'App_Combustivel.views.error_500_view'
handler403 = 'App_Combustivel.views.error_403_view'
handler400 = 'App_Combustivel.views.error_400_view'