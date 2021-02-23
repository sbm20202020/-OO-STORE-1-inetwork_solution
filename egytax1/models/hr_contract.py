from odoo import models, fields, api


class HRContract(models.Model):
    _inherit = 'hr.contract'

    taxedsalary = fields.Float('Taxed Salary', )


    def calc_taxed_salary(self):
        for rec in self:
            taxedsalary = 0.0
            contract_ids = [rec.id]
            contract_id = rec.id
            employee = rec.employee_id
            blacklist = []
            localdict = dict(employee=employee,contract=rec)
            obj_rule = self.env['hr.salary.rule']
            structure_ids = rec.get_all_structures()
            rule_ids = self.env['hr.payroll.structure'].browse(structure_ids).get_all_rules()
            sorted_rule_ids = [id for id, sequence in sorted(rule_ids, key=lambda x: x[1])]
            for rule in obj_rule.browse(sorted_rule_ids):
                # print (rule.id,'rule.id')
                localdict['result'] = None
                localdict['result_qty'] = 1.0
                localdict['result_rate'] = 100
                if rule._satisfy_condition(localdict) and rule.id not in blacklist:
                    if (rule.include):
                        amount, qty, rate = rule._compute_rule(localdict)
                        tot_rule = amount * qty * rate / 100.0
                        taxedsalary = taxedsalary + tot_rule
            rec.taxedsalary = taxedsalary
            print('taxsalary', taxedsalary)

