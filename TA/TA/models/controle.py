from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ControleDouanier(models.Model):
    _name = 'ta.controledouanier'
    _description = 'Suivi des contrôles douaniers'

    dossier_id = fields.Many2one('ta.dossier', string='Dossier')
    sequence_dossier = fields.Char(related='dossier_id.sequence', string='Num Dossier')
    state_dossier = fields.Selection(related='dossier_id.state', string='Statut Dossier', readonly=True)
    date_dossier = fields.Date(related='dossier_id.date', string='Date Dossier', readonly=True)
    loading_port_id = fields.Selection(related='dossier_id.loading_port_id', string='Port de Chargement', readonly=True)
    shipper_id = fields.Many2one(related='dossier_id.shipper_id', string='Shipper du Dossier', readonly=True)
    consignee_id = fields.Many2one(related='dossier_id.consignee_id', string='Consignee du Dossier', readonly=True)
    poids_brut = fields.Float(related='dossier_id.poids_brut', string='Poids Brut du Dossier (kg)', readonly=True)
    nombre = fields.Char(related='dossier_id.nombre', string='Colisage du Dossier', readonly=True)

    type_controle = fields.Selection(
        [('ctrl_douane', 'CTRL Douane'), ('ctrl_onssa', 'CTRL ONSSA'), ('ctrl_onssa', 'CTRL ONSSA')],
        string='Type de contrôle')
    selectivite = fields.Selection([('ac', 'AC'), ('vp', 'VP')], string='Sélectivité')
    date_controle = fields.Date(string='Date contrôle')
    obtenu = fields.Boolean(string='Obtenu?')
