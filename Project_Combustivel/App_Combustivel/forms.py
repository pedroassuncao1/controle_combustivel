from django import forms
from .models import Abastecimento 
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Usuario
from django.core.exceptions import ValidationError


class AbastecimentoForm(forms.ModelForm):
    class Meta:
        model = Abastecimento
        fields = ['data', 'litros', 'litros', ]  # Inclua todos os campos que deseja no formulário
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),  # Um widget para o campo data, criando um seletor de data
        }

    def clean_litros(self):
        litros = self.cleaned_data.get('litros')
        if litros <= 0:
            raise forms.ValidationError("A quantidade de litros deve ser maior que zero.")
        return litros

    def clean_litros(self):
        litros = self.cleaned_data.get('litros')
        if litros <= 0:
            raise forms.ValidationError("A quantidade abastecida deve ser maior que zero.")
        return litros
    
class RegistroForm(UserCreationForm): 
    class Meta: 
        model = Usuario 
        fields = ['usuario', 'email', 'tipo_usuario', 'password1', 'password2'] 

        labels = {
            'username': 'Nome de Usuário',
            'email': 'E-mail',
            'tipo_usuario' : 'Tipo de Usuário',
            'password1': 'Senha',
            'passowrd2': 'Confirme sua senha'
        }

        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'tipo_usuario': forms.Select(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }


    def clean_username(self):
        username = self.cleaned_data.get('username')
        if Usuario.objects.filter(username=username).exists():
            raise ValidationError('Este usuário já está sendo utilizado')
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exists():
            raise ValidationError('Este email já está sendo utilizado')
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        tipo_usuario = cleaned_data.get('tipo_usuario')

        # Verificando se as senhas conhecidem
        if password1 and password2 and password1 != password2:
            self.add_error('password2', "As senhas não conhecidem")

        # Verificando se o tipo de usuario não foi selecionado
        if not tipo_usuario:
            self.add_error('tipo_usuario', "Selecione o tipo de usuário")


    def save(self, commit=True): 
        usuario = super(RegistroForm, self).save(commit=False)
        usuario.set_password(self.cleaned_data['password1']) 
        if commit: 
            usuario.save()
        return usuario
    




class FiltroDataForm(forms.Form): 
    data_inicio = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label="Data Início")
    data_fim = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label="Data Fim")


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label='Usuário')
    password = forms.CharField(label='Senha', widget=forms.PasswordInput)