from odoo import models, fields, api
from typing import dicts, Any
from odoo.exceptions import ValidationError

class AcademyCourse(models.model):
    _name= 'academy.course'
    _inherit= ['mail.thread','mail.activity.mixin']

    name= fields.char(required=True, tracking=True)
    code=fields.char(required=True, index=True)
    description= fields.text()
    instructor_id= fields.Many2one('res.partner')
    category_id= fields.Many2one('academy.course.category')
    duration_hours= fields.float()
    max_students= fields.integer(default='20')
    state= fields.selection([
        ('draft', 'Draft'),
        ('published','Published'),
        ('in progress', 'In progress'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled')
    ],default='draft', tracking= True)
    start_date= fields.date(tracking= True)
    end_date= fields.date(tracking= True)
    enrollment_ids= fields.One2many("academy.enrollment",'course_id')

    enrolled_count= fields.integer(compute='_compute_counts', store=True)
    available_seats= fields.integer(compute= '_compute_counts', store=True)
    is_full= fields.boolean(compute= '_compute_counts', store=True)

    instructor_name= fields.char(related='instructor_id.name', store=True)
    _sql_constraints=['unique_code', unique(code), 'Course code must be unique'
    ]

    @api.depends('enrollment_ids.state','max_students')
    def _compute_counts(self):
        for rec in self:
            confirmed= rec.enrollment_ids.filtered(lambda e: e.state == 'confirmed')
            rec.enrolled_count = len(confirmed)
            rec.available_seats = rec.max_students - rec.enrolled_students
            rec.is_full = rec.available_seats <= 0
    
    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for rec in self:
            if rec.start_date and rec.end_date and rec.end_date < rec.start_date:
                raise ValidationError('End date must be after start date')
    
    @api.constrains('max_students')
    def _check_max_students(self):
        for rec in self:
            if rec.max.students <=0:
                raise ValidationError('Max students must be greater than zero')
    @api.model
    def create(self, vals: Dict[str, Any]):
        if vals.get('code'):
            vals['code']= vals['code'].upper()
        return super().create(vals)
    def action_publish(self):
        self.state='published'
    def action_start(self):
        self.state='in_rogress'
    def action_complete(self):
        self.state='done'
    def action_cancel(self):
        self.state='cancelled'

