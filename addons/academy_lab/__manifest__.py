{
    'name': 'Academy Management',
    'version': '1.0',
    'category': 'Education',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'security/academy_security.xml',
        'views/academy_course_views.xml',
        'views/academy_category_views.xml',
        'views/academy_enrollment_views.xml',
        'views/res_partner_views.xml',
        'views/academy_courses_menus.xml',
    ],
    'installable': True,
    'application': True,
    # ADD THESE LINES:
    'auto_install': False,
    'license': 'LGPL-3',
}