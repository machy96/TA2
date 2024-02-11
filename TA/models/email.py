from odoo import models, fields, api
import re
import logging

_logger = logging.getLogger(__name__)


class Email(models.Model):
    _name = 'ta.email'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'E-mail Entrant'

    email_from = fields.Char(string='De', compute='_compute_email_details', store=True)
    received_date = fields.Datetime(string='Date de Réception', compute='_compute_email_details', store=True)
    subject = fields.Char(string='Sujet', compute='_compute_email_details', store=True)
    body_html = fields.Html(string='Corps HTML', compute='_compute_email_details', store=True)
    numero_dum_extracted = fields.Char(string="Numéro DUM Extrait", compute='_compute_email_details', store=True)
    event_name = fields.Char(string="Nom de l’Événement", compute='_compute_email_details', store=True)
    dossier_id = fields.Many2one('ta.dossier', compute='_compute_dossier_id', store=True, string='Dossier Associé')

    @api.model
    def create_email_from_message(self, message_id):
        """
        Crée un nouvel enregistrement dans ta.email à partir d'un message_id donné.
        """
        message = self.env['mail.message'].browse(message_id)
        if not message:
            return False  # Ou gérer l'erreur comme vous le souhaitez

        # Supposons que message_id soit l'identifiant du mail.message que vous souhaitez lier
        email_values = {
            'message_ids': [(4, message.id)],  # Lien vers l'existant mail.message
            # Ajoutez ici d'autres champs nécessaires basés sur le message
        }

        # Utilisation de la logique existante pour peupler les champs calculés
        new_email = self.create(email_values)
        new_email._compute_email_details()
        return new_email

    @api.depends('message_ids')
    def _compute_email_details(self):
        for record in self:
            if record.message_ids:
                first_message = record.message_ids[0]
                record.email_from = first_message.email_from
                record.received_date = first_message.date
                record.subject = first_message.subject
                record.body_html = first_message.body
                record.numero_dum_extracted, record.event_name = self.extract_info_from_email(first_message.subject,
                                                                                              first_message.body)

    def extract_info_from_email(self, subject, body):
        numero_dum = ''
        event_name = 'Autre'

        # Expression régulière pour extraire le numéro DUM
        numero_dum_pattern = re.compile(r'\b\d{17}\b')
        numero_dum_match = numero_dum_pattern.search(body)
        if numero_dum_match:
            numero_dum = numero_dum_match.group(0)

        # Nettoie le sujet pour une comparaison plus fiable
        clean_subject = subject.strip() if subject else ""

        # Expressions régulières pour identifier les différents types d'événements
        patterns_events = [
            (r"Délivrance mainlevée sous réserve", "Main Levée Sous Réserve"),
            (r"Délivrance mainlevée définitive|Délivrance mainlevéepour la déclaration|Main levée Définitive",
             "Main Levée Définitive"),
            (r"Sortie de marchandises de la DUM", "Sortie"),
            (r"Déclaration Référence :", "Message inspecteur"),
            (r"Liquidation des Droits et Taxes", "Liquidation"),
            (r"Signature de déclaration", "Signature"),
            (r"Lancement du contrôle de la déclaration", "Lancement du Contrôle"),
            (r"Contre ecor de la DUM", "Contre Ecor"),
            (r"Délivrance bon de sortie", "Sortie"),
            (r"Quittance douanière", "Quittances"),
            (r"Vu embarquer", "Sortie"),
            (r"BADR - Traitement de la valeur", "Traitement de la valeur"),
            (r"BADR - Traitement de la valeur de la déclaration :", "Traitement de la valeur"),
        ]

        for pattern, event in patterns_events:
            if re.search(pattern, clean_subject):
                event_name = event
                break

        return numero_dum, event_name

    def update_event_name_from_subject(self):
        for email in self:
            numero_dum, event_name = email.extract_info_from_email(email.subject, email.body_html)
            email.event_name = event_name
            _logger.info(f"Event name mis à jour pour l'email {email.id} : {event_name}")

    @api.depends('numero_dum_extracted')
    def _compute_dossier_id(self):
        Dossier = self.env['ta.dossier']
        for email in self:
            # Recherche du dossier correspondant au 'numero_dum_extracted'
            dossier = Dossier.search([('numero_dum', '=', email.numero_dum_extracted)], limit=1)
            # Assignation de 'dossier_id' avec l'ID du dossier trouvé ou False si aucun n'est trouvé
            email.dossier_id = dossier.id if dossier else False