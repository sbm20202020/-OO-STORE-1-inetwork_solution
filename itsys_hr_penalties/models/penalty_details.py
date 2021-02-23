from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning, RedirectWarning, ValidationError


class PenalityDetails(models.Model):
    _name = 'penalty.details'
    _rec_name = 'seq'
    _inherit = ['mail.thread']
    check1 = fields.Boolean()
    check2 = fields.Boolean()
    # check3=fields.Boolean()
    # text=fields.Text(default='please if you delete record in employees penality press in button GET EMPLOYEE',readonly=True)
    seq = fields.Char(string="Name", readonly=True)
    penalty_reason = fields.Many2one('penalty.reason')
    activity_ids = fields.One2many('mail.activity', 'calendar_event_id', string='Activities')
    bo_check = fields.Boolean()
    states = fields.Selection([
        ('new', 'new'),
        ('submit', 'Submit To Manager'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    ], default='new')
    # name=fields.Char(required=True)
    date = fields.Date(required=True)
    submit_for = fields.Selection([
        ('department', 'Department'),
        ('employee', 'Employee')], string='Submit For', required=True)

    allocation = fields.Selection([
        ('manauly', 'Manauly'),
        ('equal', 'Equal')])

    @api.constrains('cash', 'days', 'cash_emp')
    def not_minus(self):
        for rec in self:
            if rec.cash < 0:
                raise ValidationError(_('Cash is not minus'))
            if rec.cash == 0 and rec.submit_for == 'department':
                raise ValidationError(_('Cash is not zero'))

            if rec.days < 0:
                raise ValidationError(_('days is not minus'))
            if rec.days == 0 and rec.submit_for == 'employee' and rec.penalty_term == 'days':
                raise ValidationError(_('days is not zero'))

            if rec.cash_emp < 0:
                raise ValidationError(_('Cash is not minus'))
            if rec.cash_emp == 0 and rec.submit_for == 'employee' and rec.penalty_term == 'cash':
                raise ValidationError(_('Cash is not zero'))

    @api.onchange('submit_for', 'penalty_term')
    def empty_emp_dep(self):
        if self.submit_for == 'department':
            self.employee_id = False
            self.days = 0.0
            self.cash_emp = 0.0
        if self.submit_for == 'employee':
            self.department_id = False
            self.cash = 0.0
            self.employee_ids = False
            if self.penalty_term == 'days':
                self.cash_emp = 0.0
            if self.penalty_term == 'cash':
                self.days = 0.0
        if self.submit_for == False or self.penalty_term == False:
            self.employee_id = False
            self.department_id = False
            self.days = 0.0
            self.cash = 0.0
            self.employee_ids = False
            self.cash_emp = 0.0

    # @api.multi
    def action_sumbit(self):

        total = 0.0
        if self.employee_ids:
            for line in self.employee_ids:
                total += line.penalty
                if line.penalty <= 0:
                    raise ValidationError(
                        _('Penalty is not zero or minus'))
            if total == 0:
                raise ValidationError(
                    _('Total Penalty is not Zero'))

        if self.check1 == True and self.check2 == False:
            raise ValidationError(
                _(
                    'total penalty is smaller than cash value if delete employee please press button GET EMPLOYEE to update'))
        else:
            return self.write({'states': 'submit'})

    # @api.multi
    def action_approve(self):

        total = 0.0
        if self.employee_ids:
            for line in self.employee_ids:
                total += line.penalty
                if line.penalty <= 0:
                    raise ValidationError(
                        _('Penalty is not zero or minus'))

            if total == 0:
                raise ValidationError(
                    _('Total Penalty is not Zero'))

        if self.check1 == True and self.check2 == False:
            raise ValidationError(
                _(
                    'total penalty is smaller than cash value if delete employee please press button GET EMPLOYEE to update'))
        else:
            return self.write({'states': 'approved'})

    # @api.multi
    def action_set_to_declined(self):

        total = 0.0
        if self.employee_ids:
            for line in self.employee_ids:
                total += line.penalty
                if line.penalty <= 0:
                    raise ValidationError(
                        _('Penalty is not zero or minus'))

            if total == 0:
                raise ValidationError(
                    _('Total Penalty is not Zero'))

        if self.check1 == True and self.check2 == False:
            raise ValidationError(
                _(
                    'total penalty is smaller than cash value if delete employee please press button GET EMPLOYEE to update'))
        else:
            return self.write({'states': 'declined'})

    # @api.multi
    def action_set_return_draft(self):

        total = 0.0
        if self.employee_ids:
            for line in self.employee_ids:
                total += line.penalty
                if line.penalty <= 0:
                    raise ValidationError(
                        _('Penalty is not zero or minus'))

            if total == 0:
                raise ValidationError(
                    _('Total Penalty is not Zero'))

        if self.check1 == True and self.check2 == False:
            raise ValidationError(
                _(
                    'total penalty is smaller than cash value if delete employee please press button GET EMPLOYEE to update'))


        else:
            total = 0.0

            for line in self.employee_ids:
                total += line.penalty
                if line.penalty < 0:
                    raise ValidationError(
                        _('Penalty is not minus'))

            if total == 0 and self.allocation == 'manauly':
                raise ValidationError(
                    _('total penalty must not be zero'))
            else:
                return self.write({'states': 'new'})

    @api.model
    def create(self, values):
        seq = self.env['ir.sequence'].next_by_code('hr.penality') or '/'
        values['seq'] = seq
        res = super(PenalityDetails, self).create(values)

        return res

    @api.onchange('employee_ids')
    def ch(self):
        self.check2 = False
        # self.check3=False


        if self.allocation and self.department_id:
            se_emp = self.env['hr.employee'].search([('department_id', '=', self.department_id.id)])
            if self.allocation == 'equal':
                length = 0
                list_dep = []
                if self.employee_ids:
                    for line in self.employee_ids:
                        list_dep.append(line.department_id)

                if len(se_emp) != len(self.employee_ids) and self.department_id in list_dep:
                    self.check1 = True

    # @api.multi
    def write(self, vals):
        res = super(PenalityDetails, self).write(vals)

        total = 0.0
        if self.employee_ids:
            for line in self.employee_ids:
                total += line.penalty
                if line.penalty < 0:
                    raise ValidationError(
                        _('Penalty is not minus'))

            print ('kkkkk', total)
            if total > self.cash and total != 0 and self.allocation == 'manauly':
                raise ValidationError(
                    _('Total Penalty is Greater Than Cash Value'))

            if total < self.cash and total != 0 and self.allocation == 'manauly':
                raise ValidationError(
                    _('total penalty is smaller than cash value'))

                # if total < self.cash and total!=0 and self.allocation == 'manauly':
                #     raise ValidationError(
                #         _('total penalty is smaller than cash value'))

        return res

    # @api.multi
    def unlink(self):
        for line in self:
            if line.states == 'submit' or line.states == 'approved' or line.states == 'declined':
                raise ValidationError(_('you can not delete penality that is submit or approve or declined.'))

        return super(PenalityDetails, self).unlink()

    penalty_term = fields.Selection([
        ('days', 'Days'),
        ('cash', 'Cash')])
    days = fields.Float()
    cash_emp = fields.Float('Cash')
    cash = fields.Float()
    employee_id = fields.Many2one('hr.employee', 'Employee')
    employee_department = fields.Many2one('hr.department', 'Employee Department', related='employee_id.department_id')
    department_id = fields.Many2one('hr.department', 'HR Department')
    employee_ids = fields.Many2many('hr.employee.part', 'h1', 'h2')

    @api.constrains('allocation', 'department_id', 'cash')
    # @api.multi
    def change_allocation(self):
        # self.employee_ids=False
        total = 0.0
        if self.allocation and self.department_id:
            se_emp = self.env['hr.employee'].search([('department_id', '=', self.department_id.id)])
            list = []
            if self.employee_ids:
                for line in self.employee_ids:
                    list.append(line.penalty)

            if self.allocation == 'manauly':

                list_dep = []
                if self.employee_ids:
                    for line in self.employee_ids:
                        list_dep.append(line.department_id)
                if len(se_emp) == len(self.employee_ids) and self.department_id in list_dep or len(se_emp) != len(
                        self.employee_ids) and self.department_id not in list_dep or len(se_emp) == len(
                    self.employee_ids) and self.department_id not in list_dep or len(self.employee_ids) == 0:

                    if list.count(0) == len(self.employee_ids) or self.bo_check == True:
                        for line in self.employee_ids:
                            line.unlink()
                        if se_emp:
                            print ('jjjjjjjjjjjj', se_emp)
                            for line in se_emp:
                                print(line)
                                emp_part = self.env['hr.employee.part'].create(
                                    {'employee_id': line.id, 'department_id': line.department_id.id})
                                self.write({'employee_ids': [(4, emp_part.id)]})
                                print('jjjjjjjjjjjj')

                if self.employee_ids:
                    for line in self.employee_ids:
                        total += line.penalty
                        print (total)
                        if line.penalty < 0:
                            raise ValidationError(
                                _('Penalty is not minus'))
                    if total > self.cash and total != 0 and self.allocation == 'manauly':
                        raise ValidationError(
                            _('total penalty is greater than cash value'))

                    if total < self.cash and total != 0 and self.allocation == 'manauly':
                        raise ValidationError(
                            _('total penalty is smaller than cash value'))

                self.bo_check = False

            if self.allocation == 'equal':
                length = 0
                list_dep = []
                if self.employee_ids:
                    for line in self.employee_ids:
                        list_dep.append(line.department_id)
                if len(se_emp) == len(self.employee_ids) and self.department_id in list_dep or len(se_emp) != len(
                        self.employee_ids) and self.department_id not in list_dep or len(se_emp) == len(
                        self.employee_ids) and self.department_id not in list_dep or len(
                        self.employee_ids) == 0 or self.bo_check == False:
                    print('lllllllllllllllll')
                    length = len(se_emp)
                    if self.employee_ids:
                        for line in self.employee_ids:
                            line.unlink()
                    if se_emp:
                        print ('jjjjjjjjjjjj', se_emp)
                        for line in se_emp:
                            value = self.cash / length
                            emp_part = self.env['hr.employee.part'].create(
                                {'employee_id': line.id, 'department_id': line.department_id.id, 'penalty': value})
                            self.write({'employee_ids': [(4, emp_part.id)]})
                            print('jjjjjjjjjjjj')

                elif len(se_emp) != len(self.employee_ids) and self.department_id in list_dep:
                    length = len(self.employee_ids)
                    value = self.cash / length
                    if self.employee_ids:
                        for line in self.employee_ids:
                            line.penalty = value

                    self.check2 = True

                self.bo_check = True


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    penalty_id = fields.Many2one("penalty.details")


class HrEmployeepart(models.Model):
    _name = 'hr.employee.part'
    penalty_id = fields.Many2one("penalty.details")

    employee_id = fields.Many2one('hr.employee', 'Employee')
    department_id = fields.Many2one('hr.department', 'Employee Department', related='employee_id.department_id')
    penalty = fields.Float('Penalty')


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'
    day_pen = fields.Float('Day penalty')
    penalty = fields.Float('penalty')
    cash_emp = fields.Float()

    # @api.multi
    def compute_sheet(self):
        for payslip in self:
            emp_obj = self.env['penalty.details'].search(
                [('employee_id', '=', payslip.employee_id.id), ('states', '=', 'approved'),
                 ('date', '>=', payslip.date_from), ('date', '<=', payslip.date_to)])
            print('count of objects', len(emp_obj))
            day_total = 0
            cash_total = 0
            pen = 0
            for line in emp_obj:
                if line.penalty_term == 'days':
                    day_total += line.days

                if line.penalty_term == 'cash':
                    cash_total += line.cash_emp

            payslip.day_pen = day_total
            payslip.cash_emp = cash_total
            print("total days", day_total)

            emp_dep_obj = self.env['penalty.details'].search(
                [('department_id', '=', payslip.employee_id.department_id.id), ('states', '=', 'approved'),
                 ('date', '>=', payslip.date_from), ('date', '<=', payslip.date_to)])

            for l in emp_dep_obj:
                for rec in l.employee_ids:
                    if payslip.employee_id == rec.employee_id:
                        pen += rec.penalty
            payslip.penalty = pen
        return super(HrPayslip, self).compute_sheet()
