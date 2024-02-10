from odoo import models, fields, api


class Email(models.Model):
    _name = 'ta.email'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'E-mail Entrant'

    subject = fields.Char(string='Sujet')
    body_html = fields.Html(string='Corps HTML')
    email_from = fields.Char(string='De')
    email_to = fields.Char(string='À')
    received_date = fields.Date(string='Date de Réception')
    numero_dum_extracted = fields.Char(string="Numéro DUM Extrait")
    dossier_id = fields.Many2one('ta.dossier', string='Dossier')

    @api.model
    def create_from_message(self, record):
        # Récupération des informations de base de l'email
        email_from = record.email_from
        email_to = record.email_to
        subject = record.subject
        body = record.body
        date = record.date

        # Création d'un enregistrement dans le modèle ta.email sans définir 'numero_dum_extracted' et 'dossier_id'
        return self.create({
            'email_from': email_from,
            'email_to': email_to,
            'subject': subject,
            'body_html': body,
            'received_date': date,
            # 'numero_dum_extracted' et 'dossier_id' seront gérés plus tard
        })
