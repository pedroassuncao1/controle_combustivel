from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class UsuarioManager(BaseUserManager):
    def create_user(self, usuario, email, senha=None, **extra_fields):
        if not email:
            raise ValueError('O endereço de email deve ser fornecido')
        email = self.normalize_email(email)
        user = self.model(usuario=usuario, email=email, **extra_fields)
        user.set_password(senha)  # Importante: isso salva a senha como hash!
        user.save(using=self._db)
        return user

    def create_superuser(self, usuario, email, senha=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser deve ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser deve ter is_superuser=True.')

        return self.create_user(usuario, email, senha, **extra_fields)


class Usuario(AbstractBaseUser):

    TIPO_USUARIO_CHOICES = [
        ('admin', 'Admin'),
        ('frentista', 'Frentista')
    ]

    email = models.EmailField(unique=True) # campo de email do usuario
    id_usuario = models.AutoField(primary_key=True) # campo de id do usuario
    usuario = models.TextField(max_length=255, unique=True) # campo de nome do usuario
    senha = models.TextField(max_length=255) # campo de senha do usuario
    tipo_usuario = models.CharField(max_length=10, choices=TIPO_USUARIO_CHOICES) # Tipo de usuário 

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = 'usuario'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.usuario


class Veiculo(models.Model):
    equipamento = models.CharField(max_length=100, verbose_name="Equipamento")
    ativo = models.CharField(max_length=50, unique=True, verbose_name="Ativo")
    marca = models.CharField(max_length=50, verbose_name="Marca")
    modelo = models.CharField(max_length=50, verbose_name="Modelo")
    chassis = models.CharField(max_length=50, unique=True, verbose_name="Chassis")
    placa = models.CharField(max_length=20, unique=True, blank=True, null=True, verbose_name="Placa")
    ano = models.PositiveIntegerField(verbose_name="Ano")
    obra = models.CharField(max_length=100, verbose_name="Obra")
    media_prevista = models.FloatField()


    # Campos para salvar a última troca e estimativa de troca de óleo para cada tipo de óleo(Motor, Hidraulica, Diferencial...)

    ultima_troca_motor = models.IntegerField(default=0)
    estimativa_troca_motor = models.IntegerField(null=False, blank=False)

    ultima_troca_transmissao = models.IntegerField(default=0)
    estimativa_troca_transmissao = models.IntegerField(null=False, blank=False)

    ultima_troca_hidraulica = models.IntegerField(default=0)
    estimativa_troca_hidraulica = models.IntegerField(null=False, blank=False)

    ultima_troca_dif_dianteiro = models.IntegerField(default=0)
    estimativa_troca_dif_dianteiro = models.IntegerField(null=False, blank=False)

    ultima_troca_dif_traseiro = models.IntegerField(default=0)
    estimativa_troca_dif_traseiro = models.IntegerField(null=False, blank=False)

    ultima_troca_direcao = models.IntegerField(default=0)
    estimativa_troca_direcao = models.IntegerField(null=False, blank=False)


    # RETIRAR O DEFAULT E EXIGIR QUE A ESTIMATIVA DE OLEO SEJA INSERIDA NO CADASTRAMENTO DO VEÍCULO 



    def __str__(self):
        return f"{self.equipamento} - {self.ativo}"

    

class Abastecimento(models.Model):
    veiculo = models.ForeignKey(Veiculo, on_delete=models.CASCADE)
    data = models.DateField()
    litros = models.FloatField()
    quilometragem = models.FloatField()
    consumo = models.FloatField(null=True, blank=True) # Consumo será calculado posteriormente

class ConsumoLubrificante(models.Model):
    veiculo = models.ForeignKey(Veiculo, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=50)  # Ex: Motor, Transmissão
    tipo_oleo = models.CharField(max_length=50)  # Ex: 15w40, 5w30
    quantidade = models.FloatField()
    data = models.DateField()
    quilometragem = models.FloatField()



class DossieManutencao(models.Model):
    veiculo = models.ForeignKey('Veiculo', on_delete=models.CASCADE, related_name="dossies")
    data_parada = models.DateField()
    data_liberacao = models.DateField(null=True, blank=True)
    horimetro_acumulado = models.IntegerField()
    defeito_apresentado = models.CharField(max_length=255)
    causa_falha = models.TextField()
    servico_executado = models.TextField()
    numero_nota_fiscal = models.CharField(max_length=255, null=True, blank=True)
    numero_osi = models.CharField(max_length=255)
    executado_por = models.CharField(max_length=255)

    def __str__(self):
        return f"Dossiê de {self.veiculo} - OSI {self.numero_osi}"