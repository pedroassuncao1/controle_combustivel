from django.shortcuts import render, redirect, get_object_or_404
from .models import Usuario, Veiculo, Abastecimento, ConsumoLubrificante, DossieManutencao
from django.template.loader import select_template
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Sum, Avg, Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from .forms import RegistroForm, FiltroDataForm, DossieForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from io import BytesIO
from django.urls import reverse_lazy 
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
import matplotlib.pyplot as plt 
import base64



# View para erros 404 (Página não encontrada)
def error_404_view(request, exception):
    return render(request, 'erros/404.html', status=404)

# View para erros 500 (Erro interno do servidor)
def error_500_view(request):
    return render(request, 'erros/500.html', status=500)

# View para erros 403 (Proibido)
def error_403_view(request, exception):
    return render(request, 'erros/403.html', status=403)

# View para erros 400 (Solicitação incorreta)
def error_400_view(request, exception):
    return render(request, 'erros/400.html', status=400)





@login_required(login_url='login')
def mais_opcoes(request):
    return render(request, 'usuarios/mais_opcoes.html')

@login_required(login_url='login')
def login_sucesso(request):

    if request.user.is_authenticated:
        print(f"Usuário logado: {request.user.usuario}")
    else:
        print("Usuário não está logado")

    if request.user.tipo_usuario == 'admin':
        # Rendereiza o home de admin :
        return render(request, 'usuarios/home_admin.html')
    elif request.user.tipo_usuario == 'frentista':
        # Renderiza o home de frentista : 
        return render(request, 'usuarios/home_frentista.html')
    else: 
        # Renderiza uma página de erro caso o usuário não seja nem frentista nem admin 
        return render(request, 'usuarios/home_sem_permissao.html')
    
    


def login_view(request):

    if request.user.is_authenticated:
       
        return redirect('home') 
        # Se o usuário já estiver logado e autenticado, ele não conseguirá retornar para a página de login

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                # Erro de autenticação
                return render(request, 'usuarios/login.html', {'form': form, 'error': 'Usuário ou senha incorretos'})
    else:
        form = AuthenticationForm()
    return render(request, 'usuarios/login.html', {'form': form})

@login_required(login_url='login')
def cadastrar_veiculo(request):
    # Verificando se o usuário é 'admin'
    if request.user.tipo_usuario != 'admin':
        return HttpResponseForbidden("Você não tem permissão para acessar esta página.")

    if request.method == "POST":

        print("Formulario recebido")

        print(request.POST)

        # Capturando os campos
        equipamento = request.POST.get('equipamento').upper()
        ativo = request.POST.get('ativo').upper()
        marca = request.POST.get('marca').upper()
        modelo = request.POST.get('modelo').upper()
        chassis = request.POST.get('chassis').upper()
        placa = request.POST.get('placa').upper()
        ano = request.POST.get('ano')
        obra = request.POST.get('obra').upper()
        media_prevista = float(request.POST['media_prevista'])

        # Capturando os campos de estimativa
        estimativa_troca_motor = request.POST.get("estimativa_troca_motor")
        estimativa_troca_transmissao = request.POST.get("estimativa_troca_transmissao")
        estimativa_troca_hidraulica = request.POST.get("estimativa_troca_hidraulica")
        estimativa_troca_dif_dianteiro = request.POST.get("estimativa_troca_dif_dianteiro")
        estimativa_troca_dif_traseiro = request.POST.get("estimativa_troca_dif_traseiro")
        estimativa_troca_direcao = request.POST.get("estimativa_troca_direcao")

        try:
            estimativa_troca_motor = int(request.POST.get("estimativa_troca_motor", 0))
            estimativa_troca_transmissao = int(request.POST.get("estimativa_troca_transmissao", 0))
            estimativa_troca_hidraulica = int(request.POST.get("estimativa_troca_hidraulica", 0))
            estimativa_troca_dif_dianteiro = int(request.POST.get("estimativa_troca_dif_dianteiro", 0))
            estimativa_troca_dif_traseiro = int(request.POST.get("estimativa_troca_dif_traseiro", 0))
            estimativa_troca_direcao = int(request.POST.get("estimativa_troca_direcao", 0))
        except ValueError:
            return render(request, "veiculos/cadastrar_veiculo.html", {
                "error": "Os campos de estimativa devem conter números válidos."
            })

        # Validando campos obrigatórios
        if not (equipamento and ativo and marca and modelo and chassis and ano and obra):
            return render(request, "veiculos/cadastrar_veiculo.html", {
                "error": "Todos os campos são obrigatórios."
            })

        if not all([
            estimativa_troca_motor, estimativa_troca_transmissao, estimativa_troca_hidraulica,
            estimativa_troca_dif_dianteiro, estimativa_troca_dif_traseiro, estimativa_troca_direcao
        ]):
            return render(request, "veiculos/cadastrar_veiculo.html", {
                "error": "Todos os campos de estimativa de troca de óleo são obrigatórios."
            })



        # Verificando duplicidade no banco de dados
        if Veiculo.objects.filter(ativo=ativo).exists():
            print("Veiculo com esse ativo ja cadastrado")
            return HttpResponse("Veículo com este ativo já cadastrado! <br> <a href=''>Voltar</a>")

        elif Veiculo.objects.filter(chassis=chassis).exists():
            print("Veiculo com este chassis ja cadastrado")
            return HttpResponse("Veículo com este chassis já cadastrado! <br> <a href=''>Voltar</a>")
        elif placa and Veiculo.objects.filter(placa=placa).exists():
            print("Veiculo com essa placa ja cadastrado")
            return HttpResponse("Veículo com esta placa já cadastrado! <br> <a href=''>Voltar</a>")

        # Criando o veículo no banco de dados
        Veiculo.objects.create(
            equipamento=equipamento,
            ativo=ativo,
            marca=marca,
            modelo=modelo,
            chassis=chassis,
            placa=placa,
            ano=ano,
            obra=obra,
            media_prevista=media_prevista,
            estimativa_troca_motor=estimativa_troca_motor,
            estimativa_troca_transmissao=estimativa_troca_transmissao,
            estimativa_troca_hidraulica=estimativa_troca_hidraulica,
            estimativa_troca_dif_dianteiro=estimativa_troca_dif_dianteiro,
            estimativa_troca_dif_traseiro=estimativa_troca_dif_traseiro,
            estimativa_troca_direcao=estimativa_troca_direcao,
        )
        print("Veículo cadastrado com sucesso!")
        return HttpResponse("Veículo cadastrado com sucesso! <br> <a href=''>Voltar</a>")


    return render(request, "veiculos/cadastrar_veiculo.html")




@login_required(login_url='login')
def cadastrar_abastecimento(request, veiculo_id):
    # Verifica se o veículo existe
    veiculo = get_object_or_404(Veiculo, id=veiculo_id)
    
    if request.method == "POST":
        # Obtendo dados do formulário
        data = request.POST.get("data")
        litros = request.POST.get("litros")
        quilometragem_atual = int(request.POST.get("quilometragem"))

        # Lógica de alerta para troca de óleo
        tipos_oleos = [
            ("Motor", veiculo.ultima_troca_motor, veiculo.estimativa_troca_motor),
            ("Transmissão", veiculo.ultima_troca_transmissao, veiculo.estimativa_troca_transmissao),
            ("Hidráulica", veiculo.ultima_troca_hidraulica, veiculo.estimativa_troca_hidraulica),
            ("Dif Dianteiro", veiculo.ultima_troca_dif_dianteiro, veiculo.estimativa_troca_dif_dianteiro),
            ("Dif Traseiro", veiculo.ultima_troca_dif_traseiro, veiculo.estimativa_troca_dif_traseiro),
            ("Direção", veiculo.ultima_troca_direcao, veiculo.estimativa_troca_direcao),
        ]

        # for tipo, ultima_troca, estimativa in tipos_oleos:

        #     if ultima_troca == 0: 
        #         # Ignorar se não houver registro da ultima troca de oleo 
        #         continue 

        #     limite_alerta = ultima_troca + estimativa - (estimativa * 0.1)  # 10% abaixo do limite
        #     if quilometragem_atual >= ultima_troca + estimativa:
        #         # Enviar alerta de risco
        #         enviar_email_alerta(veiculo, f"RISCO: Troca de óleo atrasada ({tipo})!", quilometragem_atual)
        #     elif quilometragem_atual >= limite_alerta:
        #         # Enviar alerta de proximidade
        #         enviar_email_alerta(veiculo, f"ALERTA: Próxima da troca de óleo ({tipo}).", quilometragem_atual)

        # Obtendo o último abastecimento para calcular o consumo
        ultimo_abastecimento = Abastecimento.objects.filter(veiculo=veiculo).last()

        if ultimo_abastecimento:
            km_anterior = ultimo_abastecimento.quilometragem
            km_percorridos = quilometragem_atual - km_anterior

            # Calcula o consumo
            consumo = km_percorridos / float(litros)

            # Atualiza o último abastecimento com o consumo calculado
            ultimo_abastecimento.consumo = consumo
            ultimo_abastecimento.save()

            verificar_consumo(veiculo, consumo, data)

            # Registra o novo abastecimento
            Abastecimento.objects.create(
                veiculo=veiculo,
                data=datetime.strptime(data, "%Y-%m-%d"),
                litros=float(litros),
                quilometragem=quilometragem_atual,
            )

            # Retorna o consumo calculado ao usuário
            return render(request, "veiculos/resultado.html", {
                "message": f"Abastecimento registrado! O consumo do último abastecimento foi de {consumo:.2f} km/l."
            })

        else:
            # Registra o primeiro abastecimento
            Abastecimento.objects.create(
                veiculo=veiculo,
                data=datetime.strptime(data, "%Y-%m-%d"),
                litros=float(litros),
                quilometragem=quilometragem_atual,
            )

            return render(request, "veiculos/resultado.html", {
                "message": "Primeiro abastecimento registrado! O consumo será calculado no próximo registro."
            })

    return render(request, 'veiculos/form_abastecimento.html', {'veiculo': veiculo})


# def enviar_email_alerta(veiculo, assunto, quilometragem_atual):
#     usuarios = Usuario.objects.all()
#     destinatarios = [usuario.email for usuario in usuarios]
    
#     # Verifique se há destinatários válidos
#     if not destinatarios or not isinstance(destinatarios, (list, tuple)):
#         raise ValueError("Nenhum destinatário válido foi fornecido para o alerta de e-mail.")

#     corpo = f"""
#     Alerta de manutenção para o veículo {veiculo.marca} {veiculo.modelo} - {veiculo.placa}.
#     Quilometragem atual: {quilometragem_atual}
#     """

#     send_mail(
#         subject=assunto,
#         message=corpo,
#         from_email=settings.EMAIL_HOST_USER,
#         recipient_list=destinatarios,
#     )

    

@login_required(login_url='login')    
def buscar_veiculo(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        placa = request.POST.get('placa')

        try: 
            veiculo = Veiculo.objects.get(nome=nome, placa=placa)
            # Se o veículo for encontrado, redireciona para a página de registro de abastecimento
            return HttpResponseRedirect(f'/cadastrar_abastecimento/{veiculo.id}')
        except Veiculo.DoesNotExist:
            # Caso o veículo não foi encontrado: 
            return render(request, 'veiculos/buscar_veiculo.html', {
                'error_message': 'Veículo não encontrado. Verifique os dados e tente novamente.'
            })
    
    return render(request, 'veiculos/buscar_veiculo.html')

@login_required(login_url='login')
def listar_veiculos(request):
    veiculos = Veiculo.objects.all()  # Obtém todos os veículos cadastrados
    return render(request, 'veiculos/listar_veiculos.html', {'veiculos': veiculos})


# Listar veículos com opção de remover
@login_required(login_url='login')
def remover_veiculo_view(request):

    # Verificando se o usuário é 'admin'
    if request.user.tipo_usuario != 'admin':
        return HttpResponseForbidden("Você não tem permissão para acessar esta página. ")
    
    

    veiculos = Veiculo.objects.all()  # Obtém todos os veículos cadastrados
    return render(request, 'veiculos/remover_veiculo.html', {'veiculos': veiculos})

# Remover veículo diretamente
@login_required(login_url='login')
def remover_veiculo(request, veiculo_id):

    veiculo = get_object_or_404(Veiculo, id=veiculo_id)
    veiculo.delete()
    messages.success(request, f"Veículo {veiculo.marca} {veiculo.modelo}  removido com sucesso!")
    return redirect('remover_veiculo_view')



@login_required(login_url='login')
def listar_veiculos_para_informacoes(request): 
    veiculos = Veiculo.objects.all() 
    return render(request, 'veiculos/listar_veiculos_informacoes.html', {'veiculos': veiculos})


# View para exibir as informações detalhadas de um veículo: 
@login_required(login_url='login')
def exibir_informacoes_veiculo(request, veiculo_id):
    veiculo = get_object_or_404(Veiculo, id=veiculo_id)
    abastecimentos = Abastecimento.objects.filter(veiculo=veiculo).order_by('-data')  # Ordena por data, mais recente primeiro
    
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')

    # Se as datas forem fornecidas, aplica o filtro
    if data_inicio and data_fim:
        try: 
            # Converter as strings de data para objetos em datetime
            data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
            data_fim = datetime.strptime(data_fim, '%Y-%m-%d').date()

            # Filtrar os abastecimentos pela data
            abastecimentos = abastecimentos.filter(data__range=[data_inicio, data_fim])
        except ValueError:
            pass # Se a data estiver inválida, ignora o filtro 


    return render(request, 'veiculos/exibir_informacoes.html', {
        'veiculo': veiculo,
        'abastecimentos': abastecimentos,
        'data_inicio': data_inicio,
        'data_fim': data_fim
    })



# Funnção para enviar email com alerta: 

def emitir_alerta(alerta_mensagem):
    # Obter todos os e-mails dos usuários cadastrados
    usuarios = Usuario.objects.all()
    lista_emails = [usuario.email for usuario in usuarios]

    # Assunto e mensagem do alerta
    assunto = 'Alerta de Consumo de Combustível'
    mensagem = ('Um novo alerta foi emitido: \n '
    f'{alerta_mensagem}')

    # Configurar o e-mail remetente
    remetente = settings.EMAIL_HOST_USER
    

    # Enviar o e-mail para todos os usuários
    try:
        send_mail(
            assunto, 
            mensagem, 
            remetente, 
            lista_emails, 
            fail_silently=False,
        )
        print("E-mails de alerta enviados com sucesso!")
        
    except Exception as e:
        print(f"Erro ao enviar e-mails: {e}")


# Função para verificar o consumo e emitir alerta, se necessário: 

def verificar_consumo(veiculo, consumo, data):
    media_prevista = veiculo.media_prevista # Media prevista registrada no veículo 
    limite_aceitavel = media_prevista * 0.90 # 10% abaixo do consumo esperado 

    if consumo < limite_aceitavel:
        alerta_mensagem = (f'O veículo {veiculo.marca} {veiculo.modelo} de placa {veiculo.placa} teve um consumo abaixo do esperado. \n'
        f'Consumo esperado: {media_prevista} Km/L \n'
        f'Consumo real: {consumo} Km/L \n '
        f'Data do abastecimento: {data} \n'
        )
        emitir_alerta(alerta_mensagem)
        return True # Indica que foi emitido alerta
    return False


@login_required(login_url='login')
def grafico_consumo(request):

     # Verificando se o usuário é 'admin'
    if request.user.tipo_usuario != 'admin':
        return HttpResponseForbidden("Você não tem permissão para acessar esta página. ")
    

    # Inicializar o formulário para filtro de data
    form = FiltroDataForm(request.GET or None)

    # Filtrar por data se o formulário estiver preenchido
    data_inicio = form.cleaned_data.get('data_inicio') if form.is_valid() else None
    data_fim = form.cleaned_data.get('data_fim') if form.is_valid() else None

    # Consultar todos os veículos
    veiculos = Veiculo.objects.all()
    consumo_veiculos = []

    # Gerar dados de consumo de combustível por veículo
    for veiculo in veiculos:
        # Filtrar abastecimentos por veículo e aplicar o filtro de data
        abastecimentos = Abastecimento.objects.filter(veiculo=veiculo)
        
        if data_inicio and data_fim:
            abastecimentos = abastecimentos.filter(data__range=[data_inicio, data_fim])
        
        # Somar o total de litros de combustível abastecido
        litros = abastecimentos.aggregate(litros=Sum('litros'))['litros'] or 0
        
        # Adicionar os dados de consumo na lista
        consumo_veiculos.append({
            'veiculo': veiculo,
            'litros': litros
        })

    # Criar o gráfico usando matplotlib
    veiculo_nomes = [consumo['veiculo'].nome for consumo in consumo_veiculos]
    combustivel_consumido = [consumo['litros'] for consumo in consumo_veiculos]

    # Configurar o gráfico
    fig, ax = plt.subplots()
    ax.bar(veiculo_nomes, combustivel_consumido, color='skyblue')
    ax.set_xlabel('Veículos')
    ax.set_ylabel(f'Combustível Consumido (litros)')
    ax.set_title('Consumo de Combustível por Veículo')

    # Converter o gráfico para imagem base64
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    imagem_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()

    # Passar os dados para o template
    context = {
        'consumo_veiculos': consumo_veiculos,
        'imagem_grafico': imagem_base64,
        'form': form  # Formulário para o filtro de data
    }

    print(combustivel_consumido)

    return render(request, 'veiculos/grafico_consumo.html', context)

@login_required(login_url='login')
def cadastrar_usuario(request):
    # Verificando se o usuário é 'admin'
    if request.user.tipo_usuario != 'admin':
        return HttpResponseForbidden("Você não tem permissão para acessar esta página. ")
    
    form = RegistroForm()

    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário cadastrado com sucesso! ')
            print('Usuário cadastrado')

        else: 
            print(f'Usuário não cadastrado')
    return render(request, 'usuarios/cadastrar_usuario.html', {'form': form})


# TROCAR SENHA, NÃO MEXER. 
class TrocarSenhaView(PasswordChangeView):
    template_name = 'usuarios/trocar_senha.html'
    success_url = reverse_lazy('senha_trocada_com_sucesso')

class SenhaTrocadaComSucessoView(PasswordChangeDoneView):
    template_name = 'usuarios/senha_trocada_com_sucesso.html'


@login_required(login_url='login')
def apagar_usuario(request):
    if request.user.tipo_usuario == 'admin':  # Verifica se o usuário é admin
        if request.method == 'POST':
            # Pegando o campo 'usuario' ao invés de 'username'
            usuario = request.POST.get('usuario')
            user = get_object_or_404(Usuario, usuario=usuario)
            
            if user != request.user:  # Impede que o admin apague a si mesmo
                user.delete()
                messages.success(request, f'O usuário {usuario} foi apagado com sucesso.')
            else:
                messages.error(request, 'Você não pode apagar a si mesmo.')

            
        
        # Retorna a lista de usuários para exibir no template
        usuarios = Usuario.objects.exclude(usuario=request.user.usuario)
        return render(request, 'usuarios/apagar_usuario.html', {'usuarios': usuarios})
    else:
        messages.error(request, 'Você não tem permissão para apagar usuários.')
        

@login_required(login_url='login')
def detalhes_veiculo(request, veiculo_id):
    veiculo = get_object_or_404(Veiculo, id=veiculo_id)

    # Consumo de combustível
    consumo_combustivel = Abastecimento.objects.filter(veiculo=veiculo).aggregate(total_consumo=Sum('litros'))['total_consumo'] or 0

    # Consumo de lubrificantes por tipo
    tipos_lubrificantes = ["Motor", "Transmissão", "Hidráulica", "Dif Dianteiro", "Dif Traseiro", "Direção"]
    consumo_lubrificantes = {
        tipo: ConsumoLubrificante.objects.filter(veiculo=veiculo, tipo=tipo).aggregate(total_consumo=Sum('quantidade'))['total_consumo'] or 0
        for tipo in tipos_lubrificantes
    }
    
    # Obter último abastecimento
    ultimo_abastecimento = Abastecimento.objects.filter(veiculo=veiculo).order_by('-data').first()
    km_atual = ultimo_abastecimento.quilometragem if ultimo_abastecimento else None

    # Dados de trocas
    trocas = {
        'motor': {
            'ultima_troca': veiculo.ultima_troca_motor,
            'estimativa': veiculo.estimativa_troca_motor,
            'status': get_status(km_atual, veiculo.ultima_troca_motor, veiculo.estimativa_troca_motor),
        },
        'transmissao': {
            'ultima_troca': veiculo.ultima_troca_transmissao,
            'estimativa': veiculo.estimativa_troca_transmissao,
            'status': get_status(km_atual, veiculo.ultima_troca_transmissao, veiculo.estimativa_troca_transmissao),
        },
        'hidraulica': {
            'ultima_troca': veiculo.ultima_troca_hidraulica,
            'estimativa': veiculo.estimativa_troca_hidraulica,
            'status': get_status(km_atual, veiculo.ultima_troca_hidraulica, veiculo.estimativa_troca_hidraulica),
        },
        'dif_dianteiro': {
            'ultima_troca': veiculo.ultima_troca_dif_dianteiro,
            'estimativa': veiculo.estimativa_troca_dif_dianteiro,
            'status': get_status(km_atual, veiculo.ultima_troca_dif_dianteiro, veiculo.estimativa_troca_dif_dianteiro),
        },
        'dif_traseiro': {
            'ultima_troca': veiculo.ultima_troca_dif_traseiro,
            'estimativa': veiculo.estimativa_troca_dif_traseiro,
            'status': get_status(km_atual, veiculo.ultima_troca_dif_traseiro, veiculo.estimativa_troca_dif_traseiro),
        },
        'direcao': {
            'ultima_troca': veiculo.ultima_troca_direcao,
            'estimativa': veiculo.estimativa_troca_direcao,
            'status': get_status(km_atual, veiculo.ultima_troca_direcao, veiculo.estimativa_troca_direcao),
        },
    }


        # Adicione outros tipos conforme necessário...


    # Histórico de consumo
    historico = ConsumoLubrificante.objects.filter(veiculo=veiculo).order_by('-data')

    context = {
        'veiculo': veiculo,
        'km_atual': km_atual,
        'trocas': trocas,
        'historico': historico,
        'consumo_combustivel': consumo_combustivel,
        'consumo_lubrificantes': consumo_lubrificantes,
    }
    return render(request, 'veiculos/detalhes_veiculos.html', context)

def get_status(km_atual, ultima_troca, estimativa):
    if ultima_troca == 0:
        return 'ok'  # Verde, pois ainda não houve troca
    if km_atual is None:
        return 'indefinido'  # Sem dados para calcular
    if km_atual >= ultima_troca + estimativa:
        return 'atrasado'  # Vermelho
    if km_atual >= (ultima_troca + (estimativa * 0.1)):  # Margem de 500 km
        return 'na_hora'  # Amarelo
    
    return 'ok'  # Verde



from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Veiculo, ConsumoLubrificante  # Certifique-se de que os modelos estão importados corretamente

@login_required(login_url='login')
def troca_oleo(request):
    veiculos = Veiculo.objects.all()

    if request.method == 'POST': 
        veiculo_id = request.POST.get('veiculo')
        data = request.POST.get('data')
        tipo = request.POST.get('tipo')
        tipo_oleo = request.POST.get('tipo_oleo')  # Captura o tipo de óleo
        quantidade = request.POST.get('quantidade')
        km_atual = request.POST.get('km_atual')  # Captura o km atual do formulário

        try: 
            veiculo = get_object_or_404(Veiculo, id=veiculo_id)
            quantidade = float(quantidade)
            km_atual = int(km_atual)

            # Atualiza o km_atual do veículo
            veiculo.km_atual = km_atual

            # Salva a troca de óleo 
            ConsumoLubrificante.objects.create(
                veiculo=veiculo,
                data=data,
                tipo=tipo,
                tipo_oleo=tipo_oleo,  # Salva o tipo de óleo
                quantidade=quantidade,
                quilometragem=km_atual,
            )

            # Atualiza o campo ultima_troca_motor no veículo
            if tipo == 'Motor':  # Certifique-se de que o valor corresponde exatamente
                veiculo.ultima_troca_motor = km_atual
                veiculo.save()  # Salva as alterações no banco de dados

            messages.success(request, "Troca de óleo registrada com sucesso!")
            print("Troca de óleo registrada com sucesso!")
            return redirect('troca_oleo')
        
        except ValueError:
            messages.error(request, "Quantidade ou quilometragem inválida!")
        except Exception as e:
            messages.error(request, f"Ocorreu um erro: {e}")
            print(f'Erro: {e}')

    context = {
        'veiculos': veiculos,
    }

    return render(request, 'veiculos/troca_oleo.html', context)





from django.db.models import Q

@login_required(login_url='login')
def detalhes_consumo(request, veiculo_id, tipo=None):
    veiculo = get_object_or_404(Veiculo, id=veiculo_id)

    # Recuperar os filtros de data
    data_inicial = request.GET.get('data_inicial')
    data_final = request.GET.get('data_final')

    if tipo == "combustivel":
        # Consumo de combustível
        abastecimentos = Abastecimento.objects.filter(veiculo=veiculo)

        # Aplicar filtro de datas se as datas forem fornecidas
        if data_inicial and data_final:
            abastecimentos = abastecimentos.filter(
                Q(data__gte=data_inicial) & Q(data__lte=data_final)
            )

        # Criar lista de registros para exibição
        registros = []
        for abastecimento in abastecimentos:
            if abastecimento.litros > 0:
                consumo = abastecimento.consumo
            registros.append({
                'data': abastecimento.data,
                'litros': abastecimento.litros,
                'quilometragem': abastecimento.quilometragem,
                'consumo': consumo
            })

        context = {
            'veiculo': veiculo,
            'registros': registros,
            'tipo': 'combustivel',
        }

    elif tipo in ["Motor", "Transmissão", "Hidráulica", "Dif Dianteiro", "Dif Traseiro", "Direção"]:
        # Consumo de lubrificante por tipo
        registros = ConsumoLubrificante.objects.filter(veiculo=veiculo, tipo=tipo)

        # Aplicar filtro de datas se as datas forem fornecidas
        if data_inicial and data_final:
            registros = registros.filter(
                Q(data__gte=data_inicial) & Q(data__lte=data_final)
            )

        registros_formatados = [
            {
                'data': registro.data,
                'quantidade': registro.quantidade,
                'quilometragem': registro.quilometragem,
                'tipo_oleo': registro.tipo_oleo,
            }
            for registro in registros
        ]

        context = {
            'veiculo': veiculo,
            'registros': registros_formatados,
            'tipo': tipo,
        }

    else:
        # Caso o tipo seja inválido
        return HttpResponse("Tipo de consumo inválido", status=400)

    return render(request, 'veiculos/detalhes_consumo.html', context)

@login_required(login_url='login')
def dossie_veiculo(request, veiculo_id):
    veiculo = get_object_or_404(Veiculo, id=veiculo_id)
    dossies = veiculo.dossies.all() 
    return render(request, 'veiculos/dossie_veiculo.html', {
        'veiculo': veiculo,
        'dossies': dossies,
    })

@login_required(login_url='login')
def cadastrar_dossie(request, veiculo_id):
    veiculo = get_object_or_404(Veiculo, id=veiculo_id)
    if request.method == 'POST':
        form = DossieForm(request.POST)
        if form.is_valid():
            dossie = form.save(commit=False)
            dossie.veiculo = veiculo
            dossie.save()
            return redirect('dossie_veiculo', veiculo_id=veiculo.id)
    else:
        form = DossieForm()

    return render(request, 'veiculos/cadastrar_dossie.html', {
        'veiculo': veiculo,
        'form': form,
    })

@login_required(login_url='login')
def relatorio_trocas_oleo(request):
    veiculos = Veiculo.objects.all()
    relatorios = []

    for veiculo in veiculos:
        relatorios.append({
            'veiculo': veiculo,
            'motor': {
                'ultima_troca': veiculo.ultima_troca_motor,
                'estimativa': veiculo.estimativa_troca_motor,
            },
            'transmissao': {
                'ultima_troca': veiculo.ultima_troca_transmissao,
                'estimativa': veiculo.estimativa_troca_transmissao,
            },
            'hidraulica': {
                'ultima_troca': veiculo.ultima_troca_hidraulica,
                'estimativa': veiculo.estimativa_troca_hidraulica,
            },
            'historico': ConsumoLubrificante.objects.filter(veiculo=veiculo).order_by('-data'),
        })

    return render(request, 'veiculos/relatorio_trocas_oleo.html', {'relatorios': relatorios})


@login_required(login_url='login')
def editar_obra(request, veiculo_id):
    veiculo = get_object_or_404(Veiculo, id=veiculo_id)

    if request.method == 'POST':
        nova_obra = request.POST.get('nova_obra')
        veiculo.obra = nova_obra.upper()
        veiculo.save()
        messages.success(request, "Obra atualizada com sucesso!")
        return redirect('listar_veiculos_informacoes')  # Redirecione para a lista de veículos ou outra página apropriada

    context = {
        'veiculo': veiculo,
    }
    return render(request, 'veiculos/editar_obra.html', context)