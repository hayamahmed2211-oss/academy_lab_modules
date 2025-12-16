from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_student = fields.Boolean(string="Is Student")
    is_instructor = fields.Boolean(string="Is Instructor")

    student_enrollment_ids = fields.One2many(
        'academy.enrollment', 
        'student_id',
        string="Student Enrollments"
    )
    instructor_course_ids = fields.One2many(
        'academy.course', 
        'instructor_id',
        string="Instructor Courses"
    )

    # TEMPORARILY COMMENT OUT THESE FIELDS
    total_courses_enrolled = fields.Integer(
         compute='_compute_totals',
         string="Total Courses Enrolled"
     )
    total_courses_teaching = fields.Integer(
         compute='_compute_totals',
         string="Total Courses Teaching"
     )
    @api.depends('student_enrollment_ids', 'instructor_course_ids')
    def _compute_totals(self):
         """Compute total courses enrolled and teaching."""
         for partner in self:
             partner.total_courses_enrolled = len(partner.student_enrollment_ids)
             partner.total_courses_teaching = len(partner.instructor_course_ids)

    def action_view_student_enrollments(self):
        """Action to view all enrollments for this student."""
        self.ensure_one()
        
        return {
            'type': 'ir.actions.act_window',
            'name': f'{self.name} - Enrollments',
            'res_model': 'academy.enrollment',
            'view_mode': 'tree,form',
            'domain': [('student_id', '=', self.id)],
            'context': {
                'default_student_id': self.id,
            },
        }

    def action_view_instructor_courses(self):
        """Action to view all courses taught by this instructor."""
        self.ensure_one()
        
        return {
            'type': 'ir.actions.act_window',
            'name': f'{self.name} - Courses',
            'res_model': 'academy.course',
            'view_mode': 'tree,form',
            'domain': [('instructor_id', '=', self.id)],
            'context': {
                'default_instructor_id': self.id,
            },
        }