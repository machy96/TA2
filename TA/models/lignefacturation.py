from odoo import models, fields, api


class LigneFacturation(models.Model):
    _name = 'ligne.facturation'
    _description = 'Ligne de Facturation'

    date_ligne = fields.Date(string='Date')
    type_ligne = fields.Selection([
        ('vente', 'Vente'),
        ('achat', 'Achat')
    ], string='Type')
    fournisseur_id = fields.Many2one('res.partner', string='Fournisseur')
    client_id = fields.Many2one('res.partner', string='Client')
    categorie_id = fields.Many2one('product.category', string='Catégorie de produit')
    produit_id = fields.Many2one('product.product', string='Produit')
    description = fields.Text(string='Description de la ligne de facture')
    prix_unitaire = fields.Float(string='Prix unitaire')
    quantite = fields.Integer(string='Quantité')
    fact_client = fields.Selection([
        ('a_facturer', 'À facturer'),
        ('facture', 'Facturé'),
        ('na', 'N/A')
    ], string='Statut de facturation client')
    n_fact_client = fields.Char(string='Numéro de facture client')
    fact_frs = fields.Selection([
        ('a_facturer', 'À facturer'),
        ('facture', 'Facturé'),
        ('na', 'N/A')
    ], string='Statut de facturation fournisseur')
    n_fact_frs = fields.Char(string='Numéro de facture fournisseur')

    dossier_id = fields.Many2one('dossier', string='Dossier associé')
