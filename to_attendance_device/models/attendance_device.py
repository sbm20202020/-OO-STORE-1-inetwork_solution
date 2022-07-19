import logging
import pytz
from datetime import datetime
# import base64
# # import base64
# # import binascii
# import io
# from io import BytesIO
# import os
# from cryptography.fernet import Fernet
# from cryptography.hazmat.backends import default_backend
# from cryptography.hazmat.primitives import hashes
# from cryptography.hazmat.primitives.kdf.hkdf import HKDF
import binascii

from odoo import models, fields, api, registry, _
from odoo.exceptions import ValidationError, UserError
from odoo.osv import expression
from ..pyzk.zk import ZK
from ..pyzk.zk.exception import ZKErrorResponse, ZKNetworkError, ZKConnectionUnauthorized
from ..pyzk.zk.user import User

text_type = str
_logger = logging.getLogger(__name__)


def format_tz(env, dt, tz=False, format=False):
    record_user_timestamp = env.user.sudo().with_context(tz=tz or env.user.sudo().tz or 'UTC')
    timestamp = fields.Datetime.from_string(dt)

    ts = fields.Datetime.context_timestamp(record_user_timestamp, timestamp)

    if env.context.get('use_babel'):
        # Formatting available here : http://babel.pocoo.org/en/latest/dates.html#date-fields
        from babel.dates import format_datetime
        return format_datetime(ts, format or 'medium', locale=env.context.get("lang") or 'en_US')

    if format:
        return text_type(ts.strftime(format))
    else:
        lang = env.context.get("lang")
        langs = env['res.lang']
        if lang:
            langs = env['res.lang'].search([("code", "=", lang)])
        format_date = langs.date_format or '%B-%d-%Y'
        format_time = langs.time_format or '%I-%M %p'

        fdate = text_type(ts.strftime(format_date))
        ftime = text_type(ts.strftime(format_time))
        m=u"%s %s%s" % (fdate, ftime, (u' (%s)' % tz) if tz else u'')
        print("mmmmm",ts)
        return u"%s %s%s" % (fdate, ftime, (u' (%s)' % tz) if tz else u'')


class AttendanceDevice(models.Model):
    _name = 'attendance.device'
    _description = 'Attendance Device'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'to.base']

    def _get_default_attendance_states(self):
        att_state_ids = self.env['attendance.state']

        # Normal Working Attendance
        attendance_device_state_code_0 = self.env.ref('to_attendance_device.attendance_device_state_code_0')
        if attendance_device_state_code_0:
            att_state_ids += attendance_device_state_code_0
        attendance_device_state_code_1 = self.env.ref('to_attendance_device.attendance_device_state_code_1')
        if attendance_device_state_code_1:
            att_state_ids += attendance_device_state_code_1

        # Overtime Working Attendance
        attendance_device_state_code_4 = self.env.ref('to_attendance_device.attendance_device_state_code_4')
        if attendance_device_state_code_4:
            att_state_ids += attendance_device_state_code_4
        attendance_device_state_code_5 = self.env.ref('to_attendance_device.attendance_device_state_code_5')
        if attendance_device_state_code_5:
            att_state_ids += attendance_device_state_code_5
        return att_state_ids

    @api.model
    def _get_default_attendance_device_state_lines(self):
        attendance_device_state_line_data = []
        for state in self._get_default_attendance_states():
            attendance_device_state_line_data.append(
                (0, 0, {
                    'attendance_state_id': state.id,
                    'code': state.code,
                    'type': state.type,
                    'activity_id': state.activity_id.id
                })
            )
        return attendance_device_state_line_data

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', index=True, copy=False, required=True,)

    name = fields.Char(string="Name", required=True, help='The name of the attendance device',
                        translate=True, copy=True, default='/',
                       readonly=True, states={'draft': [('readonly', False)]})

    firmware_version = fields.Char(string='Firmware Version', readonly=True,
                                   help="The firmware version of the device which will be filled automatically when you hit the 'Get Device Info' button.")
    serialnumber = fields.Char(string='Serial Number', readonly=True,
                               help="The serial number of the device which will be filled automatically when you hit the 'Get Device Info' button.")
    oem_vendor = fields.Char(string='OEM Vendor', readonly=True,
                             help="The OEM Vendor of the device which will be filled automatically when you hit the 'Get Device Info' button.")
    platform = fields.Char(string='Platform', readonly=True,
                           help="The Platform of the device which will be filled automatically when you hit the 'Get Device Info' button.")
    fingerprint_algorithm = fields.Char(string='Fingerprint Algorithm', readonly=True,
                                        help="The Fingerprint Algorithm (aka ZKFPVersion) of the device which will be filled automatically when you hit the 'Get Device Info' button.")
    device_name = fields.Char(string='Device Name', readonly=True,
                              help="The model of the device which will be filled automatically when you hit the 'Get Device Info' button.")

    work_code = fields.Char(string='Work Code', readonly=True,
                            help="The Work Code of the device which will be filled automatically when you hit the 'Get Device Info' button.")

    ip = fields.Char(string="IP / Domain Name", required=True, copy=False, readonly=True,
                     states={'draft': [('readonly', False)]},
                     help='The accessible IP or Domain Name of the device to get device\'s attendance data',
                     default='0.0.0.0')
    port = fields.Integer(string="Port", required=True, default=4370, readonly=True,
                          states={'draft': [('readonly', False)]})
    timeout = fields.Integer(string='Timeout', default=20, required=True, help='Connection Timeout in second',

                             readonly=True, states={'draft': [('readonly', False)]})
    description = fields.Text(string="Description")
    user_id = fields.Many2one('res.users', string="Technician",
                              default=lambda self: self.env.user)
    device_user_ids = fields.One2many('attendance.device.user', 'device_id', string='Device Users',
                                      help='List of Users stored in the attendance device')
    device_users_count = fields.Integer(string='Users Count', compute='_compute_device_users_count', store=True)

    mapped_employee_ids = fields.Many2many('hr.employee', 'mapped_device_employee_rel', string='Mapped Employees',
                                           compute='_compute_employees', store=True,
                                           help="List of employees that have been mapped with this device's users")

    mapped_employees_count = fields.Integer(string='Mapped Employee Count', compute='_compute_mapped_employees_count',
                                            store=True)

    umapped_device_user_ids = fields.One2many('attendance.device.user', 'device_id', string='Device Users',
                                              domain=[('employee_id', '=', False)],
                                              help='List of Device Users that have not been mapped with an employee')

    unmapped_employee_ids = fields.Many2many('hr.employee', 'device_employee_rel', 'device_id', 'employee_id',
                                             compute='_compute_employees', store=True, string='Unmapped Employees',
                                             help="The employees that have not been mapped with any user of this device")

    attendance_device_state_line_ids = fields.One2many('attendance.device.state.line', 'device_id',
                                                       string='State Codes', copy=False,
                                                       default=_get_default_attendance_device_state_lines,
                                                       readonly=True, states={'draft': [('readonly', False)]})
    location_id = fields.Many2one('attendance.device.location', string='Location',
                                  help='The location where the device is located', required=True,
                                  readonly=True, states={'draft': [('readonly', False)]})

    ignore_unknown_code = fields.Boolean(string='Ignore Unknown Code', default=False,
                                         help='Sometimes you don\'t want to load attendance data with status '
                                              'codes those not declared in the table below. In such the case, check this field.',
                                         readonly=True, states={'draft': [('readonly', False)]})

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id,
                                 readonly=True, states={'draft': [('readonly', False)]})

    auto_clear_attendance = fields.Boolean(string='Auto Clear Attendance Data', default=False,
                                           readonly=True, states={'draft': [('readonly', False)]},
                                           help='Check this to clear all device attendance data after download into Odoo')

    auto_clear_attendance_schedule = fields.Selection([
        ('on_download_complete', 'On Download Completion'),
        ('time_scheduled', 'Time Scheduled')], string='Auto Clear Schedule', required=True,
        default='on_download_complete',
        help="On Download Completion: Delete attendance data as soon as download finished\n"
             "Time Scheduled: Delete attendance data on the time specified below")
    auto_clear_attendance_hour = fields.Float(string='Auto Clear At',  required=True,
                                              default=0.0,
                                              help="The time (in the attendance device's timezone) to clear attendance data after download.")

    auto_clear_attendance_dow = fields.Selection([
        ('-1', 'Everyday'),
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday'), ], string='Auto Clear On', default='-1', required=True)

    auto_clear_attendance_error_notif = fields.Boolean(string='Auto Clear Attendance Notif.', default=True,

                                                       help='Notify upon no safe found to clear attendance data')

    tz = fields.Selection('_tz_get', string='Time zone',
                          default=lambda self: self.env.context.get('tz') or self.env.user.tz,

                          required=True, readonly=True, states={'draft': [('readonly', False)]},
                          help="The device's timezone, used to output proper date and time values "
                               "inside attendance reports. It is important to set a value for this field.")

    active = fields.Boolean(string='Active', default=True,  readonly=True,
                            states={'draft': [('readonly', False)]})
    unique_uid = fields.Boolean(string='Unique UID', default=True, required=True,
                                readonly=True, states={'draft': [('readonly', False)]},
                                help='Some Bad Devices allow uid duplication. In this case, uncheck this field. But it is recommended to change your device.')
    last_attendance_download = fields.Datetime(string='Last Sync.', readonly=True,
                                               help='The last time that the attendance data was downlowed from the device into Odoo.')

    map_before_dl = fields.Boolean(string='Map Employee Before Download', default=True,
                                   help='Always try to map users and employees (if any new found) before downloading attendance data.')
    create_employee_during_mapping = fields.Boolean(string='Create Employees During Mapping', default=False,
                                                    help="If checked, during mapping between Device's Users and company's employees, umapped device"
                                                         " users will try to create a new employee then map accordingly.")

    download_error_notification = fields.Boolean(string='Download Error Notification', default=True,
                                                 readonly=True, states={'draft': [('readonly', False)]},
                                                 help='Enable this to get notified when data download error occurs.')
    debug_message = fields.Boolean(string='Debug Message', default=False,
                                   help="If checked, debugging messages will be posted in"
                                        " OpenChatter for debugging purpose")

    user_attendance_ids = fields.One2many('user.attendance', 'device_id', string='Attendance Data', readonly=True)
    total_att_records = fields.Integer(string='Attendance Records', compute='_compute_total_attendance_records')
    finger_template_ids = fields.One2many('finger.template', 'device_id', string='Finger Template', readonly=True)
    total_finger_template_records = fields.Integer(string='Finger Templates',
                                                   compute='_compute_total_finger_template_records')
    protocol = fields.Selection([('udp', 'UDP'), ('tcp', 'TCP')], string='Protocol', required=True, default='tcp',

                                help="Some old devices do not support TCP. In such the case, please try on switching to UDP.")
    omit_ping = fields.Boolean(string='Omit Ping', default=True, help='Omit ping ip address when connecting to device.',
                               readonly=True, states={'draft': [('readonly', False)]})
    password = fields.Char(string='Password', readonly=True, states={'draft': [('readonly', False)]},
                           help="The password to authenticate the device, if required")

    unaccent_user_name = fields.Boolean(string='Unaccent User Name', default=True,
                                        help="Some Devices support Unicode names such as the ZKTeco K50, some others do not."
                                             " In addition to this, the name field on devices is usually limited at about 24 Latin characters"
                                             " or less Unicode characters. Unaccent is sometimes a workaround for long Unicode names")

    zk = None
    zk_cache = {}

    _sql_constraints = [
        ('ip_and_port_unique',
         'UNIQUE(ip, port, location_id)',
         "You cannot have more than one device with the same ip and port of the same location!"),
    ]

    def _set_zk(self):
        """
        This method return a ZK object.
        If an object corresponding to the connection param was created
        and available in self.zk_cache, it will be return. To avoid it, call it with .with_context(no_zk_cache=True)        
        """
        self.ensure_one()
        force_udp = self.protocol == 'udp'
        password = self.password or 0
        cached_key = self.protocol + str(self.omit_ping) + str(self.timeout) + str(password)
        if self.ip:
            cached_key += self.ip
        if self.port:
            cached_key += str(self.port)

        if not cached_key in self.zk_cache.keys() or self.env.context.get('no_zk_cache', False):
            self.zk_cache[cached_key] = ZK(self.ip, self.port, self.timeout, password=password, force_udp=force_udp,
                                           ommit_ping=self.omit_ping)

        self.zk = self.zk_cache[cached_key]

    @api.model
    def _tz_get(self):
        return [(x, x) for x in pytz.all_timezones]

    @api.onchange('location_id')
    def _onchange_location_id(self):
        if self.location_id and self.location_id.tz:
            self.tz = self.location_id.tz

    def name_get(self):
        """
        name_get that supports displaying location name and model as prefix
        """
        result = []
        for r in self:
            name = r.name
            if r.oem_vendor:
                if r.device_name:
                    name = '[' + r.oem_vendor + ' ' + r.device_name + '] ' + name
                else:
                    name = '[' + r.oem_vendor + '] ' + name

            if r.location_id:
                name = '[' + r.location_id.name + '] ' + name

            result.append((r.id, name))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        """
        name search that supports searching by tag code
        """
        args = args or []
        domain = []
        if name:
            domain = ['|', ('location_id.name', '=ilike', name + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&'] + domain
        state = self.search(domain + args, limit=limit)
        return state.name_get()

    @api.depends('device_user_ids', 'device_user_ids.active')
    def _compute_device_users_count(self):
        total_att_data = self.env['attendance.device.user'].read_group([('device_id', 'in', self.ids)], ['device_id'],
                                                                       ['device_id'])
        mapped_data = dict([(dict_data['device_id'][0], dict_data['device_id_count']) for dict_data in total_att_data])
        for r in self:
            r.device_users_count = mapped_data.get(r.id, 0)

    def _compute_total_finger_template_records(self):
        total_att_data = self.env['finger.template'].read_group([('device_id', 'in', self.ids)], ['device_id'],
                                                                ['device_id'])
        mapped_data = dict([(dict_data['device_id'][0], dict_data['device_id_count']) for dict_data in total_att_data])
        for r in self:
            r.total_finger_template_records = mapped_data.get(r.id, 0)

    def _compute_total_attendance_records(self):
        total_att_data = self.env['user.attendance'].read_group([('device_id', 'in', self.ids)], ['device_id'],
                                                                ['device_id'])
        mapped_data = dict([(dict_data['device_id'][0], dict_data['device_id_count']) for dict_data in total_att_data])
        for r in self:
            r.total_att_records = mapped_data.get(r.id, 0)

    @api.depends('device_user_ids', 'device_user_ids.active', 'device_user_ids.employee_id',
                 'device_user_ids.employee_id.active')
    def _compute_employees(self):
        HrEmployee = self.env['hr.employee']
        for r in self:
            r.update({
                'unmapped_employee_ids': [
                    (6, 0, HrEmployee.search([('id', 'not in', r.device_user_ids.mapped('employee_id').ids)]).ids)],
                'mapped_employee_ids': [(6, 0, r.device_user_ids.mapped('employee_id').filtered(
                    lambda employee: employee.active == True).ids)],
            })

    @api.depends('mapped_employee_ids')
    def _compute_mapped_employees_count(self):
        for r in self:
            r.mapped_employees_count = len(r.mapped_employee_ids)

    @api.onchange('unique_uid')
    def onchange_unique_uid(self):
        if not self.unique_uid:
            message = _('This is for experiment to check if the device contains bad data with non-unique user\'s uid.'
                        ' Turn this option off will allow mapping device user\'s user_id with user\'s user_id in Odoo.\n'
                        'NOTE:\n'
                        '- non-latin user_id are not supportted.\n'
                        '- Do not turn this option off in production.')
            return {
                'warning': {
                    'title': "Warning!",
                    'message': message,
                },
            }

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'ip' in vals:
                vals['ip'] = vals['ip'].strip()
        return super(AttendanceDevice, self).create(vals_list)

    def write(self, vals):
        if 'ip' in vals:
            vals['ip'] = vals['ip'].strip()
        return super(AttendanceDevice, self).write(vals)

    def connect(self):
        self.ensure_one()

        def post_message():
            email_template_id = self.env.ref('to_attendance_device.email_template_attendance_device')
            self.post_message(email_template_id)
            self.env.cr.commit()

        error_msg = False
        try:
            self._set_zk()
            return self.zk.connect()
        except ZKNetworkError as e:
            error_msg = _("Could not reach the device %s (ping %s)") % (self.display_name, self.ip)
        except ZKConnectionUnauthorized as e:
            error_msg = _("Connection Unauthorized! The device %s may require password") % self.display_name
        except ZKErrorResponse as e:
            error_msg = _("Could not get connected to the device %s. This is usually due to either the network error or"
                          " wrong protocol selection or password authentication is required.\n"
                          "Debugging info:\n%s") % (self.display_name, e)
        except Exception as e:
            error_msg = _("Could not get connected to the device '%s'. Please check your network"
                          " configuration and device password and/or hard restart your device") % (self.display_name,)

        if error_msg:
            post_message()
            raise ValidationError(error_msg)

    def disconnect(self):
        try:
            return self.zk.disconnect()
        except Exception as e:
            _logger.error(e)
            raise ValidationError(_("Could not get the device %s disconnected. Here is the debugging information:\n%s")
                                  % (self.display_name, e))

    def disableDevice(self):
        """
        disable (lock) device, ensure no activity when process run
        """
        try:
            return self.zk.disable_device()
        except Exception as e:
            _logger.error(e)
            raise ValidationError(_("Could not get the device %s disabled. Here is the debugging information:\n%s")
                                  % (self.display_name, e))

    def action_restart(self):
        self.ensure_one()
        self.restartDevice()

    def enableDevice(self):
        """
        re-enable the connected device
        """
        try:
            return self.zk.enable_device()
        except Exception as e:
            _logger.error(e)
            raise ValidationError(_('Could not get the device %s enabled. Here is the debugging information:\n%s')
                                  % (self.display_name, e))

    def getFirmwareVersion(self):
        '''
        return the firmware version
        '''
        try:
            self.connect()
            self.enableDevice()
            return self.zk.get_firmware_version()
        except Exception as e:
            _logger.error(e)
            raise ValidationError(
                _("Could not get the firmware version of the device %s. Here is the debugging information:\n%s")
                % (self.display_name, e))
        finally:
            self.disconnect()

    def getSerialNumber(self):
        '''
        return the serial number
        '''
        try:
            self.connect()
            self.enableDevice()
            return self.zk.get_serialnumber()
        except Exception as e:
            _logger.error(e)
            raise ValidationError(
                _("Could not get the serial number of the device %s. Here is the debugging information:\n%s")
                % (self.display_name, e))
        finally:
            self.disconnect()

    def getOEMVendor(self):
        '''
        return the serial number
        '''
        try:
            self.connect()
            self.enableDevice()
            return self.zk.get_oem_vendor()
        except Exception as e:
            _logger.error(e)
            raise ValidationError(
                _('Could not get the OEM Vendor of the device %s. Here is the debugging information:\n%s')
                % (self.display_name, e))
        finally:
            self.disconnect()

    def getFingerprintAlgorithm(self):
        '''
        return the Fingerprint Algorithm
        '''
        try:
            self.connect()
            self.enableDevice()
            return self.zk.get_fp_version()
        except Exception as e:
            _logger.error(e)
            raise ValidationError(
                _('Could not get the Fingerprint Algorithm of the device %s. Here is the debugging information:\n%s')
                % (self.display_name, e))
        finally:
            self.disconnect()

    def getPlatform(self):
        '''
        return the serial number
        '''
        try:
            self.connect()
            self.enableDevice()
            return self.zk.get_platform()
        except Exception as e:
            _logger.error(e)
            raise ValidationError(
                _('Could not get the Platform of the device %s. Here is the debugging information:\n%s')
                % (self.display_name, e))
        finally:
            self.disconnect()

    def getDeviceName(self):
        '''
        return the serial number
        '''
        try:
            self.connect()
            self.enableDevice()
            return self.zk.get_device_name()
        except Exception as e:
            _logger.error(e)
            raise ValidationError(_('Could not get the Name of the device %s. Here is the debugging information:\n%s')
                                  % (self.display_name, e))
        finally:
            self.disconnect()

    def getWorkCode(self):
        '''
        return the serial number
        '''
        try:
            self.connect()
            self.enableDevice()
            return self.zk.get_workcode()
        except Exception as e:
            _logger.error(e)
            raise ValidationError(
                _('Could not get the Work Code of the device %s. Here is the debugging information:\n%s')
                % (self.display_name, e))
        finally:
            self.disconnect()

    def restartDevice(self):
        '''
        restart the device
        '''
        try:
            self.connect()
            self.enableDevice()
            return self.zk.restart()
        except Exception as e:
            _logger.error(e)
            raise ValidationError(
                _('Could not get the serial number of the device %s. Here is the debugging information:\n%s')
                % (self.display_name, e))

    def setUser(self, uid=None, name='', privilege=0, password='', group_id='', user_id='', card=0):
        try:
            self.connect()
            self.enableDevice()
            self.disableDevice()
            return self.zk.set_user(uid, name, privilege, password, group_id, user_id, card)
        except Exception as e:
            _logger.info(e)
            raise ValidationError(_('Could not set user into the device %s. Here is the user information:\n'
                                    'uid: %s\n'
                                    'name: %s\n'
                                    'privilege: %s\n'
                                    'password: %s\n'
                                    'group_id: %s\n'
                                    'user_id: %s\n'
                                    'Here is the debugging information:\n%s')
                                  % (self.display_name, uid, name, privilege, password, group_id, user_id, e))
        finally:
            self.enableDevice()
            self.disconnect()

    def delUser(self, uid, user_id):
        '''
        delete specific user by uid
        '''
        try:
            self.connect()
            self.enableDevice()
            self.disableDevice()
            return self.zk.delete_user(uid, user_id)
        except Exception as e:
            _logger.error(e)
            raise ValidationError(_('Could not delete the user with uid "%s", user_id "%s" from the device %s\n%s')
                                  % (uid, user_id, self.display_name, e))
        finally:
            self.enableDevice()
            self.disconnect()

    def action_clear_data(self):
        '''
        clear all data (include: user, attendance report, finger database )
        '''
        try:
            self.connect()
            self.enableDevice()
            self.disableDevice()
            return self.zk.clear_data()
        except Exception as e:
            _logger.error(e)
            raise ValidationError(_('Could not clear data from the device %s. Here is the debugging information:\n%s')
                                  % (self.display_name, e))
        finally:
            self.enableDevice()
            self.disconnect()

    def getUser(self):
        '''
        return a Python List of device users in User(uid, name, privilege, password, group_id, user_id)
        '''
        try:
            self.connect()
            self.enableDevice()
            self.disableDevice()
            return self.zk.get_users()
        except Exception as e:
            _logger.error(str(e))
            raise ValidationError(_('Could not get users from the device %s\n'
                                    'If you had connected to your device, perhaps your device had problem. '
                                    'Some bad devices allowed duplicated uid may cause such problem. In such case, '
                                    'if you still want to load users from that bad device, please uncheck Data '
                                    'Acknowledge field.\n'
                                    'Here is the debugging error message:\n%s') % (self.display_name, str(e)))
        finally:
            self.enableDevice()
            self.disconnect()

    def upload_finger_templates(self, uid, name, privilege, password, group_id, user_id, fingers):
        user = User(uid, name, privilege, password, group_id, user_id, card=0)
        try:
            self.connect()
            self.enableDevice()
            self.disableDevice()
            return self.zk.save_user_template(user, fingers)
        except Exception as e:
            _logger.error(e)
            raise ValidationError(_("Could not set finger template into the device %s. Here are the information:\n"
                                    "user_id: %s\n"
                                    "Debugging information:\n%s")
                                  % (self.display_name, user_id, e))
        finally:
            self.enableDevice()
            self.disconnect()

    def delFingerTemplate(self, uid, fid, user_id):
        '''
        delete finger template by uid and fid
        '''
        try:
            self.connect()
            self.enableDevice()
            self.disableDevice()
            return self.zk.delete_user_template(uid, fid, user_id)
        except Exception as e:
            _logger.error(e)
            raise ValidationError(_('Could not delete finger template with fid "%s" of uid "%s" from the device %s') % (
            fid, uid, self.display_name,))
        finally:
            self.enableDevice()
            self.disconnect()

    def getFingerTemplate(self):
        '''
        return a Python List of fingers template in Finger(uid, fid, valid, template)
        '''
        try:
            self.connect()
            self.enableDevice()
            self.disableDevice()
            return self.zk.get_templates()
        except Exception as e:
            _logger.error(str(e))
            raise ValidationError(_('Could not get finger templates from the device %s\n'
                                    'If you had connected to your device, perhaps your device had problem. '
                                    'Some bad devices allowed duplicated uid may cause such problem. In such case, '
                                    'if you still want to load users from that bad device, please uncheck Data '
                                    'Acknowledge field.\n'
                                    'Here is the debugging error message:\n%s') % (self.display_name, str(e)))
        finally:
            self.enableDevice()
            self.disconnect()

    def get_next_uid(self):
        '''
        return max uid of users on attendance device
        '''
        try:
            self.connect()
            self.enableDevice()
            self.disableDevice()
            return self.zk.get_next_uid()
        except Exception as e:
            _logger.error(str(e))
            raise ValidationError(_('Could not get max uid from the device %s\n'
                                    'If you had connected to your device, perhaps your device had problem.\n'
                                    'Here is the debugging error message:\n%s') % (self.display_name, str(e)))
        finally:
            self.enableDevice()
            self.disconnect()

    def getMachineTime(self):
        try:
            self.connect()
            self.enableDevice()
            return self.zk.get_time()
        except Exception as e:
            _logger.error(str(e))
            raise ValidationError(_("Could not get time from the device %s\n"
                                    "Here is the debugging error message:\n%s") % (self.display_name, str(e)))
        finally:
            self.disconnect()

    def clearData(self):
        '''
        clear all data (include: user, attendance report, finger database )
        '''
        try:
            self.connect()
            self.enableDevice()
            return self.zk.clear_data()
        except Exception:
            raise ValidationError(_('Could not clear all data from the device %s') % (self.display_name,))
        finally:
            self.enableDevice()
            self.disconnect()

    def getAttendance(self):
        post_err_msg = False
        try:
            self.connect()
            self.enableDevice()
            self.disableDevice()
            return self.zk.get_attendance()

        except Exception as e:
            _logger.error(str(e))
            post_err_msg = True
            raise ValidationError(_('Could not get attendance data from the device %s') % (self.display_name,))

        finally:
            if post_err_msg and self.download_error_notification:
                email_template_id = self.env.ref('to_attendance_device.email_template_error_get_attendance')
                self.post_message(email_template_id)
            self.enableDevice()
            self.disconnect()

    def clearAttendance(self):
        '''
        clear all attendance records from the device
        '''
        try:
            self.connect()
            self.enableDevice()
            self.disableDevice()
            return self.zk.clear_attendance()
        except Exception:
            raise ValidationError(_('Could not get attendance data from the device %s') % (self.display_name,))
        finally:
            self.enableDevice()
            self.disconnect()

    def _download_users_by_uid(self):
        """
        This method download and update all device users into model attendance.device.user using uid as key
        """
        DeviceUser = self.env['attendance.device.user']
        for r in self:
            error_msg = ""
            # device_users = User(uid, name, privilege, password, group_id, user_id)
            device_users = r.getUser()

            uids = []
            for device_user in device_users:
                uids.append(device_user.uid)

            existing_user_ids = []

            device_user_ids = DeviceUser.with_context(active_test=False).search([('device_id', '=', r.id)])
            for user in device_user_ids.filtered(lambda user: user.uid in uids):
                existing_user_ids.append(user.uid)

            users_not_in_device = device_user_ids.filtered(lambda user: user.uid not in existing_user_ids)
            users_not_in_device.write({'not_in_device': True})

            for device_user in device_users:
                uid = device_user.uid
                vals = {
                    'uid': uid,
                    'name': device_user.name,
                    'privilege': device_user.privilege,
                    'password': device_user.password,
                    'user_id': device_user.user_id,
                    'device_id': r.id,
                }
                if device_user.group_id.isdigit():
                    vals['group_id'] = device_user.group_id
                if uid not in existing_user_ids:
                    try:

                        DeviceUser.create(vals)
                    except Exception as e:
                        _logger.info(e)
                        _logger.info(vals)
                        error_msg += str(e)
                        error_msg += _("\nData that caused the error: %s") % str(vals)
                else:
                    existing = DeviceUser.with_context(active_test=False).search(
                        [('uid', '=', uid), ('device_id', '=', r.id)], limit=1)
                    if existing:
                        update_data = {}
                        if existing.name != vals['name']:
                            update_data['name'] = vals['name']
                        if existing.privilege != vals['privilege']:
                            update_data['privilege'] = vals['privilege']
                        if existing.password != vals['password']:
                            update_data['password'] = vals['password']
                        if 'group_id' in vals and existing.group_id != vals['group_id']:
                            update_data['group_id'] = vals['group_id']
                        if existing.user_id != vals['user_id']:
                            update_data['user_id'] = vals['user_id']
                        if existing.device_id.id != vals['device_id']:
                            update_data['device_id'] = vals['device_id']
                        if bool(update_data):
                            try:
                                existing.write(update_data)
                            except Exception as e:
                                _logger.info(e)
                                _logger.info(vals)
                                error_msg += str(e) + "<br />"
                                error_msg += _("\nData that caused the error: %s") % str(update_data)
            if error_msg and r.debug_message:
                r.message_post(body=error_msg)

    def _download_users_by_user_id(self):
        """
        This method download and update all device users into model attendance.device.user using user_id as key
        NOTE: This method is experimental as it failed on comparing user_id in unicode type from devices (unicode: string) with user_id in unicode string from Odoo (u'string')
        """
        DeviceUser = self.env['attendance.device.user']
        for r in self:
            # device_users = User(uid, name, privilege, password, group_id, user_id)
            device_users = r.getUser()

            user_ids = []
            for device_user in device_users:
                user_ids.append(str(device_user.user_id))

            existing_user_ids = []
            device_user_ids = DeviceUser.with_context(active_test=False).search([('device_id', '=', r.id)])
            for user in device_user_ids.filtered(lambda user: user.user_id in user_ids):
                existing_user_ids.append(str(user.user_id))

            for device_user in device_users:
                user_id = str(device_user.user_id)
                vals = {
                    'uid': device_user.uid,
                    'name': device_user.name,
                    'privilege': device_user.privilege,
                    'password': device_user.password,
                    'user_id': device_user.user_id,
                    'device_id': r.id,
                }
                if device_user.group_id.isdigit():
                    vals['group_id'] = device_user.group_id
                if user_id not in existing_user_ids:
                    DeviceUser.create(vals)
                else:
                    existing = DeviceUser.with_context(active_test=False).search([
                        ('user_id', '=', user_id),
                        ('device_id', '=', r.id)], limit=1)
                    if existing:
                        existing.write(vals)

    def action_show_time(self):
        """
        Show the time on the machine
        """
        self.ensure_one()
        raise ValidationError(_("The Machine time is %s") % self.getMachineTime())

    def action_user_download(self):
        """
        This method download and update all device users into model attendance.device.user
        """
        for r in self:
            if r.unique_uid:
                r._download_users_by_uid()
            else:
                r._download_users_by_user_id()

    def action_user_upload(self):
        """
        This method will
        1. Download users from device
        2. Map the users with emloyee
        3. Upload users from model attendance.device.user into the device
        """
        ignored_employees_dict = {}
        for r in self:
            # Then we download and map all employees with users
            r.action_employee_map()
            # Then we create users from unmapped employee
            ignored_employees = []
            for employee in r.unmapped_employee_ids:
                if not employee.barcode:
                    ignored_employees.append(employee)
                    continue
                employee.action_load_to_attendance_device(r)
            # we download and map all employees with users again
            r.action_employee_map()

            if len(ignored_employees) > 0:
                ignored_employees_dict[r] = ignored_employees

        if not bool(ignored_employees_dict):
            message = _(
                'The following employees, who have no Badge ID defined, have not been uploaded to the corresponding device:\n')
            for device in ignored_employees_dict.keys():
                for employee in ignored_employees_dict[device]:
                    message += device.name + ': ' + employee.name + '\n'

            return {
                'warning': {
                    'title': "Some Employees could not be uploaded!",
                    'message': message,
                },
            }

    def action_employee_map(self):
        self.action_user_download()

        for r in self:
            for user in r.device_user_ids.filtered(lambda user: not user.employee_id):
                employee = user.smart_find_employee()
                if employee:
                    user.write({
                        'employee_id': employee.id,
                    })
            # upload users that are available in Odoo but not available in device
            for user in r.device_user_ids.filtered(lambda user: user.not_in_device):
                user.setUser()
                user.write({'not_in_device': False})

            # upload users that are available in Odoo but not available in device
            for user in r.device_user_ids.filtered(lambda user: user.not_in_device):
                user.setUser()
                user.write({'not_in_device': False})
            if r.create_employee_during_mapping:
                for user in r.device_user_ids.filtered(lambda user: not user.employee_id):
                    user.create_employee()

    def action_attendance_download(self):
        DeviceUserAttendance = self.env['user.attendance']
        AttendanceUser = self.env['attendance.device.user']
        att_obj = self.env['hr.attendance']


        for r in self:
            error_msg = ""
            if r.map_before_dl:
                r.action_finger_template_download()

            attendance_states = {}
            for state_line in r.attendance_device_state_line_ids:
                attendance_states[state_line.attendance_state_id.code] = state_line.attendance_state_id.id
            sss=0
            attendance_data = r.getAttendance()
            for attendance in attendance_data:
                sss=sss+1

                print("attendanceattendance",attendance)
                if attendance.punch not in attendance_states.keys():
                    if not r.ignore_unknown_code:
                        raise UserError(_('We found attendance status code "%s" from your device %s '
                                          'but no such code found in the device\'s settings in Odoo. '
                                          'Please go to the device %s and add this attendance code.\n'
                                          'In case you want to ignore to load attendance data with this code, '
                                          ' go to the device setting in Odoo and check "Ignore Unknown Code".')
                                        % (attendance.punch, r.display_name, r.display_name))
                    else:
                        continue

                user_id = AttendanceUser.with_context(active_test=False).search([
                    ('user_id', '=', attendance.user_id),
                    ('device_id', '=', r.id)], limit=1)
                if user_id:
                    utc_timestamp = attendance.timestamp
                    print("utc_timestamputc_timestamp",utc_timestamp)

                    duplicate_attend = DeviceUserAttendance.search([
                        ('device_id', '=', r.id),
                        ('user_id', '=', user_id.id),
                        ('timestamp', '=', utc_timestamp)], limit=1)

                    if not duplicate_attend:
                        try:

                            vals = {
                                'device_id': r.id,
                                'user_id': user_id.id,
                                'timestamp': utc_timestamp,
                                'status': attendance.punch,
                                'attendance_state_id': attendance_states[attendance.punch]
                            }


                            s=DeviceUserAttendance.sudo().create(vals)
                            # ss=att_obj.sudo().create({'employee_id': r.id,
                            #                 'check_in': utc_timestamp})
                            # print("ssssss",ss)

                            

                        except Exception as e:
                            error_msg += str(e) + "<br />"
                            error_msg += _(
                                "Error create DeviceUserAttendance record: device_id %s; user_id %s; timestamp %s; attendance_state_id %s.<br />") % (
                                             r.id,
                                             user_id.id,
                                             format_tz(r.env, attendance.timestamp, r.tz),
                                             attendance_states[attendance.punch]
                                         )
                            _logger.error(error_msg)
                            pass
            r.last_attendance_download = fields.Datetime.now()
            if error_msg and r.debug_message:
                r.message_post(body=error_msg)

            if not r.auto_clear_attendance:
                continue

            if r.auto_clear_attendance_schedule == 'on_download_complete':
                r.action_attendance_clear()
            elif r.auto_clear_attendance_schedule == 'time_scheduled':
                # datetime in the timezone of the device
                dt_now = self.convert_utc_time_to_tz(datetime.utcnow(), r.tz)
                float_dt_now = self.time_to_float_hour(dt_now)

                if r.auto_clear_attendance_dow == '-1' or str(dt_now.weekday()) == r.auto_clear_attendance_dow:
                    delta = r.auto_clear_attendance_hour - float_dt_now
                    if abs(delta) <= 0.5 or abs(delta) >= 23.5:
                        r.action_attendance_clear()

    def action_finger_template_download(self):
        FingerTemplate = self.env['finger.template']
        for r in self:
            print("rrrrrr",r)
            r.action_employee_map()
            print("rrrrrr",r)

            template_data = r.getFingerTemplate()
            template_datas = []
            for template in template_data:
                template_datas.append(str(template.uid) + '_' + str(template.fid))

            existing_finger_template_ids = []
            finger_template_ids = FingerTemplate.search([('device_id', '=', r.id)])
            for template in finger_template_ids.filtered(
                    lambda tmp: (str(tmp.uid) + '_' + str(tmp.fid)) in template_datas):
                existing_finger_template_ids.append(str(template.uid) + '_' + str(template.fid))

            for template in template_data:
                uid = template.uid
                fid = template.fid
                valid = template.valid
                tmp = template.template
                # hkdf = HKDF(
                # algorithm = 10,
                # length = 32,
                # salt = None,
                # info = None,
                # backend = default_backend()
                #     )
                print(tmp)
                # result = list(format(c, 'b') for c in bytearray(tmp, "utf-8"))
                # print("temmmmmmmm1", result)
                # tmp1= b''.join(format(x, 'b') for x in bytearray(tmp, 'utf-8'))
                tmp1=binascii.hexlify(tmp)
                # for i in reversed(range(int(len(binascii.hexlify(tmp)) / 2))):
                #     tmp1 += binascii.hexlify(tmp).decode('utf-8')[i * 2:(i * 2) + 2]
                # tmp=io.BytesIO(tmp)
                    # '01100010 00100010 01001011 01011100 01111000 01100110 01100010 01010011 01010011 00110010 00110001 01011100 01111000 00110000 00110000 01011100 01111000 00110000 00110000 01011100 01111000 00110000 00110010 01011100 01111000 01100010 00111000 01011100 01111000 01100010 01100001 01011100 01111000 00110000 00110100 01011100 01111000 00110000 00111000 01011100 01111000 00110000 00110101 01011100 01111000 00110000 00110111 01011100 01110100 01011100 01111000 01100011 01100101 01011100 01111000 01100100 00110000 01011100 01111000 00110000 00110000 01011100 01111000 00110000 00110000 01011100 01111000 00110001 01100001 01011100 01111000 01100010 00111001 01101001 01011100 01111000 00110000 00110001 01011100 01111000 00110000 00110000 01011100 01111000 00110000 00110000 01011100 01111000 00110000 00110000 01011100 01111000 00111000 00110010 01100101 01011100 01111000 00110001 00110100 01110010 01011100 01111000 01100010 00111000 01011100 01111000 00111000 00110010 01011100 01111000 00110000 00110000 01011100 01011100 01011100 01111000 00110000 01100110 01011100 01111000 00111001 00110101 01011100 01111000 00110000 00110000 01011101 01011100 01111000 00110000 00110000 01010100 01011100 01111000 01100010 00110111 01011100 01111000 01100101 00111001 01011100 01111000 00110000 00110000 01011100 01111000 00111001 00111000 01011100 01111000 00110000 00110000 00101010 01011100 01111000 00110000 01100110 01011011 01011100 01111000 00110000 00110000 01011100 01111000 01100011 00110001 01011100 01111000 01100010 00111000 00111111 01011100 01111000 00110000 01100110 01111101 01011100 01111000 00110000 00110000 01011100 01111000 01100011 01100010 01011100 01111000 00110000 00110000 01011100 01111000 00111000 00110100 01011100 01111000 00110000 01100110 01011100 01111000 01100001 00111001 01011100 01111000 01100010 00111000 01011100 01111000 01100011 01100001 01011100 01111000 00110000 00110000 00111010 01011100 01111000 00110000 01100110 01011100 01111000 00110000 01100011 01011100 01111000 00110000 00110001 01011100 01111000 00110001 00110000 01011100 01111000 00110000 00110000 00111101 01011100 01111000 01100010 00110111 01011100 01111000 01100001 00110001 01011100 01111000 00110000 00110000 01011100 01111000 01100101 00110111 01011100 01111000 00110000 00110000 01011100 01111000 01100010 01100101 01011100 01111000 00110000 01100110 01010000 01011100 01111000 00110000 00110000 01011100 01111000 01100101 00111000 01011100 01111000 01100010 00111000 00111001 01011100 01111000 00110000 01100110 01010110 01011100 01111000 00110000 00110000 01011100 01111000 01100101 01100110 01011100 01111000 00110000 00110000 01011100 01111000 01100110 01100010 01011100 01111000 00110000 01100110 01011100 01111000 01100110 00110001 01011100 01111000 01100010 00111000 01011100 01111000 01100110 00110011 01011100 01111000 00110000 00110000 01011100 01111000 01100011 00110000 01011100 01110010 01011100 01111000 01100101 00111001 01011100 01111000 00110000 00110000 00111101 01011100 01111000 00110000 00110000 00110010 01011100 01111000 01100010 00110101 01011100 01111000 01100101 00111001 01011100 01111000 00110000 00110000 01011100 01111000 00110000 00110011 01011100 01111000 00110000 00110001 00100100 01011100 01110010 01011100 01111000 01100001 01100010 01011100 01111000 00110000 00110000 01011100 01111000 00110000 01100010 01011100 01111000 01100010 00111001 00110110 01011100 01111000 00110000 01100110 01011100 01111000 01100100 00110110 01011100 01111000 00110000 00110000 01011100 01110100 01011100 01111000 00110000 00110001 01011100 01111000 01100110 00110100 01011100 01111000 00110000 01100101 01011100 01111000 01100011 01100011 01011100 01111000 01100010 00111000 01011100 01111000 00110000 01100011 01011100 01111000 00110000 00110001 01011100 01111000 01100010 01100101 01011100 01111000 00110000 01100101 01011100 01111000 00110000 00110001 01011100 01111000 00110000 00110001 01011100 01111000 01100100 01100011 01011100 01111000 00110000 00110001 00100001 01011100 01111000 01100010 00110111 01011100 01111000 01100100 01100110 01011100 01111000 00110000 00110000 01011100 01111000 00110001 01100010 01011100 01111000 00110000 00110001 01011100 01111000 01100010 00110000 01011100 01111000 00110000 01100101 01011100 01111000 00110111 01100110 01011100 01111000 00110000 00110000 00100100 01011100 01111000 01100010 00111001 00101001 01011100 01111000 00110000 01100101 01011100 01111000 01100001 01100110 01011100 01111000 00110000 00110000 00110000 01011100 01111000 00110000 00110001 01110101 01011100 01111000 00110000 01100110 00111000 01011100 01111000 01100010 00110011 01011110 01011100 01111000 00110001 01100110 01001111 00100011 01011100 01111000 01100011 00110010 01011100 01111000 01100110 01100110 01011100 01111000 01100001 00110111 01011100 01111000 00110001 01100010 01011001 01011100 01111000 01100001 00110110 01011100 01111000 00111000 00110010 01011100 01111000 01100101 01100110 01011100 01111000 01100010 01100010 01011100 01111000 01100110 00110011 01011100 01111000 01100100 01100010 01011100 01111000 01100100 00110111 01011100 01111000 00111001 01100011 01011100 01111000 00110000 00110100 01011100 01111000 01100010 00111000 01000101 01011100 01111000 00111000 00110011 01011100 01111000 00111000 00110001 00110110 01011100 01111000 00110000 00110101 01100110 01011100 01101110 01011100 01111000 00111001 01100010 01011100 01111000 00111000 00110111 01011100 01111000 01100100 01100110 01000100 01011100 01111000 00111001 00110111 01111100 01011100 01111000 01100001 00110010 01011100 01111000 00110000 00110110 01011100 01111000 01100001 00110010 01011100 01111000 00111000 00110010 01100110 01011100 01111000 00110001 00110000 01011100 01111000 00111001 01100100 01011100 01111000 01100001 00110111 00111001 01011100 01111000 00111000 01100010 01011100 01111000 00111001 00110010 01011100 01111000 00111000 00110100 01011100 01111000 00111000 00110010 01011100 01111000 00111000 00110001 01011100 01111000 01100110 00111001 01011100 01111000 00110111 01100110 00100000 01011100 01111000 01100010 01100001 01011100 01111000 01100101 01100110 01011100 01111000 01100110 01100001 01100110 01011100 01110100 00100111 01011100 01111000 01100110 01100100 01011100 01111000 00111000 00110110 01011100 01111000 00110000 01100010 00101110 00101011 01011100 01111000 00110001 00111000 01011100 01111000 00111001 01100100 00100110 01011100 01111000 00111001 00110001 01011100 01111000 00111001 00110100 01011100 01111000 00110000 01100110 01011100 01111000 01100110 00111001 01110011 01011100 01111000 01100010 00110111 01011100 01111000 01100010 01100001 00100001 01011100 01111000 01100110 00110111 01011100 01111000 01100100 00110001 01011100 01111000 01100110 00110101 00110101 01100101 00101011 01011100 01111000 01100110 00111001 00101101 01011100 01111000 01100010 00111001 00110010 01111011 01011100 01111000 01100010 01100011 01110110 01000101 01011100 01110010 01000100 01011100 01111000 00111000 00110001 01011100 01111000 01100010 00110010 00110110 01011100 01111000 01100101 00110000 01011100 01111000 00110001 00110001 01011100 01111000 01100010 00110101 01011100 01111000 00111001 01100110 01011100 01111000 01100110 01100101 01011100 01111000 00110000 00110000 01011100 01111000 00110001 01100010 01110101 01011100 01111000 00110000 00110100 01001110 01011100 01111000 00111000 00110000 01011100 01111000 00111000 00110001 01101101 01011100 01111000 01100110 00110101 01011100 01111000 01100001 00110001 01011100 01111000 00111000 01100110 01111000 01111000 00110100 01011100 01111000 01100100 00110100 01001111 01111010 01011100 01111000 01100010 00110101 01011100 01111000 00111000 00111000 01011100 01111000 01100001 01100110 01011100 01111000 01100110 00110100 01011100 01111000 00110000 00110110 01011100 01111000 00110000 00110001 01000000 01011100 01111000 01100011 00110110 01011100 01111000 00110000 00111000 00100000 00100111 01011100 01111000 00110000 00110001 01011100 01111000 00110000 00110001 01011100 01111000 01100001 00110111 01011100 01111000 01100100 00110011 01011000 01011100 01111000 00110000 00110001 01011100 01111000 01100010 00111000 01100110 01010101 01100100 01011100 01111000 01100011 00110001 01011100 01111000 00110000 00110110 01011100 01111000 00110000 00110000 01000111 01011000 01110110 00110011 01011100 01111000 01100011 00110000 01011100 01110100 01011100 01111000 00110000 00110000 01011100 01111000 00111000 00111000 01011110 01110111 01010001 01011100 01111000 01100011 00110010 01011100 01111000 01100011 00110011 01011100 01111000 01100011 01100101 01011100 01111000 00110001 00110010 01011100 01111000 00110000 00110000 01011100 01111000 01100001 01100011 01100001 01110000 01001110 01011100 01111000 00110000 00110111 01101110 01011100 01111000 01100011 00110000 01111010 01000100 01111000 01011100 01111000 01100011 00110010 01011100 01111000 01100110 01100101 01011100 01111000 00110000 01100011 01011100 01111000 00110000 00110000 01001000 01100011 01110011 01111001 01011100 01111000 01100011 00110000 01011100 01111000 00111000 00110000 01011001 01110111 01011100 01110100 01011100 01111000 00110000 00110000 01011100 01111000 00110000 00110111 01100100 01011100 01111000 00110000 01100101 01111000 01011100 01111000 01100110 01100110 01011100 01111000 01100011 00110001 00101011 01011100 01111000 01100110 01100011 01011100 01111000 00110001 00110110 01011100 01111000 00110000 00110000 01101011 01101011 01111000 00111011 01011100 01111000 01100011 00110011 01011100 01111000 01100011 00110010 01110000 01101111 01011001 01111000 01011100 01111000 00110000 00110101 01011100 01111000 00111001 01100010 01011100 01111000 00110000 00110110 01011100 01111000 01100010 00111000 01011100 01111000 01100110 00110010 01101011 01011100 01111000 00110001 01100011 01001001 01011100 01101110 01011100 01111000 00110000 00110000 01111110 01101101 01011100 01111000 00110000 00110001 01011100 01111000 00111001 00110011 01011100 01111000 01100110 01100110 01011100 01111000 01100110 01100110 00110101 01011100 01111000 00110001 00110000 01011100 01111000 00110000 00110000 01101101 01000000 01011110 01011100 01111000 01100011 00110000 01111000 01011100 01111000 01100011 00110011 01011001 01011100 01111000 01100011 00110000 01011100 01111000 01100011 00110001 01110000 01101011 01011100 01111000 01100011 00111000 01011100 01111000 00110000 00110000 01011100 01111000 00111001 01100010 00101100 01011100 01111000 01100101 01100001 01011100 01111000 01100110 01100101 01011100 01111000 01100110 01100011 01011100 01111000 01100110 01100100 01011100 01111000 01100110 01100100 01011100 01111000 01100110 01100101 00111011 01011100 01111000 01100110 01100110 01011100 01111000 01100110 01100011 01111001 01011100 01111000 01100110 01100110 01011100 01111000 01100110 01100110 01011100 01111000 00110000 01100110 01011100 01111000 00110000 00110000 01011100 01111000 00111001 00110001 01011100 01111000 00111001 00111000 01011100 01111000 01100001 00110101 01011100 01111000 01100011 00110100 01011100 01111000 01100110 01100100 01111010 01011100 01111000 01100011 00110001 01011100 01111000 00111000 00110111 01011100 01111000 01100011 00110010 01011100 01111000 01100011 00110010 01011100 01111000 01100110 01100110 01011100 01111000 00111000 01100010 01011100 01111000 01100011 01100001 01011100 01111000 00110000 00110000 01011100 01111000 00111001 00110111 00100100 01010110 01011100 01111000 01100011 00110010 01011100 01111000 01100011 00110000 01011100 01111000 01100011 00110100 01011100 01111000 01100011 00110000 01011100 01111000 01100011 00110000 01011100 01111000 01100010 00110100 01101111 01110100 01011100 01111000 01100010 01100101 01011100 01111000 00110000 00110001 01011100 01111000 01100101 01100011 01011100 01111000 00111001 01100011 00100111 01011100 01111000 01100110 01100110 01011100 01111000 01100110 01100101 01011100 01111000 01100110 01100100 01011100 01111000 00110000 01100101 01011100 01111000 00110000 00110010 01011100 01111000 00110000 01100011 01011100 01111000 01100001 00110010 01101001 01011100 01111000 01100011 00110111 01011100 01111000 00111001 00110100 01011100 01111000 01100011 00110000 01101111 01011100 01111000 00110000 00110101 01011100 01111000 01100110 01100110 01011100 01111000 00111001 00110100 01011100 01111000 01100010 00110001 01011100 01111000 00110000 00110001 01011100 01111000 01100010 01100011 01011100 01111000 01100001 00110101 00100000 00101000 00111110 00111010 01011100 01111000 00110000 00110110 01011100 01111000 00110000 00110010 01011100 01111000 01100110 01100110 01011100 01111000 01100001 01100010 01010111 01011100 01111000 01100011 00110011 01011010 01011100 01110010 01011100 01111000 00110000 00110000 01110101 01011100 01111000 01100001 01100010 01000100 01111010 01011100 01111000 01100011 00110101 01011100 01111000 01100110 01100101 01000010 01111001 01110000 01011100 01111000 00110000 00111000 01011100 01111000 01100011 00110101 01011100 01111000 01100010 01100010 01011100 01111000 01100001 01100101 01011100 01111000 00111000 00111000 01001010 01010011 01011100 01110010 01011100 01111000 00110000 00110000 01011100 01111000 01100010 00110110 01011100 01111000 01100001 01100101 01011100 01111000 01100110 01100110 01110011 01000111 01111000 01011100 01111000 01100011 00110101 01011100 01111000 01100011 00110010 01100000 01011100 01111000 00110000 01100010 01011100 01111000 00110000 00110000 01011100 01111000 01100001 01100010 01011100 01111000 00110000 01100010 00110111 01011100 01111000 01100110 01100100 01111000 01011100 01111000 01100011 00110000 01101100 01011100 01111000 01100011 00110001 01011100 01111000 01100011 00110000 01011100 01111000 01100011 00110001 01011100 01101110 01011100 01111000 01100011 00110101 01111101 01011100 01111000 01100100 00110010 01011100 01111000 01100110 00111000 01011100 01111000 01100110 01100101 01011100 01111000 00111000 00110011 01111100 01011100 01111000 01100011 00110100 01011100 01111000 00110001 01100110 01011100 01111000 00110000 00110001 01011100 01111000 01100011 01100101 01011100 01111000 01100100 00110000 01011100 01111000 01100010 00111000 01111010 01011100 01111000 00111000 00110101 01011100 01111000 01100011 00110011 01011100 01111000 01100011 00110000 01011100 01111000 01100011 00110000 01011100 01111000 01100011 00110011 01011100 01111000 01100011 00110010 01010110 01011100 01111000 01100011 00110010 01011100 01111000 00111000 01100001 01111001 01011100 01111000 01100011 00110000 01011100 01111000 01100011 00110010 01011100 01111000 01100110 01100110 01011100 01111000 01100011 00110001 01011100 01111000 01100011 00110010 01101000 01011100 01111000 00110000 00110110 01011100 01111000 01100011 00110000 01011100 01111000 01100011 00110001 01111010 01011100 01111000 00110001 00111000 01011100 01111000 00110000 00110001 01011100 01111000 00110001 00110101 01011100 01111000 01100100 00110001 01011100 01111000 01100010 01100001 01011100 01111000 00111000 00110000 01011100 01111000 00110000 00110111 01011100 01111000 01100011 00110000 01011100 01111000 00111000 00110010 01111010 01011100 01111000 01100011 00110001 01011100 01111000 01100011 00110011 01011100 01111000 00111000 00111000 01011100 01111000 00111000 00110110 01011100 01111000 00111000 00110100 01011100 01111000 01100011 00110000 01011100 01111000 01100010 00111001 01011100 01111000 00110000 00110110 01011100 01111000 00110000 00110010 00101101 01011100 01111000 01100101 01100101 00110100 01011100 01111000 01100110 01100110 01011100 01111000 01100011 00110001 01111000 01011100 01111000 00110001 00111001 01011100 01111000 01100011 00110101 01011100 01111000 01100110 00110111 01011100 01111000 01100110 00110010 01110001 01011100 01111000 00111001 00110010 01111000 01011100 01111000 01100011 00110011 01011100 01111000 01100011 00110001 01011100 01111000 01100011 00110011 01011100 01111000 00111001 00110111 01011100 01111000 00110000 00110110 01011100 01111000 01100011 00110001 01011100 01111000 01100011 00110011 00110001 01011100 01111000 01100011 00110011 01101010 01011100 01111000 01100011 00110010 01011100 01111000 00110000 00110111 01011100 01111000 00110000 00110000 01010010 00110111 01000000 01011100 01111000 01100011 00110010 01011100 01111000 01100011 00110110 01011100 01111000 01100011 00110011 01011100 01111000 00110000 00110111 01011100 01111000 00110000 00110000 01011000 01011100 01111000 01100110 00110010 00111010 01011100 01111000 00111001 01100100 01011100 01111000 00111001 00110010 01011100 01111000 00110001 00111000 01011100 01111000 01100010 00111000 01011100 01111000 01100101 00111000 01011100 01111000 01100110 00110100 01011100 01111000 01100010 01100100 01110100 01111001 01011100 01111000 01100011 00110011 01011100 01111000 00110000 00110100 01011100 01111000 01100011 00110110 01011100 01111000 01100001 01100011 00111110 01011100 01111000 01100011 00110001 01100111 01011100 01111000 01100011 00110010 01100001 01011100 01111000 01100110 01100100 01011100 01111000 00110000 00110100 01011100 01111000 01100011 00110101 01011100 01111000 01100110 00110010 01011100 01111000 01100110 00110100 01011100 01111000 01100001 00110110 01101100 01011100 01111000 00110000 00110101 01011100 01111000 00110000 00110000 01011100 01111000 01100101 01100100 01011100 01111000 01100110 01100011 01011100 01111000 00110001 01100101 01011100 01111000 00110000 00110100 00111000 01011100 01111000 00110000 00110100 01011100 01111000 01100001 00111000 01011100 01111000 01100101 00110100 01011100 01111000 00110000 00110110 00101011 01011100 01111000 01100011 00110010 01011100 01111000 01100110 01100110 01101000 01011100 01111000 01100011 00110011 01011100 01111000 00110001 00110000 01011100 01111000 01100100 00110000 01011100 01111000 01100010 00110100 00111011 01011100 01111000 01100011 00110111 01010100 01011100 01111000 00110000 00110110 01011100 01111000 00110001 00110000 01101100 01011100 01111000 01100011 00111000 00111101 01011100 01111000 01100011 00110000 00101001 01011100 01111000 00110000 00110100 01011100 01111000 00110001 00110000 01110010 01011100 01110010 00110111 01011100 01111000 00111000 00110000 01011100 01111000 01100011 00110110 01011100 01111000 00110001 00110001 01011100 01111000 00110000 00110010 01011100 01111000 01100001 00110101 00101000 01011100 01111000 01100011 00110010 01011100 01111000 00110000 00110011 01011100 01111000 00110001 00110000 01011100 01111000 01100010 01100011 00101001 01011100 01111000 01100101 01100011 01011100 01111000 01100011 00110001 01011100 01111000 00110001 01100101 01011100 01111000 01100001 00111000 01011100 01111000 01100010 00110000 00101100 01011100 01111000 01100010 00110000 01011100 01111000 01100011 00110000 01011100 01111000 01100110 01100110 01001101 00111001 01011100 01111000 01100110 01100110 01011100 01111000 01100110 01100110 01111000 01011100 01111000 01100110 01100110 01011100 01111000 01100110 01100010 01011100 01111000 01100110 01100010 01011100 01111000 01100110 00111001 01011100 01111000 01100110 01100100 01011100 01111000 01100110 01100101 00111011 01011100 01111000 01100110 01100110 01011100 01111000 01100011 00110010 01000111 01011100 01111000 01100110 01100101 01011100 01111000 01100110 01100110 01011100 01111000 01100011 00110011 01011100 01111000 01100011 00110100 01011100 01111000 01100011 00110000 01101000 01011100 01111000 01100011 00110001 01011100 01111000 00110001 00110000 01011100 01111000 01100110 00110000 01011100 01111000 01100110 01100110 01011100 01111000 00111000 00110001 01011100 01111000 01100011 00110010 01011100 01111000 01100110 01100110 01011100 01111000 00110000 00110000 00100010 '
                # f = io.BytesIO(tmp)
                # f.write(base64.decodebytes(tmp))
                # f.seek(1)
                # tmp.seek(0)
                # tmp1='LeSS21\x00\x00\x05&$\x04\x08\x05\x07\t\xce\xd0\x00\x00\x1d\'i\x01\x00\x00\x00\x85\xcb.\x9e&.\x00\x1b\x0fp\x00\x88\x00\t)d\x00V\x00n\x0f{\x00[&!\x0f4\x00e\x00\x9b\x0fh&n\x00d\x0f8\x00\xba\x00_)Q\x00\x81\x00V\x0f\x00\x00\x84&&\x0f\xa7\x00\x83\x00\xea\x0ff&\x85\x00O\x0f\x98\x00U\x00\x9d(3\x00\x98\x00O\x0fm\x00\x98&\xab\r~\x00\xaa\x00\xec\x0e\xb4&\xab\x00\xad\x0c\xe4\x00h\x00\x13+\xd6\x00\xae\x00&\x0c\x8b\x00\xbf&8\x0f?\x00\xc4\x00\x85\x0f\xec&\xc4\x00\x9c\r\x9b\x00\x0f\x00\x02)\xd6\x00\xcc\x00\x8e\r\xf6\x00\xd7&I\x0f\xad\x00\xe1\x008\x0f\xd0&\xe5\x00y\x0f<\x00)\x00:+t\x00\xf5\x00\xa2\x0f\x8e\x00\xf9&\x98\r.\x00\xfe\x00\x17\rY&\x00\x01\x99\x0f.\x00\xcf\x01\xf9+\x7f\x00\x0b\x01\x95\x0f\xa1\x00\x15\'\x86\x0f\xbd\x00\x12\x01G\x0f\x9e&\x15\x01\x8c\x0f\xd7\x00\xe5\x01\xf7)u\x00&\x01\x81\x0f\x1f\x00.\'t\x0f\xa2\x001\x01@\x0fN&6\x01\x7f\x0f\xaa\x00\xfe\x01z)\xb3\x00K\x01\xf9\x0eC\x00I\'}\x0f\xcc\x00[\x01\xbe\x0e\xb9&_\x01\x00\x0e\xcf\x11J\xff\xca\x89\xd8\xa0\xba\xa9_\xf1<d@)V \x9a\xf9\xba\xf3\xce\x07X!G\ng\x11q\x16\x14\xfb\xe7\x7f(\x06q\x0f\xe1\xff\xf4\t\xa8\xd8\x17\xf5\xda\xf8\x12\t\x7f~\xb0\xbf\x90\x87R\x08\xb9\xf9\xc0\xee\xb3\xd1\xcci\x05\xf1\n\xed8\xf7\x1f\xdcW\x1b\xfd\xfcq\x15P\x7f?\xb7{\'N\x83}\x04\xb3\x15\xdf\xac\xe9\xf3\xa1~\xbe\x89\x9d\x13\x84\xa9\x9f\x98\xb1\xf9\xaa\xf1+\xef,/\x9c\xf9\x86\x02U\x11X\x8a\x8c]\xa0\x0fR^\x1e\xe3 \xf500\xb7h\x15\tm\x0b\xdb\x11,\xdd\x8b\x86sp\xcd\xee\'\xdd\x8bXd\xaa\x9dn\xf5\xfb\xd4\x0eH-7\x1c\xf5\x01\x89^\xa0\xcb\xf5\xfd\x88\x96\xad;\x15\x14\xb0\x01\xd0\xddE/rdV\xbcX\xf6`58\x17\xa5\xf0\xf1\xf7\xe4\x0b\x13\xb6\x7f\xf9\x1e\x0e.\x08G\xf8\xf7+\xc5\x7f&p\xfbu`\xff\xc8\xc9/\x07\xc0\x87\xaa\xf6\x9e\xfd%-\xb3\xf8&\x8c\xf2\x03\x1e\xf8\xae\xa0\xa5\xff1\x89.\x82\xf0}\xb0\xdf3t\xe6\xfa\xf6\xfes\xffxZ\x9f\x84\xa7\xfcy\x84\xe8\t+\xa4A\xb2\x98\xa7\x01-\xe5I\x04$\xdb"n\x04\x00\xa5\xc1\x17N"\x01\xa1\n\x16Z\x04\xc5\x95\x11*1\x07\x00\x95\x1a\x0f\x05\xfd_/\x01\x85\x1c\x0cA\xff\x07C\x0f&t!\x06>\xfe\xfe\x04l\x03&Z(w\x8c\xff\r\xc5c-\xdb\xff\xff\xfe\xff6\xc1\x05J\x02&\x9f0\x1a\xffk\xff\xc8\x00\xade\x96\x84\x88\xc0\xc3j\xc2\x00\xaea#\xc1\xc2\xfd]\r\xc5\xa7M\xb0\xc0\xc1\x90\x88i\x04\xc5\x81O\xa0\x88\x0b\x00\x83K\x0c88\xfas\xc1\x08\x00YMt\x07\xc2c\xe7\x0c\x00tN\x06\xfe8\xc0\xfa\xd9>E\x08\x00\xa9N\xdb\xc0\xfb\xe7\xc1d\n\x00bV\xb4\x88\\J\x04\x00\xc1` \xc0\x9c\x04\x05\x15ibs\x16\x00\x16\xa8\xdc\xfa\x1e2\xff3\xfd\xc0U\xae\xc0\x10&\x1dm\xe2\xc0>1\xf4+\\w\x11\x00kpk\xc3\x07\xc2\xc6o\xc1\xc2\xc3\xc3\xc0\x95\xc3\x00jS\x01\xfd\xfc.\x0c\x00\xa8wb\xe4\xc2\xc3\x80\xc1\xc2{\xd4\x00>]\xdf\xc0\xfd\xff\xfd\xfd;\xfe\xfb\xd9\xc1\xfe\xff\xff\xc1\xc0\xc9\x00\xa1Y\xa1y\xc3\xc3\xc3\xc2\x05\x8d\x03&2\x81\\\xc0\xc2|\xc2\x00=\xa5[\xc0~\xc0\x07\x00\x8b\x83R\xa0K\x06\x00\xc8\x85\'\x07\xff\xc5\xe4\x04\x00\xab\x86+\xff\x9a\x15\x05G\x86V\xc3\xc3u\xc1A\x8b\xc6\xe7\xc0\xc2\xc1\xff\xc1\x03\xc5\xa6\x82\x0b\xfe\x18\x00\x96\x8d\x9c\x06\xc3\xc2\xe3\xc2\x8c\xc2\xc0\xc3\xc0\x04\xc2\xc7\xe7\xc2\xc1\xc0\xc2\xc0\xc1\xd2\x00\x13\xb5\xd67\xc0\xfe\xfe#\xf6\xff=j\xc0\xc5\x03\x00{\x98\xc3\xfe\t&w\x99L\xc4\xc2\xc2\x06u\xc4\x84\x14\x00\xa9\x99\xb0\xc2\x04\xc2\x9a\x84\xc3\xc1\xc2\xc1D\xc0\x82\x07\x05\x08\x9bP\xc0\xc1\xffY\xd6\x00\x91\xbc\x92\xc2\xc7\xc9\xc2\xc3\x07\xc2\xc4\xe4\xc1\xc3\xc1\xc3\xc3\xc0:\xc1\r&2\x9bL\xc0SU\xcd\x00|\xbb<\xc0\xc5\x80\xc3\x08\xc5\x7f\x98\x12\xc3\xc3\x97\xc4\x03\x00\x80\x9fL\xe4\x16\x00\xa2\xa4\xa9\xc4\x05\xc4\xc2\xe0\xc5\xc1\xc3\xc1\xc1\xc3\x05\xc2\xc4\xe5\xc1\xc4r\xc1\x0b\x00\xbb\xad(\xe4\xc0\xc2\xc4\xc3\\\xc0\xc6\x00\xda\x88(\xc5\x0c\x00M\xbd\xf8\xc3\x85Y\x82\x03\x00<\xc8C\x07\x05\x05g\xc9@\x8d\x06\x00\xf0\x16tG\xd8\x04\x000\xd6I\xff\x05\xfd\x01&7\xd6C\xff\xfd\x03\xc5\xfa\xddR\xc0\x06\x00M\xd90V\xc2\x146\xfa\x02mD\xff\xc0;\xffCd\xa4\x04\x102\x0c\xfa\xee\x12\x15\xd1\x0fth\xc0/>\x07\xc1\xfa\xa4\x11\x10\xf4\x1ep\xfe\x9f\xff\xf9\xe7D\xc1\xc1[\x0f\x102%l\xdb\xc22\xc0\xfe\xfe\xc1\xbd\xfd\x036q&\x83k\xc1\x0b\xd5\xd6)Q\xc0\xff\xfd\xc2:l\xcf\x10.\x08\xfcE^k\x06\x1025\x7f\xe59\x06\x10\xf6;m\x84\xc1\r6\xa6<}B\xc1W\xc1\x10\x87o|i\x03\x10\x8aK\xc3\xc2\x016\xe9Lp)\x05\x10vTx\xd9\xfe\xc4\x03\x10\xefS\xb4\xff\x016x\\\x00YRB\xc5\x0bF\'\x01\x00\x0bER\x00'
                # tmp1 = ' '.join(format(ord(x), 'b') for x in tmp1)
                # del tmp[0]
                # tmp1='01000111011001010110010101101011011100110110011001101111011100100100011101100101011001010110101101110011'
                    # base64.decodebytes(f)

                # tmp="".join(["{:08b}".format(x) for x in tmp])
                # tmp=binascii.unhexlify(tmp)
                # bin(tmp)
                # print("temmmmmmmm2",tmp)

                # tmp = Fernet(tmp)
                device_user_id = self.env['attendance.device.user'].search(
                    [('uid', '=', uid), ('device_id', '=', r.id)], limit=1)
                if not device_user_id:
                    continue
                vals = {
                    'device_user_id': device_user_id.id,
                    'fid': fid,
                    'valid': valid,
                    'template': tmp1,
                }

                if device_user_id.employee_id:
                    vals['employee_id'] = device_user_id.employee_id.id
                    # print('device_user_id', device_user_id)

                if (str(template.uid) + '_' + str(template.fid)) not in existing_finger_template_ids:
                    print("FingerTemplate", vals,FingerTemplate)
                    FingerTemplate.create(vals)
                else:
                    print("FingerTemplate1111", vals,FingerTemplate)
                    existing = FingerTemplate.search([
                        ('uid', '=', uid),
                        ('fid', '=', fid),
                        ('device_id', '=', r.id),
                    ], limit=1)
                    if existing:

                        existing.write(vals)
        return

    @api.model
    def is_attendance_clear_safe(self):
        """
        If the data from devices has not been downloaded into Odoo, this method will return false
        """
        UserAttendance = self.env['user.attendance']
        User = self.env['attendance.device.user']

        check_statuses = self.attendance_device_state_line_ids.mapped('code')

        attendances = self.getAttendance()  # Attendance(user_id, timestamp, status)
        for att in attendances:
            if att.punch not in check_statuses:
                continue
            user = User.with_context(active_test=False).search(
                [('user_id', '=', att.user_id), ('device_id', '=', self.id)], limit=1)
            utc_dt = self.convert_time_to_utc(att.timestamp, self.tz)
            match = UserAttendance.search([('device_id', '=', self.id),
                                           ('user_id', '=', user.id),
                                           ('status', '=', att.punch),
                                           ('timestamp', '=', utc_dt)], limit=1)
            if not match:
                return False, att
        return True, False

    def action_attendance_clear(self):
        """
        Method to clear all attendance data from the device
        """

        for r in self:
            error_msg = ""
            attendance_clear_safe, att = r.is_attendance_clear_safe()
            if attendance_clear_safe:
                r.clearAttendance()
            else:
                error_msg += _("It was not safe to clear attendance data from the device %s.<br />") % (r.name,)
                error_msg += _("The following attendance data has not been stored in Odoo yet:<br />")
                error_msg += _("user_id: %s<br />timestamp: %s<br />status: %s<br />") % (
                att.user_id, att.timestamp, att.punch)
                _logger.warning("It was not safe to clear attendance data from the device %s" % r.name)
                if r.auto_clear_attendance_error_notif:
                    email_template_id = self.env.ref('to_attendance_device.email_template_not_safe_to_clear_attendance')
                    r.post_message(email_template_id)
            if error_msg and r.debug_message:
                r.message_post(body=error_msg)

    def action_check_connection(self):
        self.ensure_one()
        if self.connect():
            self.disconnect()
            raise UserError(_('Connect to the device %s successfully') % (self.display_name,))

    def action_device_information(self):
        dbname = self._cr.dbname
        for r in self:
            try:
                cr = registry(dbname).cursor()
                r = r.with_env(r.env(cr=cr))
                r.connect()
                r.firmware_version = r.zk.get_firmware_version()
                r.serialnumber = r.zk.get_serialnumber()
                r.platform = r.zk.get_platform()
                r.oem_vendor = r.zk.get_oem_vendor()
                r.fingerprint_algorithm = r.zk.get_fp_version()
                r.device_name = r.zk.get_device_name()
                r.work_code = r.zk.get_workcode()
            except Exception as e:
                _logger.error(e)
            finally:
                cr.commit()
                cr.close()

    @api.model
    def post_message(self, email_template):
        if self.user_id:
            self.message_subscribe([self.user_id.partner_id.id])
        if email_template:
            self.message_post_with_template(email_template.id)

    def action_view_users(self):
        action = self.env.ref('to_attendance_device.device_user_list_action')
        result = action.read()[0]

        # reset context
        result['context'] = {}

        # choose the view_mode accordingly
        if self.device_users_count != 1:
            result['domain'] = "[('id', 'in', " + str(self.device_user_ids.ids) + ")]"
        elif self.device_users_count == 1:
            res = self.env.ref('to_attendance_device.attendance_device_user_form_view', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = self.device_user_ids.id
        return result

    def action_view_attendance_data(self):
        self.ensure_one()
        action = self.env.ref('to_attendance_device.action_user_attendance_data')
        result = action.read()[0]

        # reset context
        result['context'] = {}
        # choose the view_mode accordingly
        total_att_records = self.total_att_records
        if total_att_records != 1:
            result['domain'] = "[('device_id', 'in', " + str(self.ids) + ")]"
        elif total_att_records == 1:
            res = self.env.ref('to_attendance_device.view_attendance_data_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = self.user_attendance_ids.id
        return result

    def action_view_mapped_employees(self):
        action = self.env.ref('hr.open_view_employee_list_my')
        result = action.read()[0]

        # reset context
        result['context'] = {}
        # choose the view_mode accordingly
        if self.mapped_employees_count != 1:
            result['domain'] = "[('id', 'in', " + str(self.mapped_employee_ids.ids) + ")]"
        elif self.mapped_employees_count == 1:
            res = self.env.ref('to_attendance_device.view_employee_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = self.mapped_employee_ids.id
        return result

    def action_view_finger_template(self):
        self.ensure_one()
        action = self.env.ref('to_attendance_device.action_finger_template')
        result = action.read()[0]

        # reset context
        result['context'] = {}
        # choose the view_mode accordingly
        total_finger_template_records = self.total_finger_template_records
        if total_finger_template_records != 1:
            result['domain'] = "[('device_id', 'in', " + str(self.ids) + ")]"
        elif total_finger_template_records == 1:
            res = self.env.ref('to_attendance_device.view_finger_template_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = self.finger_template_ids.id
        return result

    def unlink(self):
        force_delete = self.env.context.get('force_delete', False)
        for r in self:
            if r.state != 'draft':
                raise UserError(_("You cannot delete the device '%s' while its state is not Draft.")
                                % (r.display_name,))
            if r.device_user_ids and not force_delete:
                raise UserError(_("You may not be able to delete the device '%s' while its data is stored in Odoo."
                                  " Please remove all the related data of this device before removing it from Odoo."
                                  " You may also consider to deactivate this device so that you don't have to delete"
                                  " it.") % (r.display_name,))
        return super(AttendanceDevice, self).unlink()


class AttendanceDeviceStateLine(models.Model):
    _name = 'attendance.device.state.line'
    _description = 'Attendance Device State'

    attendance_state_id = fields.Many2one('attendance.state', string='State Code', required=True, index=True, )
    device_id = fields.Many2one('attendance.device', string='Device', required=True, ondelete='cascade', index=True,
                                copy=False)
    code = fields.Integer(string='Code Number', related='attendance_state_id.code', store=True, readonly=True)
    type = fields.Selection([('checkin', 'Check-in'),
                             ('checkout', 'Check-out')], related='attendance_state_id.type',
                            store=True, readonly=True, index=True)
    activity_id = fields.Many2one('attendance.activity', related='attendance_state_id.activity_id',
                                  help='Attendance activity, e.g. Normal Working, Overtime, etc', readonly=True,
                                  store=True, index=True)

    _sql_constraints = [
        ('attendance_state_id_device_id_unique',
         'UNIQUE(attendance_state_id, device_id)',
         "The Code must be unique per Device"),
    ]

    @api.onchange('attendance_state_id')
    def onchange_attendance_state_id(self):
        self.type = self.attendance_state_id.type
