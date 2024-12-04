from django.db import models


# Definindo as opções de tipos de contratos imobiliários
TIPO_CONTRATO_CHOICES = [
    ('compra_venda', 'Contrato de Compra e Venda'),
    ('promessa_compra_venda', 'Contrato de Promessa de Compra e Venda'),
    ('locacao', 'Contrato de Locação (Aluguel)'),
    ('permuta', 'Contrato de Permuta'),
    ('financiamento', 'Contrato de Financiamento Imobiliário'),
    ('corretagem', 'Contrato de Corretagem Imobiliária'),
    ('comodato', 'Contrato de Comodato'),
    ('arrendamento_rural', 'Contrato de Arrendamento Rural'),
    ('built_to_suit', 'Contrato Built to Suit'),
    ('incorporacao', 'Contrato de Incorporação Imobiliária'),
    ('doacao', 'Contrato de Doação'),
    ('cessao_direitos', 'Contrato de Cessão de Direitos'),
]

# Garantias para Contratos de Aluguel
TIPO_GARANTIA_ALUGUEL_CHOICES = [
    ('caucao', 'Caução'),
    ('fiador', 'Fiador'),
    ('seguro_fianca', 'Seguro Fiança'),
    ('titulo_capitalizacao', 'Título de Capitalização'),
    ('carta_fiança', 'Carta Fiança'),
]

# Garantias para Contratos de Compra e Venda
TIPO_GARANTIA_COMPRA_VENDA_CHOICES = [
    ('hipoteca', 'Hipoteca'),
    ('alienacao_fiduciaria', 'Alienação Fiduciária'),
    ('cessao_fiduciaria', 'Cessão Fiduciária de Quotas de Fundos de Investimento'),
    ('penhor', 'Penhor'),
    ('anticrese', 'Anticrese'),
]


