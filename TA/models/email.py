from odoo import models, fields, api

class Email(models.Model):
    _name = 'ta.email'
    _description = 'E-mail Entrant'

    subject = fields.Char(string='Sujet')
    body_html = fields.Html(string='Corps HTML')
    email_from = fields.Char(string='De')
    email_to = fields.Char(string='À')
    received_date = fields.Datetime(string='Date de Réception')
    numero_dum_extracted = fields.Char(string="Numéro DUM Extrait")
    dossier_id = fields.Many2one('ta.dossier', string='Dossier Associé')

    @api.model
    def create(self, vals):
        # Ici, vous pouvez ajouter la logique pour extraire le numéro DUM du corps de l'email si nécessaire
        # et mettre à jour `vals` en conséquence avant de créer l'enregistrement.
        return super(Email, self).create(vals)