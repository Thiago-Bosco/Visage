from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, TextAreaField, BooleanField, SelectField, PasswordField
from wtforms.validators import DataRequired, NumberRange, Length, Optional

class CheckoutForm(FlaskForm):
    customer_name = StringField('Nome Completo', validators=[
        DataRequired(message='Nome é obrigatório'),
        Length(min=2, max=100, message='Nome deve ter entre 2 e 100 caracteres')
    ])
    customer_phone = StringField('Telefone (opcional)', validators=[
        Optional(),
        Length(max=20, message='Telefone deve ter no máximo 20 caracteres')
    ])

class ProductForm(FlaskForm):
    name = StringField('Nome do Produto', validators=[
        DataRequired(message='Nome é obrigatório'),
        Length(min=2, max=100, message='Nome deve ter entre 2 e 100 caracteres')
    ])
    description = TextAreaField('Descrição', validators=[
        Optional(),
        Length(max=500, message='Descrição deve ter no máximo 500 caracteres')
    ])
    price = FloatField('Preço (R$)', validators=[
        DataRequired(message='Preço é obrigatório'),
        NumberRange(min=0.01, message='Preço deve ser maior que zero')
    ])
    image_url = StringField('URL da Imagem', validators=[
        Optional(),
        Length(max=255, message='URL deve ter no máximo 255 caracteres')
    ])
    category = SelectField('Categoria', choices=[
        ('Pomadas', 'Pomadas'),
        ('Óleos', 'Óleos'),
        ('Shampoos', 'Shampoos'),
        ('Ceras', 'Ceras'),
        ('Pós-Barba', 'Pós-Barba'),
        ('Kits', 'Kits'),
        ('Outros', 'Outros')
    ], validators=[Optional()])
    in_stock = BooleanField('Em Estoque', default=True)

class AddToCartForm(FlaskForm):
    quantity = IntegerField('Quantidade', validators=[
        DataRequired(message='Quantidade é obrigatória'),
        NumberRange(min=1, max=99, message='Quantidade deve ser entre 1 e 99')
    ], default=1)

class AdminLoginForm(FlaskForm):
    username = StringField('Usuário', validators=[
        DataRequired(message='Usuário é obrigatório'),
        Length(min=3, max=50, message='Usuário deve ter entre 3 e 50 caracteres')
    ])
    password = PasswordField('Senha', validators=[
        DataRequired(message='Senha é obrigatória'),
        Length(min=4, max=100, message='Senha deve ter entre 4 e 100 caracteres')
    ])
