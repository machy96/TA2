# TA/__manifest__.py
{
    'name': 'TA',
    'version': '1.0',
    'summary': 'Module Transit',
    'sequence': -100,
    'description': """Module Transit""",
    'category': 'Logistique',
    'website': 'https://www.also.ma',
    'depends': ['base','account','mail'],
    'data': [
        'security/ir.model.access.csv',
    	'views/dossier_views.xml',
        'views/email_views.xml',
        'data/ta_dossier_data.xml',
        'views/ventilation_views.xml',
        'views/report_bon_livraison.xml',
        'views/controle_views.xml',
        'views/lignefacturation.xml',
        'views/account_move_views.xml',
        'views/action.xml',
    ],
    'demo': [
        # 'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

