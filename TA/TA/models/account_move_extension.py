from odoo import models, fields

class AccountMoveExtension(models.Model):
    _inherit = 'account.move'

    dossier_id = fields.Many2one('ta.dossier', string='Dossier Associé')