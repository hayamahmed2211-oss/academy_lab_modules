from odoo import models, fields, api

class AcademyCourseCategory(models.Model):
    _name = 'academy.course.category'
    _description = 'Course Category'  # Added for Odoo 18

    name = fields.Char(required=True)
    description = fields.Text()
    course_ids = fields.One2many('academy.course', 'category_id')
    course_count = fields.Integer(compute='_compute_course_count', store=True)

    @api.depends('course_ids')
    def _compute_course_count(self):
        for rec in self:
            rec.course_count = len(rec.course_ids)
    
    def action_view_courses(self):
        """Action to view courses in this category."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Courses in {self.name}',
            'res_model': 'academy.course',
            'view_mode': 'list,form',
            'domain': [('category_id', '=', self.id)],
            'context': {'default_category_id': self.id},
        }