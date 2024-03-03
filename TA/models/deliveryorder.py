from odoo import models, fields


class DeliveryOrder(models.Model):
    _name = 'ta.delivery.order'
    _description = 'Bon de Livraison'

    dossier_id = fields.Many2one('ta.dossier', string='Dossier Associé', required=True)

    # Champs liés
    shipper_id = fields.Many2one('res.partner', related='dossier_id.shipper_id', string='Expéditeur', readonly=True)
    consignee_id = fields.Many2one('res.partner', related='dossier_id.consignee_id', string='Destinataire',
                                   readonly=True)
    poids_brut = fields.Float(related='dossier_id.poids_brut', string='Poids Brut', readonly=True)
    nombre = fields.Char(related='dossier_id.nombre', string='Colisage', readonly=True)
    emballage = fields.Selection(related='dossier_id.emballage', string='Emballage', readonly=True)


    # Nouveaux champs ajoutés
    transporteur_id = fields.Many2one('res.partner', string='Transporteur')
    destination = fields.Text(string='Destination')
    ref_tc_rem = fields.Text(string='Numéro TC/REM')