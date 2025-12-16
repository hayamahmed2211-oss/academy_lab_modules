from odoo import models, fields, api
from odoo.exceptions import ValidationError

class AcademyCourse(models.Model):
    _name = 'academy.course'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Academy Course'

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(required=True, index=True)
    description = fields.Text()
    instructor_id = fields.Many2one('res.partner', string="Instructor")
    category_id = fields.Many2one('academy.course.category', string="Category")
    duration_hours = fields.Float(string="Duration (hours)")
    max_students = fields.Integer(default=20, string="Maximum Students")
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled')
    ], default='draft', tracking=True, string="Status")
    
    start_date = fields.Date(tracking=True)
    end_date = fields.Date(tracking=True)
    enrollment_ids = fields.One2many("academy.enrollment", 'course_id', string="Enrollments")

    # Computed fields
    enrolled_count = fields.Integer(
        compute='_compute_counts', 
        store=True, 
        string="Enrolled Students"
    )
    available_seats = fields.Integer(
        compute='_compute_counts', 
        store=True, 
        string="Available Seats"
    )
    is_full = fields.Boolean(
        compute='_compute_counts', 
        store=True, 
        string="Is Full"
    )
    
    # Search field
    is_full_search = fields.Boolean(
        compute='_compute_counts',
        store=True,
        string="Full (Search)",
        help="Stored field for searching/filtering purposes"
    )

    instructor_name = fields.Char(related='instructor_id.name', store=True)
    
    # SQL Constraints
    _sql_constraints = [
        ('unique_code', 'UNIQUE(code)', 'Course code must be unique')
    ]

    @api.depends('enrollment_ids.state', 'max_students')
    def _compute_counts(self):
        """Compute enrollment counts, available seats, and full status."""
        for course in self:
            # Count only confirmed enrollments
            confirmed_enrollments = course.enrollment_ids.filtered(
                lambda e: e.state == 'confirmed'
            )
            course.enrolled_count = len(confirmed_enrollments)
            
            # Calculate available seats
            course.available_seats = course.max_students - course.enrolled_count
            
            # Determine if course is full
            course.is_full = course.available_seats <= 0
            course.is_full_search = course.available_seats <= 0

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        """Validate that end date is after start date."""
        for course in self:
            if course.start_date and course.end_date and course.end_date < course.start_date:
                raise ValidationError('End date must be after start date')
    
    @api.constrains('max_students')
    def _check_max_students(self):
        """Validate maximum students is positive."""
        for course in self:
            if course.max_students <= 0:
                raise ValidationError('Maximum students must be greater than zero')
    
    @api.model
    def create(self, vals):
        """Override create to uppercase course code."""
        if vals.get('code'):
            vals['code'] = vals['code'].upper().strip()
        return super().create(vals)
    
    def write(self, vals):
        """Override write to uppercase course code if being updated."""
        if vals.get('code'):
            vals['code'] = vals['code'].upper().strip()
        return super().write(vals)

    # State transition methods
    def action_publish(self):
        """Publish a draft course."""
        for course in self:
            if course.state != 'draft':
                raise ValidationError("Only draft courses can be published")
            course.state = 'published'
    
    def action_start(self):
        """Start a published course."""
        for course in self:
            if course.state != 'published':
                raise ValidationError("Only published courses can be started")
            course.state = 'in_progress'
    
    def action_complete(self):
        """Complete a course that's in progress."""
        for course in self:
            if course.state != 'in_progress':
                raise ValidationError("Only courses in progress can be completed")
            course.state = 'done'
    
    def action_cancel(self):
        """Cancel a course."""
        for course in self:
            if course.state in ['done', 'cancelled']:
                raise ValidationError("Cannot cancel completed or already cancelled courses")
            course.state = 'cancelled'
    
    def action_draft(self):
        """Reset a course to draft state."""
        for course in self:
            if course.state not in ['cancelled']:
                raise ValidationError("Only cancelled courses can be reset to draft")
            course.state = 'draft'
    
    def action_view_enrollments(self):
        """Action to view enrollments for this course."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Enrollments for {self.name}',
            'res_model': 'academy.enrollment',
            'view_mode': 'list,form',
            'domain': [('course_id', '=', self.id)],
            'context': {
                'default_course_id': self.id,
                'default_student_id': False,
                'search_default_confirmed': 1,
            },
        }
    
    # Search methods
    @api.model
    def _search_is_full(self, operator, value):
        """Custom search method for is_full field."""
        courses = self.search([])
        
        if operator == '=':
            if value:
                full_courses = courses.filtered(lambda c: c.is_full)
            else:
                full_courses = courses.filtered(lambda c: not c.is_full)
        elif operator == '!=':
            if value:
                full_courses = courses.filtered(lambda c: not c.is_full)
            else:
                full_courses = courses.filtered(lambda c: c.is_full)
        else:
            return []
        
        return [('id', 'in', full_courses.ids)]