from django.shortcuts import render, redirect, get_object_or_404
from .models import Usuario, Veiculo, Abastecimento
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Sum
from .forms import RegistroForm, FiltroDataForm
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
        return HttpResponseForbidden("Você não tem permissão para acessar esta página. ")

    if request.method == "POST":
        nome = request.POST.get('nome').upper()
        placa = request.POST.get("placa").upper()

        # Verificando se o veículo já existe no banco de dados: 
        if Veiculo.objects.filter(nome=nome).exists():
            return HttpResponse("Veículo já cadastrado! <br> <a href="">Voltar</a>")
        
        elif Veiculo.objects.filter(placa=placa).exists():
            return HttpResponse("Veículo já cadastrado! <br> <a href="">Voltar</a>")

        if not nome or not placa:
            return render(request, "veiculos/cadastrar_veiculo.html", {
                "error": "Nome e placa são obrigatórios."
            })

        try:
            veiculo = Veiculo.objects.get(nome=nome, placa=placa)
            # Se o veículo já existe, redireciona para o formulário de abastecimento
            return render(request, "veiculos/form_abastecimento.html", {"veiculo": veiculo})
        except Veiculo.DoesNotExist:
            if "media_prevista" in request.POST:
                media_prevista = request.POST.get("media_prevista")
                Veiculo.objects.create(
                    nome=nome,
                    placa=placa,
                    media_prevista=media_prevista
                )
                return HttpResponse("Veículo cadastrado com sucesso! Agora insira os dados de abastecimento.")
            else:
                return render(request, "veiculos/cadastrar_veiculo.html", {
                    "error": "Veículo não encontrado. Por favor, preencha todos os campos."
                })

    return render(request, "veiculos/cadastrar_veiculo.html")


@login_required(login_url='login')
def cadastrar_abastecimento(request, veiculo_id):
    # Verifica se o veículo existe
    veiculo = get_object_or_404(Veiculo, id=veiculo_id)
    
    if request.method == "POST":
        # Obtendo dados do formulário
        data = request.POST.get("data")
        litros = request.POST.get("litros")
        quilometragem_atual = request.POST.get("quilometragem")

        # Tenta pegar o último abastecimento para calcular o consumo
        ultimo_abastecimento = Abastecimento.objects.filter(veiculo=veiculo).last()

        # Se houver um abastecimento anterior, calcula o consumo
        if ultimo_abastecimento:
            km_anterior = ultimo_abastecimento.quilometragem
            km_percorridos = float(quilometragem_atual) - float(km_anterior)

            # Calcula o consumo com base no km percorrido e litros abastecidos no atual
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
                quilometragem=float(quilometragem_atual),
            )

            # Retorna o consumo calculado ao usuário
            return render(request, "veiculos/resultado.html", {
                "message": f"Abastecimento registrado! O consumo do último abastecimento foi de {consumo:.2f} km/l."
            })

        # Se for o primeiro abastecimento, não calcula consumo
        else:
            Abastecimento.objects.create(
                veiculo=veiculo,
                data=datetime.strptime(data, "%Y-%m-%d"),
                litros=float(litros),
                quilometragem=float(quilometragem_atual),
            )

            return render(request, "veiculos/resultado.html", {
                "message": "Primeiro abastecimento registrado! O consumo será calculado no próximo registro."
            })

    return render(request, 'veiculos/form_abastecimento.html', {'veiculo': veiculo})
    

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
    messages.success(request, f"Veículo {veiculo.nome} removido com sucesso!")
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
        alerta_mensagem = (f'O veículo {veiculo.nome} de placa {veiculo.placa} teve um consumo abaixo do esperado. \n'
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
        