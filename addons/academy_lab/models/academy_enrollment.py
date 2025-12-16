from odoo import models, fields, api
from odoo.exceptions import ValidationError

class AcademyEnrollment(models.Model):
    _name = 'academy.enrollment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Academy Enrollment' 
    student_id = fields.Many2one('res.partner', required=True)
    course_id = fields.Many2one('academy.course', required=True)
    enrollment_date = fields.Date(default=fields.Date.today)
    state = fields.Selection([
        ('draft','Draft'),
        ('confirmed','Confirmed'),
        ('cancelled','Cancelled'),
        ('completed','Completed')
    ], default='draft', tracking=True)
    grade = fields.Float()
    attendance_percentage = fields.Float()
    notes = fields.Text()

    student_name = fields.Char(related='student_id.name', store=True)
    course_name = fields.Char(related='course_id.name', store=True)

    passed = fields.Boolean(compute='_compute_passed', store=True)

    _sql_constraints = [
        ('unique_student_course',
         'unique(student_id, course_id)',
         'Student already enrolled in this course')
    ]

    @api.depends('grade', 'attendance_percentage')
    def _compute_passed(self):
        for rec in self:
            rec.passed = rec.grade >= 60 and rec.attendance_percentage >= 75

    def action_confirm(self):
        for rec in self:
            if rec.course_id.is_full:
                raise ValidationError('Course is full')
            rec.state = 'confirmed'

    def action_cancel(self):
        self.state = 'cancelled'

    def action_complete(self):
        self.state = 'completed'
