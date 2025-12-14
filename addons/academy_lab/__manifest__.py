{
    'name': 'Academy lab',
    'version': '18.0.1.0',
    'summary': 'training academy management system',
    'depends': ['base','mail','contact'],
    'data':[
        'security/ir.model.access.csv',
        'views/academy_course_views.xml',
        'views/academy_enrollment_views.xml',
        'views/res_partner_views.xml',
        'views/academy_course_menus.xml'



    ],

    'application': True,


}