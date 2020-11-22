odoo.define('inventory_adjustments_access_right.InventoryValidationController', function (require) {
   "use strict";
   var CompletionFieldMixin = require('web.CompletionFieldMixin');

   var _t = core._t;
   var QWeb = core.qweb;

   CompletionFieldMixin.include({
       _onValidateInventory: function () {
        var self = this;
        var prom = Promise.resolve();
        var recordID = this.renderer.getEditableRecordID();
        if (recordID) {
            // If user's editing a record, we wait to save it before to try to
            // validate the inventory.
            prom = this.saveRecord(recordID);
        }

        prom.then(function () {
            self._rpc({
                model: 'stock.inventory',
                method: 'action_validate',
                args: [self.inventory_id]
            }).then(function (res) {
                var exitCallback = function (infos) {
                    // In case we discarded a wizard, we do nothing to stay on
                    // the same view...
                    if (infos && infos.special) {
                        return;
                    }
                    // ... but in any other cases, we go back on the inventory form.
                    self.do_notify(
                        _t("SuccessDoaaaaaaaaaa"),
                        _t("The inventory has been validated"));
                    self.trigger_up('history_back');
                };

                if (_.isObject(res)) {
                    self.do_action(res, { on_close: exitCallback });
                } else {
                    return exitCallback();
                }
            });
        });
    },
});
