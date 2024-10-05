from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _ 



class CustomMinimumLengthValidator: 
    def __init__(self, min_length=6):
        self.min_length = min_length

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                _(f'Senha muito curta. Mínimo de caracteres: {self.min_length}.'),
                code='password_too_short',
            )
        
    def get_help_text(self):
        return _(f'Sua senha dever ter pelo menos {self.min_length} caracteres. ')