from odoo import models, fields, api

class AcademyCourseCategory(models.Model):
    _name = 'academy.course.category'

    name = fields.Char(required=True)
    description = fields.Text()
    course_ids = fields.One2many('academy.course', 'category_id')
    course_count = fields.Integer(compute='_compute_course_count', store=True)

    @api.depends('course_ids')
    def _compute_course_count(self):
        for rec in self:
            rec.course_count = len(rec.course_ids)
