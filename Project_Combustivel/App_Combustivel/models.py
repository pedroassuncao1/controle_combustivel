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
    nome = models.CharField(max_length=100)
    placa = models.CharField(max_length=10, unique=True)
    media_prevista = models.FloatField()
    

    def __str__(self):
        return f"{self.nome} - {self.placa}"
    

class Abastecimento(models.Model):
    veiculo = models.ForeignKey(Veiculo, on_delete=models.CASCADE)
    data = models.DateField()
    litros = models.FloatField()
    quilometragem = models.FloatField()
    consumo = models.FloatField(null=True, blank=True) # Consumo será calculado posteriormente