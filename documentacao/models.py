from django.db import models

class Documento(models.Model):
    descricao = models.CharField(max_length=255)
    arquivo = models.FileField(upload_to='documentos/')
    data_emissao = models.DateField()

    class Meta:
        abstract = True
        

class DocumentoPessoaFisica(Documento):
    pessoa_fisica = models.ForeignKey('core.PessoaFisica', on_delete=models.CASCADE, related_name='documentos')
    tipo_documento = models.CharField(max_length=50, choices=[('CPF', 'CPF'), ('RG', 'RG'), ('CNH', 'CNH'), 
                                                              ('certidao_nascimento', 'Certidão Nascimento'), 
                                                              ('certidao_casamento', 'Certidão Casamento'),
                                                              ('comprovante_renda', 'Comprovante Renda'),
                                                              ('imposto_renda', 'Declaração Imposto de Renda'),
                                                              ('comprovante_residencia', 'Comprovante de Residência')])

    def __str__(self):
        return f"{self.tipo_documento} - {self.pessoa_fisica.nome}"
    

class DocumentoPessoaJuridica(Documento):
    pessoa_juridica = models.ForeignKey('core.PessoaJuridica', on_delete=models.CASCADE, related_name='documentos')
    tipo_documento = models.CharField(max_length=50, choices=[('CNPJ', 'CNPJ'), 
                                                              ('contrato_social', 'Contrato Social'),
                                                              ('cert_negativa_deb_tributarios', 'Certidão Negativa de Débitos Tributários'),
                                                              ('cert_regul_fgts', 'Certidão Regularidade FGTS')])

    def __str__(self):
        return f"{self.tipo_documento} - {self.pessoa_juridica.nome}"


class DocumentoImovel(Documento):
    TIPO_DOCUMENTO_CHOICES = [
        ('escritura', 'Escritura Pública'),
        ('matricula', 'Certidão de Matrícula'),
        ('cnd', 'Certidão Negativa de Débitos'),
        ('iptu', 'Certidão Negativa de IPTU'),
        ('condominio', 'Certidão Negativa de Débitos Condominiais'),
        ('onus_reais', 'Certidão de Ônus Reais'),
        ('habitese', 'Habite-se'),
        ('licenca_construcao', 'Licença de Construção'),
        ('licenca_ambiental', 'Licença Ambiental'),
        ('alvara_funcionamento', 'Alvará de Funcionamento'),
    ]
    imovel = models.ForeignKey('imovel.Imovel', on_delete=models.CASCADE, related_name='documentos')
    tipo_documento = models.CharField(max_length=50, choices=TIPO_DOCUMENTO_CHOICES)

    def __str__(self):
        return f"{self.get_tipo_documento_display()} - {self.imovel.nome}"
    

class FotosVideoImovel(Documento):
    TIPO_FOTOVIDEO_CHOICES = [
        ('foto_profissional', 'Foto Profissional'),
        ('foto_drone', 'Foto Aérea com Drone'),
        ('foto_360', 'Imagem 360º'),
        ('planta_baixa', 'Imagem de Planta Baixa'),
        ('foto_ambientada', 'Foto Ambientada'),
        ('video_tour', 'Vídeo Tour'),
        ('tour_virtual_360', 'Tour Virtual 360º'),
        ('video_drone', 'Vídeo com Drone'),
        ('video_obra', 'Vídeo de Andamento de Obras'),
        ('depoimento_cliente', 'Depoimento de Cliente'),
    ]

    imovel = models.ForeignKey('imovel.Imovel', on_delete=models.CASCADE, related_name='midia')
    tipo_midia = models.CharField(max_length=50, choices=TIPO_FOTOVIDEO_CHOICES)
    FORMATO_CHOICES = [
        ('imagem', 'Imagem'),
        ('video', 'Vídeo'),
    ]
    formato = models.CharField(max_length=10, choices=FORMATO_CHOICES, default='Imagem')


    def __str__(self):
        return f"{self.get_tipo_midia_display()} - {self.imovel.nome}"

