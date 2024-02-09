from odoo import models, fields, api


class Email(models.Model):
    _name = 'ta.email'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'E-mail Entrant'

    subject = fields.Char(string='Sujet')
    body_html = fields.Html(string='Corps HTML')
    email_from = fields.Char(string='De')
    email_to = fields.Char(string='À')
    received_date = fields.Datetime(string='Date de Réception')
    numero_dum_extracted = fields.Char(string="Numéro DUM Extrait")
    dossier_id = fields.Many2one('ta.dossier', string='Dossier Associé')
