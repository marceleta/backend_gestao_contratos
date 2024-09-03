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
    imovel = models.ForeignKey('imovel.Imovel', on_delete=models.CASCADE, related_name='documentos')
    tipo_documento = models.CharField(max_length=50, choices=[('matricula', 'Matrícula'), 
                                                              ('cert_negativa_iptu', 'Certidão Negativa IPTU'),
                                                              ('cert_negativa_condominio', 'Certidão Negativa Condomínio'),
                                                              ('cert_negativa_deb_trabalhistas', 'Certidão Negativa Débitos Trabalhistas'),
                                                              ('recibo_itbi', 'Recibo ITBI'),
                                                              ('habitese', 'Habite-se'),
                                                              ('escritura_publica', 'Escritura Pública')])

    def __str__(self):
        return f"{self.tipo_documento} - {self.imovel.descricao}"

