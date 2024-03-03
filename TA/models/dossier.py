from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta
from odoo.tools import format_amount


class Dossier(models.Model):
    _name = 'ta.dossier'
    _description = 'DOSSIER'
    _rec_name = 'sequence'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    sequence = fields.Char('Name', default='New')
    reference_client = fields.Char(string='Référence client')
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('ouvert', 'Ouvert'),
        ('attente_bad', 'Attente BAD'),
        ('preparation_dum', 'Préparation DUM'),
        ('signe', 'Signé'),
        ('pret_pour_sortie', 'Prêt pour sortie'),
        ('livre', 'Livré'),
        ('facture', 'Facturé'),
        ('cloture', 'Cloturé')
    ], string='Statut', compute='_compute_state', store=True)
    shipper_id = fields.Many2one('res.partner', 'Shipper', required=True, help="Shipper's Details")
    consignee_id = fields.Many2one('res.partner', 'Consignee', required=True, help="Details of consignee")
    date = fields.Date(string='Date', default=lambda self: fields.Date.context_today(self))
    poids_brut = fields.Float(string='Poids brut (kg)')
    nombre = fields.Char(string='Colisage')
    emballage = fields.Selection([
        ('carton', 'Carton'),
        ('colis', 'Colis'),
        ('palettes', 'Palettes'),
        ('container', 'Container'),
        ('remorque', 'Remorque'),
        ('fardeaux', 'Fardeaux'),
        ('sachet', 'Sachet'),
        ('fut', 'Fût'),
        ('boite', 'Boîte'),
        ('barquette', 'Barquette'),
        ('tube', 'Tube'),
        ('enveloppe', 'Enveloppe'),
        ('caisse', 'Caisse'),
        ('sac', 'Sac'),
        ('bouteille', 'Bouteille'),
        ('pot', 'Pot'),
        ('bidon', 'Bidon')
    ], string='Emballage')
    loading_port_id = fields.Selection([
        ('casablanca', 'Casablanca (Maroc) - MACAS'),
        ('tanger', 'Tanger (Maroc) - MATNG'),
        ('dakar', 'Dakar (Sénégal) - SNDAK'),
        ('lagos', 'Lagos (Nigeria) - NGLAG'),
        ('alexandria', 'Alexandrie (Égypte) - EGALY'),
        ('mombasa', 'Mombasa (Kenya) - KEMBA'),
        ('abidjan', 'Abidjan (Côte d\'Ivoire) - CIABJ'),
        ('durban', 'Durban (Afrique du Sud) - ZADUR'),
        ('tema', 'Tema (Ghana) - GHTEM'),
        ('beira', 'Beira (Mozambique) - MZBEW'),
        ('libreville', 'Libreville (Gabon) - GAFPO'),
        ('nouakchott', 'Nouakchott (Mauritanie) - MRNKC'),
        ('pointenoire', 'Pointe-Noire (Congo) - CGPNR'),
        ('maputo', 'Maputo (Mozambique) - MZMPM'),
        ('lusaka', 'Lusaka (Zambie) - ZMLUN'),
        ('casablanca', 'Port de Casablanca (Maroc) - MACAS'),
        ('tanger', 'Port de Tanger (Maroc) - MATNG'),
        ('dakar', 'Port de Dakar (Sénégal) - SNDAK'),
        ('lagos', 'Port de Lagos (Nigeria) - NGLAG'),
        ('alexandria', 'Port d\'Alexandrie (Égypte) - EGALY'),
        ('mombasa', 'Port de Mombasa (Kenya) - KEMBA'),
        ('abidjan', 'Port d\'Abidjan (Côte d\'Ivoire) - CIABJ'),
        ('durban', 'Port de Durban (Afrique du Sud) - ZADUR'),
        ('tema', 'Port de Tema (Ghana) - GHTEM'),
        ('beira', 'Port de Beira (Mozambique) - MZBEW'),
        ('libreville', 'Port de Libreville (Gabon) - GAFPO'),
        ('nouakchott', 'Port de Nouakchott (Mauritanie) - MRNKC'),
        ('pointenoire', 'Port de Pointe-Noire (Congo) - CGPNR'),
        ('shanghai', 'Shanghai (Chine) - CNPVG'),
        ('singapore', 'Singapour - SGSIN'),
        ('ningbo', 'Ningbo-Zhoushan (Chine) - CNNGB'),
        ('shenzhen', 'Shenzhen (Chine) - CNSHK'),
        ('guangzhou', 'Port de Guangzhou (Chine) - CNGZP'),
        ('busan', 'Port de Busan (Corée du Sud) - KRPUS'),
        ('qinhuangdao', 'Qinhuangdao (Chine) - CNQIN'),
        ('hongkong', 'Hong Kong - HKHKG'),
        ('qingdao', 'Qingdao (Chine) - CNTAO'),
        ('tianjin', 'Tianjin (Chine) - CNTXG'),
        ('rotterdam', 'Port de Rotterdam (Pays-Bas) - NLRTM'),
        ('xiamen', 'Xiamen (Chine) - CNXMN'),
        ('kaohsiung', 'Port de Kaohsiung (Taïwan) - TWKHH'),
        ('dalian', 'Dalian (Chine) - CNDLC'),
        ('ningbozhoushan', 'Ningbo-Zhoushan (Chine) - CNNGB'),
        ('portsaid', 'Port Saïd (Égypte) - EGPSD'),
        ('melbourne', 'Port de Melbourne (Australie) - AUMEL'),
        ('jakarta', 'Port de Jakarta (Indonésie) - IDJKT'),
        ('losangeles', 'Port de Los Angeles (États-Unis) - USLAX'),
        ('hamburg', 'Port de Hambourg (Allemagne) - DEHAM'),
        ('tanjunpelapas', 'Port de Tanjung Pelapas (Malaisie) - MYPAS'),
        ('longbeach', 'Port de Long Beach (États-Unis) - USLGB'),
        ('tanjungpriok', 'Port de Tanjung Priok (Indonésie) - IDTPK'),
        ('taipei', 'Port de Taipei (Taïwan) - TNTPE'),
        ('antwerp', 'Port d\'Anvers (Belgique) - BEANR'),
        ('sydney', 'Port de Sydney (Australie) - AUSYD'),
        ('vancouver', 'Port de Vancouver (Canada) - CAVAN'),
        ('porto', 'Port de Santos (Brésil) - BRSSZ'),
        ('qingdao', 'Port de Qingdao (Chine) - CNTAO'),
        ('santos', 'Port de Santos (Brésil) - BRSSZ'),
        ('jebelali', 'Port de Jebel Ali (Émirats arabes unis) - AEJEA'),
        ('houston', 'Port de Houston (États-Unis) - USHOU'),
        ('dubai', 'Port de Dubaï (Émirats arabes unis) - AEDUB'),
        ('shenzhen', 'Port de Shenzhen (Chine) - CNSHK'),
        ('hamad', 'Port Hamad (Qatar) - QAHAH'),
        ('portsaid', 'Port Said Est (Égypte) - EGPSD'),
        ('newyork', 'Port de New York/New Jersey (États-Unis) - USNYC'),
        ('colombo', 'Port de Colombo (Sri Lanka) - LKCMB'),
        ('felixstowe', 'Port de Felixstowe (Royaume-Uni) - GBFXT'),
        ('valencia', 'Port de Valence (Espagne) - ESVLC'),
        ('sharjah', 'Port de Sharjah (Émirats arabes unis) - AESHJ'),
        ('bremerhaven', 'Port de Brême (Allemagne) - DEBRV')
    ], string='POL')
    discharging_port_id = fields.Selection([
        ('casablanca', 'Casablanca (Maroc) - MACAS'),
        ('tanger', 'Tanger (Maroc) - MATNG'),
        ('dakar', 'Dakar (Sénégal) - SNDAK'),
        ('lagos', 'Lagos (Nigeria) - NGLAG'),
        ('alexandria', 'Alexandrie (Égypte) - EGALY'),
        ('mombasa', 'Mombasa (Kenya) - KEMBA'),
        ('abidjan', 'Abidjan (Côte d\'Ivoire) - CIABJ'),
        ('durban', 'Durban (Afrique du Sud) - ZADUR'),
        ('tema', 'Tema (Ghana) - GHTEM'),
        ('beira', 'Beira (Mozambique) - MZBEW'),
        ('libreville', 'Libreville (Gabon) - GAFPO'),
        ('nouakchott', 'Nouakchott (Mauritanie) - MRNKC'),
        ('pointenoire', 'Pointe-Noire (Congo) - CGPNR'),
        ('maputo', 'Maputo (Mozambique) - MZMPM'),
        ('lusaka', 'Lusaka (Zambie) - ZMLUN'),
        ('casablanca', 'Port de Casablanca (Maroc) - MACAS'),
        ('tanger', 'Port de Tanger (Maroc) - MATNG'),
        ('dakar', 'Port de Dakar (Sénégal) - SNDAK'),
        ('lagos', 'Port de Lagos (Nigeria) - NGLAG'),
        ('alexandria', 'Port d\'Alexandrie (Égypte) - EGALY'),
        ('mombasa', 'Port de Mombasa (Kenya) - KEMBA'),
        ('abidjan', 'Port d\'Abidjan (Côte d\'Ivoire) - CIABJ'),
        ('durban', 'Port de Durban (Afrique du Sud) - ZADUR'),
        ('tema', 'Port de Tema (Ghana) - GHTEM'),
        ('beira', 'Port de Beira (Mozambique) - MZBEW'),
        ('libreville', 'Port de Libreville (Gabon) - GAFPO'),
        ('nouakchott', 'Port de Nouakchott (Mauritanie) - MRNKC'),
        ('pointenoire', 'Port de Pointe-Noire (Congo) - CGPNR'),
        ('shanghai', 'Shanghai (Chine) - CNPVG'),
        ('singapore', 'Singapour - SGSIN'),
        ('ningbo', 'Ningbo-Zhoushan (Chine) - CNNGB'),
        ('shenzhen', 'Shenzhen (Chine) - CNSHK'),
        ('guangzhou', 'Port de Guangzhou (Chine) - CNGZP'),
        ('busan', 'Port de Busan (Corée du Sud) - KRPUS'),
        ('qinhuangdao', 'Qinhuangdao (Chine) - CNQIN'),
        ('hongkong', 'Hong Kong - HKHKG'),
        ('qingdao', 'Qingdao (Chine) - CNTAO'),
        ('tianjin', 'Tianjin (Chine) - CNTXG'),
        ('rotterdam', 'Port de Rotterdam (Pays-Bas) - NLRTM'),
        ('xiamen', 'Xiamen (Chine) - CNXMN'),
        ('kaohsiung', 'Port de Kaohsiung (Taïwan) - TWKHH'),
        ('dalian', 'Dalian (Chine) - CNDLC'),
        ('ningbozhoushan', 'Ningbo-Zhoushan (Chine) - CNNGB'),
        ('portsaid', 'Port Saïd (Égypte) - EGPSD'),
        ('melbourne', 'Port de Melbourne (Australie) - AUMEL'),
        ('jakarta', 'Port de Jakarta (Indonésie) - IDJKT'),
        ('losangeles', 'Port de Los Angeles (États-Unis) - USLAX'),
        ('hamburg', 'Port de Hambourg (Allemagne) - DEHAM'),
        ('tanjunpelapas', 'Port de Tanjung Pelapas (Malaisie) - MYPAS'),
        ('longbeach', 'Port de Long Beach (États-Unis) - USLGB'),
        ('tanjungpriok', 'Port de Tanjung Priok (Indonésie) - IDTPK'),
        ('taipei', 'Port de Taipei (Taïwan) - TNTPE'),
        ('antwerp', 'Port d\'Anvers (Belgique) - BEANR'),
        ('sydney', 'Port de Sydney (Australie) - AUSYD'),
        ('vancouver', 'Port de Vancouver (Canada) - CAVAN'),
        ('porto', 'Port de Santos (Brésil) - BRSSZ'),
        ('qingdao', 'Port de Qingdao (Chine) - CNTAO'),
        ('santos', 'Port de Santos (Brésil) - BRSSZ'),
        ('jebelali', 'Port de Jebel Ali (Émirats arabes unis) - AEJEA'),
        ('houston', 'Port de Houston (États-Unis) - USHOU'),
        ('dubai', 'Port de Dubaï (Émirats arabes unis) - AEDUB'),
        ('shenzhen', 'Port de Shenzhen (Chine) - CNSHK'),
        ('hamad', 'Port Hamad (Qatar) - QAHAH'),
        ('portsaid', 'Port Said Est (Égypte) - EGPSD'),
        ('newyork', 'Port de New York/New Jersey (États-Unis) - USNYC'),
        ('colombo', 'Port de Colombo (Sri Lanka) - LKCMB'),
        ('felixstowe', 'Port de Felixstowe (Royaume-Uni) - GBFXT'),
        ('valencia', 'Port de Valence (Espagne) - ESVLC'),
        ('sharjah', 'Port de Sharjah (Émirats arabes unis) - AESHJ'),
        ('bremerhaven', 'Port de Brême (Allemagne) - DEBRV')
    ], string='POD')
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
    expected_date = fields.Date(string='Date Prévu')
    type_titre_transport = fields.Selection([
        ('lta', 'LTA'),
        ('cnt', 'CNT'),
        ('cmr', 'CMR')
    ], string='Titre de Transport', default='cnt')
    ref_titre_transport = fields.Char(string='titre transport')
    transport_ids = fields.Text(string='Liste de transport')

    date_reception_dossier = fields.Date(string='Date réception dossier')
    date_ventilation = fields.Date(string='Date ventilation')
    date_saisie = fields.Date(string='Date saisie')
    bureau = fields.Selection([
        ('100', '100 Bureau d\'Agadir Ville'),
        ('101', '101 Bureau de Laâyoune'),
        ('104', '104 Bureau d\'Ed-Dakhla'),
        ('105', '105 Bureau de Tan-Tan'),
        ('200', '200 Bureau de Safi'),
        ('201', '201 Bureau de Marrakech Ville'),
        ('202', '202 Bureau d\'Essaouira'),
        ('203', '203 Bureau d\'Ouarzazate'),
        ('300', '300 Bureau de Casablanca MEAD'),
        ('301', '301 Bureau de Nouasser'),
        ('302', '302 Bureau de Mohammedia'),
        ('304', '304 Bureau de Casa Colis Postaux et Paquets-Poste'),
        ('305', '305 Bureau de Jorf Lasfar'),
        ('306', '306 Bureau de Casa Extérieur'),
        ('309', '309 Bureau de Casa Port'),
        ('310', '310 Bureau de Settat'),
        ('400', '400 Bureau de Tanger port'),
        ('401', '401 Bureau de Tanger Ville'),
        ('403', '403 Bureau de Kénitra'),
        ('404', '404 Bureau de Rabat Salé'),
        ('405', '405 Bureau de Rabat'),
        ('406', '406 Bureau de Larache'),
        ('407', '407 Bureau de Tétouan Ville'),
        ('411', '411 Bureau de Tanger-Méditerranée'),
        ('412', '412 Bureau de Tanger-Ibn Batouta'),
        ('408', '408 Bureau de Bab Sebta'),
        ('500', '500 Bureau Fès Ville'),
        ('501', '501 Bureau d\'Al Hoceima'),
        ('503', '503 Bureau Fès Garantie et Impôts Indirects'),
        ('504', '504 Bureau de Taza'),
        ('600', '600 Bureau d\'Oujda Ville'),
        ('603', '603 Bureau d\'Ahfir'),
        ('601', '601 Bureau de Zouj Beghal'),
        ('602', '602 Bureau de Nador'),
        ('607', '607 Bureau de Nador-port'),
        ('700', '700 Bureau de Meknès')
    ], compute='_compute_dum_details', store=True, string='Code Bureau')
    regime = fields.Selection([
        ('010', '010 MISE A LA CONSOMMATION DIRECTE'),
        ('060', '060 EXPORTATION EN SIMPLE SORTIE'),
        ('061', '061 EXPORTATION DANS LE CADRE DU SGP'),
        ('680',
         '680 EXPORTATION DEFINITIVE EN REGULARISATION D’EXPORTATION TEMPORAIRE POUR PERFECTIONNEMENT PASSIF (ETPP) OU D’EXPORTATION TEMPORAIRE (ET)'),
        ('069', '069 EXPORTATION DANS LE CADRE DU DRAWBACK'),
        ('020', '020 ADMISSION TEMPORAIRE POUR PERFECTIONNEMENT ACTIF (ATPA) AVEC PAIEMENT'),
        ('021', '021 ATPA SANS PAIEMENT'),
        ('022', '022 TRANSFORMATION SOUS DOUANE IMPORTATION FRACTIONNEE'),
        ('023', '023 TRANSFORMATION SOUS DOUANE PAPIER D’EDITION'),
        ('241', '241 TRANSFORMATION SOUS DOUANE AUTRES'),
        ('242', '242 ADMISSION TEMPORAIRE (AT) MATERIEL DE RECHERCHE HYDROCARBURE'),
        ('243', '243 AT DE MATERIEL SOUMIS A REDEVANCES TRIMESTRIELLES'),
        ('300', '300 AT DE MATERIEL NON SOUMIS A REDEVANCES TRIMESTRIELLES'),
        ('301', '301 AT DE MARCHANDISES REEXPORTEES POUR OPERATION DE COMMERCE TRIANGULAIRE'),
        ('302', '302 AT DE FILMS ET ENREGISTREMENTS LOUES OU PRETES'),
        ('303', '303 AT D’EMBALLAGES ET CONTENANTS IMPORTES VIDES'),
        ('310', '310 AT D’EMBALLAGES ET CONTENANTS IMPORTES PLEINS'),
        ('311', '311 AT DE MARCHANDISES (DELAI 6 MOIS)'),
        ('312', '312 AT DE MARCHANDISES (DELAI 2 ANS)'),
        ('321', '321 IMPORTATION ANTICIPEE DANS LE CADRE DE L’ECHANGE STANDARD'),
        ('322', '322 AT DES VEHICULES'),
        ('323', '323 AUTRES AT'),
        ('382', '382 EIF EN SUITE D\'EIF'),
        ('383', '383 EIF EN SUITE D\'ATPA'),
        ('384', '384 EIF EN SUITE D\'AT'),
        ('386', '386 EIF EN SUITE D’EPP'),
        ('080', '080 MUTATION ET ENTREE EN ENTREPOT'),
        ('081', '081 ENTREPOT EN SUITE DE REGIMES ECONOMIQUES'),
        ('817', '817 CESSION/ENTREE EN ENTREPOT D’EXPORTATION EN SUITE DE REGIMES ECONOMIQUES'),
        ('082', '082 ATPA EN SUITE DE REGIMES ECONOMIQUES'),
        ('820', '820 TRANSFORMATION SOUS DOUANE EN SUITE D’ATPA'),
        ('821', '821 TRANSFORMATION SOUS DOUANE EN SUITE D’AT'),
        ('822', '822 TRANSFORMATION SOUS DOUANE EN SUITE D’EPP'),
        ('083', '083 AT EN SUITE DE REGIMES ECONOMIQUES'),
        ('084', '084 CESSION/EXPORT PREALABLE'),
        ('849', '849 CESSION EXPORTATION PREALABLE DES VEHICULES AUTOMOBILES'),
        ('040', '040 MAC EN SUITE D\'ATPA'),
        ('430', '430 MAC EN SUITE DE TRANSFORMATION SOUS DOUANE'),
        ('044', '044 MAC EN SUITE D\'AT'),
        ('046', '046 MAC EN SUITE D\'ENTREPOT PUBLIC'),
        ('047', '047 MAC EN SUITE D\'ENTREPOT PRIVE PARTICULIER'),
        ('048', '048 MAC EN SUITE D\'ENTREPOT INDUSTRIEL FRANC'),
        ('070', '070 EXPORTATION EN SUITE D’ATPA AVEC PAIEMENT'),
        ('700', '700 EXPORTATION EN SUITE DE TRANSFORMATION SOUS DOUANE'),
        ('072', '072 EXPORTATION EN SUITE D’ATPA SANS PAIEMENT'),
        ('074', '074 EXPORTATION EN SUITE D\'AT'),
        ('075', '075 EXPORTATION EN SUITE D’EPP'),
        ('751', '751 EXPORTATION EN SUITE D’EIF'),
        ('752', '752 EXPORTATION EN SUITE D’ENTREPOT D’EXPORTATION'),
        ('077', '077 ETPP DE MARCHANDISES MAROCAINES OU NATIONALISEES'),
        ('770', '770 ETTP AVEC ECHANGE STANDARD'),
        ('771', '771 ETTP EN SUITE D\'ATPA'),
        ('772', '772 EXPORTATION EN SUITE D’IMPORTATION ANTICIPEE DANS LE CADRE DE L’ECHANGE STANDARD'),
        ('078', '078 EXPORTATION TEMPORAIRE'),
        ('079', '079 EXPORTATION PREALABLE'),
        ('051', '051 REIMPORTATION EN SUITE D’ETPP'),
        ('510', '510 REIMPORTATION EN SUITE D’ETPP AVEC ECHANGE STANDARD'),
        ('511', '511 REIMPORTATION DANS CADRE ETPP EN SUITE D\'ATPA'),
        ('052', '052 REIMPORTATION EN SUITE D’ET'),
        ('053', '053 REIMPORTATION EN SUITE DE DRAWBACK'),
        ('054', '054 REIMPORTATION EN SUITE D’AUTRES EXPORTATIONS'),
        ('055', '055 ATPA DE MARCHANDISES REIMPORTEES POUR RETOUCHES'),
        ('056', '056 AT DE MARCHANDISES REIMPORTEES'),
        ('087', '087 TRANSIT DE MARCHANDISES LOCALES'),
        ('090', '090 ENTREPOT DE PRODUITS PETROLIERS'),
        ('092', '092 ENTREPOT D\'AUTRES PRODUITS'),
        ('093', '093 ATPA DE MARCHANDISES SOUMISES A TIC'),
        ('094', '094 MAC EN SUITE D’ENTREPOT PRODUITS PETROLIERS'),
        ('095', '095 MAC EN SUITE DE SORTIE RAFFINERIE'),
        ('097', '097 MAC EN SUITE D’ENTREPOT AUTRES MARCHANDISES'),
        ('098', '098 ESSAI ET MARQUAGE DES OBJETS EN PLATINE, OR OU ARGENT'),
        ('099', '099 MAC D’AUTRES MARCHANDISES SOUMISES A TIC'),
        ('050', '050 MAC DE MARCHANDISES EN PROVENANCE DES ZONES FRANCHES'),
        ('221', '221 ATPA AVEC PAIEMENT EN PROVENANCE DES ZONES FRANCHES'),
        ('231', '231 ATPA SANS PAIEMENT EN PROVENANCE DES ZONES FRANCHES'),
        ('681', '681 EXPORTATION DEFINITIVE EN REGULARISATION D’ETPP OU D’ET VERS LES ZONES FRANCHES'),
        ('682', '682 EXPORTATION VERS L’ETRANGER EN SUITE D’EXPORTATION VIA LES ZONES FRANCHES LOGISTIQUES'),
        ('761', '761 EXPORTATION SIMPLE VERS LES ZONES FRANCHES'),
        ('762', '762 EXPORTATION EN SUITE D’ATPA VERS LES ZONES FRANCHES'),
        ('763', '763 EXPORTATION EN SUITE D’AT VERS LES ZONES FRANCHES'),
        ('764', '764 EXPORTATION EN SUITE D’ENTRPEPOT VERS LES ZONES FRANCHES'),
        ('765', '765 EXPORTATION TEMPORAIRE (ET) VERS LES ZONES FRANCHES'),
        ('766', '766 EXPORTATION POUR PERFECTIONNEMENT PASSIF (ETPP) VERS LES ZONES FRANCHES'),
        ('767', '767 EXPORTATION EN SUITE DE TRANSFORMATION SOUS DOUANE VERS LES ZONES FRANCHES'),
        ('768', '768 EXPORTATION VIA LES ZONES FRANCHES LOGISTIQUES'),
        ('769', '769 TRANSIT A L’IMPORT DE L’ETRANGER A DESTINATION DES ZONES FRANCHES'),
        ('855', '855 TRANSIT ENTRE ZONES FRANCHES AUTRES QUE PORTUAIRES ET AEROPORTUAIRES'),
        ('856', '856 TRANSIT A L’EXPORT VERS L’ETRANGER A PARTIR DES ZONES FRANCHES'),
        ('002', '002 TRANSBORDEMENT SUR L\'ETRANGER'),
        ('003', '003 TRANSPORT MARITIME INTERIEUR'),
        ('004', '004 DECLARATION OCCASIONNELLE IMPORT'),
        ('005', '005 DECLARATION OCCASIONNELLE EXPORT'),
        ('006', '006 DECLARATION PROVISOIRE IMPORT SIMPLE'),
        ('007', '007 DECLARATION PROVISOIRE IMPORT SOUS REGIMES ECONOMIQUES'),
        ('008', '008 DECLARATION D’ADMISSION TEMPORAIRE DE CONTENEURS'),
        ('009', '009 DECLARATION D’ADMISSION TEMPORAIRE DE VEHICULES A USAGE COMMERCIAL'),
        ('800', '800 EXPORTATION TEMPORAIRE DE CONTENEURS (D 21)'),
        ('900', '900 EXPORTATION TEMPORAIRE DE VEHICULES A USAGE COMMERCIAL (D 20)')
    ], compute='_compute_dum_details', store=True, string='Régime Douanier')
    annee = fields.Selection([
        ('2022', '2022'),
        ('2023', '2023'),
        ('2024', '2024'),
        ('2025', '2025'),
        ('2026', '2026'),
    ], compute='_compute_dum_details', store=True, string='Année')
    numero_dum = fields.Char(string='Numéro DUM')
    ancien_num_dossier = fields.Char(string='Ancien Dossier')
    commis_id = fields.Many2one('hr.employee', string='Commis')
    date_facturation = fields.Date(string='Date facturation')
    date_signature = fields.Date(string='Date signature', compute='_compute_event_dates')
    date_liquidation = fields.Date(string='Date liquidation', compute='_compute_event_dates')
    date_mainlevee = fields.Date(string='Date mainlevée', compute='_compute_event_dates')
    date_sortie = fields.Date(string='Date sortie', compute='_compute_event_dates')
    statut_fact = fields.Selection([
        ('en_cours', 'En cours'),
        ('signe', 'Signé'),
        ('pret_pour_sortie', 'Prêt pour sortie'),
        ('livre', 'Livré'),
        ('facture', 'Facturé'),
        ('cloture', 'Clôturé'),
    ], string='Statut Facture', default='en_cours')
    facture_summary_html = fields.Html(
        string='Résumé Factures',
        compute='_compute_facture_summary_html',
        sanitize=False,  # Permet de conserver le HTML tel quel, faites attention à l'injection HTML
    )
    email_ids = fields.One2many('ta.email', 'dossier_id', string='E-mails liés')
    controle_douanier_ids = fields.One2many('ta.controledouanier', 'dossier_id', string='Contrôles douaniers')
    ligne_facturation_ids = fields.One2many('ligne.facturation', 'dossier_id', string='Lignes de Facturation')
    ventilations_ids = fields.One2many('ventilation.model', 'dossier_id', string='Ventilations')
    facture_ids = fields.One2many('account.move', 'dossier_id', string='Factures Associées')
    delivery_order_ids = fields.One2many('ta.delivery.order', 'dossier_id', string='Bon de livraison')

    # Nouveau : Champ calculé pour récupérer les lignes de facture liées
    ligne_facture_ids = fields.One2many('account.move.line', compute='_compute_ligne_facture_ids',
                                        string='Lignes de Facture')

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

    @api.depends('numero_dum', 'email_ids', 'email_ids.event_name', 'email_ids.received_date')
    def _compute_event_dates(self):
        event_name_mapping = {
            'Signature': 'date_signature',
            'Liquidation': 'date_liquidation',
            'Main Levée Définitive': 'date_mainlevee',
            'Sortie': 'date_sortie',
        }

        for dossier in self:
            for event_name, field_name in event_name_mapping.items():
                # Recherche du dernier email correspondant à chaque événement pour le même numéro DUM
                last_email = self.env['ta.email'].search([
                    ('numero_dum_extracted', '=', dossier.numero_dum),
                    ('event_name', '=', event_name)],
                    order='received_date desc',
                    limit=1
                )
                # Mise à jour du champ calculé avec la date du dernier email trouvé
                if last_email:
                    setattr(dossier, field_name, last_email.received_date)
                else:
                    setattr(dossier, field_name, False)

    @api.depends('date_signature', 'date_mainlevee', 'date_sortie', 'statut_fact')
    def _compute_state(self):
        for invoice in self:
            if invoice.statut_fact == 'facture':
                invoice.state = 'facture'
            elif invoice.statut_fact == 'cloture':
                invoice.state = 'cloture'
            elif invoice.statut_fact == 'signe':
                invoice.state = 'signe'
            elif invoice.statut_fact == 'pret_pour_sortie':
                invoice.state = 'pret_pour_sortie'
            elif invoice.statut_fact == 'livre':
                invoice.state = 'livre'
            elif invoice.date_sortie:
                invoice.state = 'livre'
            elif invoice.date_mainlevee:
                invoice.state = 'pret_pour_sortie'
            elif invoice.date_signature:
                invoice.state = 'signe'
            else:
                invoice.state = 'preparation_dum'

    @api.model
    def create(self, vals):
        if vals.get('sequence', 'New') == 'New':
            vals['sequence'] = self.env['ir.sequence'].next_by_code('ta.dossier.sequence') or 'New'
        record = super(Dossier, self).create(vals)
        # Pas besoin d'appeler _update_related_emails ici si vous utilisez des champs calculés dans ta.email
        return record

    def write(self, vals):
        result = super(Dossier, self).write(vals)
        # Si le numéro de DUM est parmi les champs mis à jour
        if 'numero_dum' in vals:
            # Recherche et mise à jour des enregistrements ta.email correspondants
            self.env['ta.email'].search([('numero_dum_extracted', '=', vals['numero_dum'])]).write(
                {'dossier_id': self.id})
        return result

    @api.depends('numero_dum')
    def _update_related_emails(self):
        for record in self:
            if record.numero_dum:
                emails = self.env['ta.email'].search([
                    ('numero_dum_extracted', '=', record.numero_dum),
                    '|', ('dossier_id', '=', False), ('dossier_id', '!=', record.id)])
                if emails:
                    emails.write({'dossier_id': record.id})

    @api.depends('numero_dum')
    def _compute_dum_details(self):
        for record in self:
            if record.numero_dum and len(record.numero_dum) >= 10:
                # Assurez-vous que les valeurs extraites existent dans vos sélections
                bureau_code = record.numero_dum[:3]
                regime_code = record.numero_dum[3:6]
                annee_code = record.numero_dum[6:10]

                # Assignation conditionnelle en fonction de la validité
                record.bureau = bureau_code if bureau_code in dict(self._fields['bureau'].selection).keys() else False
                record.regime = regime_code if regime_code in dict(self._fields['regime'].selection).keys() else False
                record.annee = annee_code if annee_code in dict(self._fields['annee'].selection).keys() else False
            else:
                record.bureau = False
                record.regime = False
                record.annee = False

    @api.constrains('numero_dum')
    def _validate_dum(self):
        for record in self:
            if record.numero_dum:
                # Validation du bureau
                bureau_code = record.numero_dum[:3]
                valid_bureau_codes = [option[0] for option in self._fields['bureau'].selection]
                if bureau_code not in valid_bureau_codes:
                    raise ValidationError(f"Le code bureau '{bureau_code}' extrait du numéro DUM n'est pas valide.")

                # Validation du régime
                regime_code = record.numero_dum[3:6]
                valid_regime_codes = [option[0] for option in self._fields['regime'].selection]
                if regime_code not in valid_regime_codes:
                    raise ValidationError(f"Le code régime '{regime_code}' extrait du numéro DUM n'est pas valide.")

                # Validation de l'année
                annee_code = record.numero_dum[6:10]
                valid_annee_codes = [option[0] for option in self._fields['annee'].selection]
                if annee_code not in valid_annee_codes:
                    raise ValidationError(f"L'année '{annee_code}' extraite du numéro DUM n'est pas valide.")
                    pass

    def action_update_details(self):
        for dossier in self:
            # Mise à jour des champs calculés bureau, régime, année, etc.
            dossier._compute_dum_details()
            dossier._compute_event_dates()
            dossier._update_related_emails()
            # Mise à jour du numéro de dossier dans ta.email si nécessaire
            emails = self.env['ta.email'].search([('numero_dum_extracted', '=', dossier.numero_dum)])
            emails.write({'dossier_id': dossier.id})



