from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta
from odoo.tools import format_amount


class Dossier(models.Model):
    _name = 'ta.dossier'
    _description = 'DOSSIER'
    _rec_name = 'sequence'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Hériter de mail.thread et mail.activity.mixin

    sequence = fields.Char('Name', default='New', readonly=True)
    reference_client = fields.Char(string='Référence client')
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('ouvert', 'Ouvert'),
        ('attente_bad', 'Attente BAD'),
        ('preparation_dum', 'Préparation DUM'),
        ('signe', 'Signé'),
        ('livre', 'Livré'),
        ('facture', 'Facturé')
    ], string='Statut', default='draft')
    shipper_id = fields.Many2one('res.partner', 'Shipper', required=True, help="Shipper's Details")
    consignee_id = fields.Many2one('res.partner', 'Consignee', required=True, help="Details of consignee")
    date = fields.Date(string='Date', default=lambda self: fields.Date.context_today(self))
    poids_brut = fields.Float(string='Poids brut (kg)')
    nombre = fields.Char(string='Colisage')
    emballage = fields.Selection([('type1', 'Type 1'), ('type2', 'Type 2')], string='Emballage')
    loading_port_id = fields.Selection([('shanghai', 'Shanghai (Chine)'), ], string='Port de Chargement')
    discharging_port_id = fields.Selection([
        ('shanghai', 'Shanghai (Chine)'),
        ('singapore', 'Singapour (Singapour)'),
        ('rotterdam', 'Rotterdam (Pays-Bas)'),
    ], string='Port de Déchargement')
    transport = fields.Selection([
        ('routier', 'Routier'),
        ('maritime', 'Maritime'),
        ('aerien', 'Aérien')],
        string='Transport', default='maritime')
    groupage_complet = fields.Selection([('g', 'Groupage'), ('c', 'Complet')], string='Groupage/Complet')
    import_export = fields.Selection([('import', 'Import'), ('export', 'Export')], string='Import/Export',
                                     default='import')
    incoterm_id = fields.Selection([
        ('exw', 'EXW - Ex Works '),
        ('fca', 'FCA - Free Carrier '),
        ('cpt', 'CPT - Carriage Paid To '),
        ('cip', 'CIP - Carriage and Insurance Paid To '),
        ('dap', 'DAP - Delivered At Place '),
        ('dpu', 'DPU - Delivered at Place Unloaded '),
        ('ddp', 'DDP - Delivered Duty Paid '),
        ('fob', 'FOB - Free On Board '),
        ('cfr', 'CFR - Cost and Freight'),
        ('cif', 'CIF - Cost, Insurance and Freight '),
    ], string='Incoterm')
    expected_date = fields.Date(string='Expected Date', compute='_compute_expected_date', store=True)
    type_titre_transport = fields.Selection([
        ('lta', 'LTA'),
        ('cnt', 'CNT'),
        ('cmr', 'CMR')
    ], string='Titre de Transport', default='cnt')
    ref_titre_transport = fields.Char(string='Numéro DUM')
    transport_ids = fields.Text(string='Liste de transport')

    date_reception_dossier = fields.Date(string='Date réception dossier')
    date_ventilation = fields.Date(string='Date ventilation')
    date_saisie = fields.Date(string='Date saisie')
    bureau = fields.Selection([('bureau1', 'Bureau 1')], string='Bureau')
    regime = fields.Selection([('regime1', 'Régime 1')], string='Régime')
    annee = fields.Char(string='Year (Annee)')
    numero_dum = fields.Char(string='Numéro DUM')
    date_signature = fields.Date(string='Date signature')
    commis_id = fields.Many2one('res.users', string='Commis')
    date_facturation = fields.Date(string='Date facturation')
    date_liquidation = fields.Date(string='Date liquidation')
    date_mainlevee = fields.Date(string='Date mainlevée')
    date_livraison = fields.Date(string='Date livraison')
    facture_summary_html = fields.Html(
        string='Résumé Factures',
        compute='_compute_facture_summary_html',
        sanitize=False,  # Permet de conserver le HTML tel quel, faites attention à l'injection HTML
    )

    controle_douanier_ids = fields.One2many('ta.controledouanier', 'dossier_id', string='Contrôles douaniers')
    ligne_facturation_ids = fields.One2many('ligne.facturation', 'dossier_id', string='Lignes de Facturation')
    ventilations_ids = fields.One2many('ventilation.model', 'dossier_id', string='Ventilations')
    # Supposons que le modèle de facture d'Odoo soit 'account.move' et que chaque facture ait un champ 'dossier_id' le reliant au dossier
    facture_ids = fields.One2many('account.move', 'dossier_id', string='Factures Associées')


    # Nouveau : Champ calculé pour récupérer les lignes de facture liées
    ligne_facture_ids = fields.One2many('account.move.line', compute='_compute_ligne_facture_ids', string='Lignes de Facture')


    @api.depends('date')
    def _compute_expected_date(self):
        for record in self:
            if record.date:
                record.expected_date = fields.Date.to_string(
                    fields.Date.from_string(record.date) + timedelta(days=1))
            else:
                record.expected_date = False

    @api.depends('facture_ids', 'facture_ids.invoice_line_ids')
    def _compute_facture_summary_html(self):
        for dossier in self:
            products_summary = {}
            total_sales = 0
            total_purchases = 0

            for invoice in dossier.facture_ids:
                sign = 1 if invoice.move_type == 'out_invoice' else -1
                for line in invoice.invoice_line_ids.filtered(lambda l: l.product_id):
                    product = line.product_id
                    amount = line.price_subtotal * sign

                    if product not in products_summary:
                        products_summary[product] = {'sales': 0, 'purchases': 0}
                    if sign == 1:
                        products_summary[product]['sales'] += amount
                        total_sales += amount
                    else:
                        products_summary[product]['purchases'] += amount
                        total_purchases += amount

            # Construction du contenu HTML avec les classes CSS d'Odoo
            html_content = """
                <table class="o_list_view table table-condensed table-striped o_list_view_ungrouped">
                    <thead>
                        <tr>
                            <th>Produit</th>
                            <th>Ventes</th>
                            <th>Achats</th>
                            <th>Delta</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            for product, amounts in products_summary.items():
                delta = amounts['sales'] + amounts['purchases']  # Achats sont déjà négatifs
                html_content += f"""
                    <tr>
                        <td>{product.display_name}</td>
                        <td>{amounts['sales']}</td>
                        <td>{amounts['purchases']}</td>
                        <td>{delta}</td>
                    </tr>
                """

            # Calcul de la marge totale
            total_margin = total_sales + total_purchases
            html_content += f"""
                    <tr class="o_list_view_total">
                        <td><strong>Total Marge</strong></td>
                        <td></td>
                        <td></td>
                        <td><strong>{total_margin}</strong></td>
                    </tr>
                    </tbody>
                </table>
            """

            dossier.facture_summary_html = html_content
    @api.model
    def create(self, vals):
        # Création d'un enregistrement dossier avec une séquence
        if vals.get('sequence', 'New') == 'New':
            vals['sequence'] = self.env['ir.sequence'].next_by_code('ta.dossier.sequence') or 'New'

        # Appel à la méthode create du parent pour sauvegarder le dossier
        new_record = super(Dossier, self).create(vals)

        return new_record
