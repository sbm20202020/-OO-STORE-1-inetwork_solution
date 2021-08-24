# -*- coding: utf-8 -*-


def pre_init_hook(cr):
    """Loaded before installing the module.

    None of this module's DB modifications will be available yet.

    If you plan to raise an exception to abort install, put all code inside a
    ``with cr.savepoint():`` block to avoid broken databases.

    :param openerp.sql_db.Cursor cr:
        Database cursor.
    """
    pass


def post_init_hook(cr, registry):
    """
    Loaded after installing the module.
    The goal is to update security role view when the module is installed

    This module's DB modifications will be available.

    :param openerp.sql_db.Cursor cr:
        Database cursor.

    :param openerp.modules.registry.RegistryManager registry:
        Database registry, using v7 api.
    """
    from odoo import api, SUPERUSER_ID
    env = api.Environment(cr, SUPERUSER_ID, {})
    config = env['res.config.settings'].search([('company_id','=',env.user.company_id.id)], limit=1, order='id desc')
    #enable Tracking lots and serial number in inventory
    if config:
        if not config.group_stock_production_lot:
            config.group_stock_production_lot = True
            config.execute()
    else:
        res_config_id = env['res.config.settings'].create({
            'company_id': env.user.company_id.id,
            'group_stock_production_lot': True
        })
        res_config_id.execute()



def uninstall_hook(cr, registry):
    """Loaded before uninstalling the module.

    This module's DB modifications will still be available. Raise an exception
    to abort uninstallation.

    :param openerp.sql_db.Cursor cr:
        Database cursor.

    :param openerp.modules.registry.RegistryManager registry:
        Database registry, using v7 api.
    """
    pass


def post_load():
    """Loaded before any model or data has been initialized.

    This is ok as the post-load hook is for server-wide
    (instead of registry-specific) functionalities.
    """
    pass
