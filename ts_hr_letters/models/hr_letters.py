from odoo import api, fields, models, _
import base64
from odoo.exceptions import UserError
from datetime import timedelta, datetime
from ast import literal_eval


class HRContract(models.Model):
    _inherit = "hr.contract"

    x_hc_tds = fields.Char(string="TDS")
    x_hc_retention_bonus = fields.Char(string="Retention Amt.")


class HREmployee(models.Model):
    _inherit = "hr.employee"

    ts_resignation_date = fields.Date(string="Resignation Date")

    def action_experience_letter(self):
        lst = ['ts_resignation_date', 'company_id', 'job_id']
        missing_fields = []
        for field_name in lst:
            if not getattr(self, field_name, False):
                field_string = self._fields[field_name].string
                missing_fields.append(field_string)
        if missing_fields:
            fields_string = ', '.join(missing_fields)
            raise UserError(_('Missing required fields: %s') % fields_string)

        template_id = self.env.ref('ts_hr_letters.email_template_experience_letter').id
        compose_form_id = self.env.ref('mail.email_compose_message_wizard_form').id
        template = self.env['mail.template'].browse(template_id)
        experience_report = self.env.ref('ts_hr_letters.action_experience_letter_report')
        data_record = base64.b64encode(self.env['ir.actions.report'].sudo()._render_qweb_pdf(experience_report, [self.id], data=None)[0])
        report_name = 'Experience Letter - %s' % self.name
        ir_values = {
            'name': report_name,
            'type': 'binary',
            'datas': data_record,
            'store_fname': data_record,
            'mimetype': 'application/pdf',
            'res_model': 'hr.employee',
        }
        experience_report_attachment_id = self.env['ir.attachment'].sudo().create(ir_values)
        ctx = {
            'default_model': 'hr.employee',
            'default_res_id': self.id,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'custom_layout': "mail.mail_notification_paynow",
            'force_email': False,
            'default_attachment_ids': [(4, experience_report_attachment_id.id)]
        }
        return {
            'name': 'Experience Cum Relieving Letter Mail',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    def action_resignation_letter(self):
        lst = ['ts_resignation_date', 'company_id', 'parent_id']
        missing_fields = []
        for field_name in lst:
            if not getattr(self, field_name, False):
                field_string = self._fields[field_name].string
                missing_fields.append(field_string)
        if missing_fields:
            fields_string = ', '.join(missing_fields)
            raise UserError(_('Missing required fields: %s') % fields_string)
        
        if not self.contract_id.date_end:
            raise UserError('Invalid Contract End Date')


        template_id = self.env.ref('ts_hr_letters.email_template_resignation_letter').id
        compose_form_id = self.env.ref('mail.email_compose_message_wizard_form').id
        template = self.env['mail.template'].browse(template_id)

        resignation_report = self.env.ref('ts_hr_letters.action_resignation_letter_report')
        data_record = base64.b64encode(self.env['ir.actions.report'].sudo()._render_qweb_pdf(resignation_report, [self.id], data=None)[0])
        report_name = 'Resignation Acceptance Letter - %s' % self.name
        ir_values = {
            'name': report_name,
            'type': 'binary',
            'datas': data_record,
            'store_fname': data_record,
            'mimetype': 'application/pdf',
            'res_model': 'hr.employee',
        }
        resignation_report_attachment_id = self.env['ir.attachment'].sudo().create(ir_values)
        ctx = {
            'default_model': 'hr.employee',
            'default_res_id': self.id,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'custom_layout': "mail.mail_notification_paynow",
            'force_email': False,
            'default_attachment_ids': [(4, resignation_report_attachment_id.id)]
        }
        return {
            'name': 'Resignation Acceptance Letter Mail',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    def open_appointment_wizard(self):
        """Function to open wizard"""
        lst = ['company_id']
        missing_fields = []
        for field_name in lst:
            if not getattr(self, field_name, False):
                field_string = self._fields[field_name].string
                missing_fields.append(field_string)
        if missing_fields:
            fields_string = ', '.join(missing_fields)
            raise UserError(_('Missing required fields: %s') % fields_string)

        if not self.contract_ids:
            raise UserError(_('Employee has no contract.'))

        if not self.contract_ids[0].wage:
            raise UserError(_('Wage field in contract is empty.'))

        return {
            'name': 'Salary Structure For Appointment Letter',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'wiz.salary.structure',
            'target': 'new',
        }

    def open_appraisal_wizard(self):
        """Function to open wizard"""
        if not self.contract_ids:
            raise UserError(_('Employee has no contract.'))

        # Check if the employee has an active contract
        active_contract = False
        for contract in self.contract_ids:
            if contract.state and contract.date_end:
                if contract.state == 'open' and contract.date_end >= datetime.now().date():
                    active_contract = True
                    break

        if not active_contract:
            raise UserError(_('Employee has no active contract.'))

        if not self.contract_ids[0].wage:
            raise UserError(_('Wage field in contract is empty.'))

        return {
            'name': 'Salary Structure For Appraisal Letter',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'wiz.appraisal.letter',
            'target': 'new',
        }

    def action_promotion_letter(self):
        template_id = self.env.ref('ts_hr_letters.email_template_promotion_letter').id
        compose_form_id = self.env.ref('mail.email_compose_message_wizard_form').id
        template = self.env['mail.template'].browse(template_id)

        # Render the promotion letter report and create an attachment
        promotion_report = self.env.ref('ts_hr_letters.action_promotion_letter_report_id')
        data_record = base64.b64encode(self.env['ir.actions.report'].sudo()._render_qweb_pdf(promotion_report, [self.id], data=None)[0])
        report_name = 'Promotion Letter - %s' % self.name
        ir_values = {
            'name': report_name,
            'type': 'binary',
            'datas': data_record,
            'store_fname': data_record,
            'mimetype': 'application/pdf',
            'res_model': 'hr.employee',
        }
        promotion_report_attachment = self.env['ir.attachment'].sudo().create(ir_values)
        ctx = {
            'default_model': 'hr.employee',
            'default_res_id': self.id,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'custom_layout': "mail.mail_notification_paynow",
            'force_email': False,
            'default_attachment_ids': [(4, promotion_report_attachment.id)]
        }
        return {
            'name': 'Promotion Letter Mail',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }


class HRApplicant(models.Model):
    _inherit = "hr.applicant"

    def action_testing_mail(self):
        template_id = self.env.ref('ts_hr_letters.gmail_template_id').id
        compose_form_id = self.env.ref('mail.email_compose_message_wizard_form').id
        template = self.env['mail.template'].browse(template_id)
        ctx = {
            'default_model': 'hr.applicant',
            'default_res_id': self.id,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'custom_layout': "mail.mail_notification_paynow",
            'force_email': False,
        }
        return {
            'name': 'Gmail Mail',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    new_availability_date = fields.Date(string="New Availability Date", compute='_compute_availability')

    @api.depends('availability')
    def _compute_availability(self):
        for rec in self:
            if rec.availability:
                rec.new_availability_date = fields.Date.to_string(fields.Date.from_string(rec.availability) + timedelta(days=1))
            else:
                rec.new_availability_date = False

    def open_offer_wizard(self):
        """Function to open wizard"""
        lst = ['company_id', 'partner_name', 'job_id']
        missing_fields = []
        for field_name in lst:
            if not getattr(self, field_name, False):
                field_string = self._fields[field_name].string
                missing_fields.append(field_string)
        if missing_fields:
            fields_string = ', '.join(missing_fields)
            raise UserError(_('Missing required fields: %s') % fields_string)

        return {
            'name': 'Salary Structure For Offer Letter',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'wizard.offer.letter',
            'target': 'new',
        }

    def action_erp_creation(self):
        lst = ['partner_name', 'email_from', 'job_id', 'department_id']
        missing_fields = []
        for field_name in lst:
            if not getattr(self, field_name, False):
                field_string = self._fields[field_name].string
                missing_fields.append(field_string)
        if missing_fields:
            fields_string = ', '.join(missing_fields)
            raise UserError(_('Missing required fields: %s') % fields_string)

        template_id = self.env.ref('ts_hr_letters.email_template_erp_creation').id
        compose_form_id = self.env.ref('mail.email_compose_message_wizard_form').id
        template = self.env['mail.template'].browse(template_id)
        ctx = {
            'default_model': 'hr.applicant',
            'default_res_id': self.id,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'custom_layout': "mail.mail_notification_paynow",
            'force_email': False,
        }
        return {
            'name': 'ERP Creation Mail',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    def action_mail_id_creation(self):
        lst = ['partner_name', 'availability', 'email_from', 'job_id']
        missing_fields = []
        for field_name in lst:
            if not getattr(self, field_name, False):
                field_string = self._fields[field_name].string
                missing_fields.append(field_string)
        if missing_fields:
            fields_string = ', '.join(missing_fields)
            raise UserError(_('Missing required fields: %s') % fields_string)

        template_id = self.env.ref('ts_hr_letters.email_template_mail_creation_id').id
        compose_form_id = self.env.ref('mail.email_compose_message_wizard_form').id
        template = self.env['mail.template'].browse(template_id)
        ctx = {
            'default_model': 'hr.applicant',
            'default_res_id': self.id,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'custom_layout': "mail.mail_notification_paynow",
            'force_email': False,
        }
        return {
            'name': 'Mail ID Creation Mail',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    def action_send_email_joining(self):
        lst = ['company_id', 'partner_name']
        missing_fields = []
        for field_name in lst:
            if not getattr(self, field_name, False):
                field_string = self._fields[field_name].string
                missing_fields.append(field_string)
        if missing_fields:
            fields_string = ', '.join(missing_fields)
            raise UserError(_('Missing required fields: %s') % fields_string)

        template_id = self.env.ref('ts_hr_letters.email_template_joining_letter').id
        compose_form_id = self.env.ref('mail.email_compose_message_wizard_form').id
        template = self.env['mail.template'].browse(template_id)
        office_attachments = self.env['ir.config_parameter'].sudo().get_param('ts_hr_letters.office_attachment_ids',
                                                                              default='False')
        if office_attachments:
            office_attachment_ids = literal_eval(office_attachments)
        else:
            office_attachment_ids = []


        ctx = {
            'default_model': 'hr.applicant',
            'default_res_id': self.id,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'default_attachment_ids': [(6, 0, office_attachment_ids)] if office_attachments else False,
            'custom_layout': "mail.mail_notification_paynow",
            'force_email': False,
        }
        return {
            'name': 'Joining Mail',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    def action_send_email_letter(self):
        lst = ['job_id', 'availability', 'salary_proposed']
        missing_fields = []
        for field_name in lst:
            if not getattr(self, field_name, False):
                field_string = self._fields[field_name].string
                missing_fields.append(field_string)
        if missing_fields:
            fields_string = ', '.join(missing_fields)
            raise UserError(_('Missing required fields: %s') % fields_string)

        template_id = self.env.ref('ts_hr_letters.email_template_send_email').id
        compose_form_id = self.env.ref('mail.email_compose_message_wizard_form').id
        template = self.env['mail.template'].browse(template_id)
        ctx = {
            'default_model': 'hr.applicant',
            'default_res_id': self.id,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'custom_layout': "mail.mail_notification_paynow",
            'force_email': False,
        }
        return {
            'name': 'Documents Mail',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }


class HRJob(models.Model):
    _inherit = "hr.job"

    notice_period = fields.Selection([('one month', 'One Month'), ('two month', 'Two Month'),
                                      ('Three month', 'Three Month')], string='Notice Period')