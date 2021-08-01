odoo.define('to_safe_confirm_button.safe_confirm', function (require) {
"use strict";

var Dialog = require('web.Dialog')
var form_controller = require('web.FormController')

form_controller.include({
	_onButtonClicked: function (event) {
        event.stopPropagation();
        var self = this;
        var def;
        this._disableButtons();
        function saveAndExecuteAction () {
            return self.saveRecord(self.handle, {
                stayInEdit: true,
            }).then(function () {
                var record = self.model.get(event.data.record.id);
                return self._callButtonAction(attrs, record);
            });
        }
        var attrs = event.data.attrs;
        if (attrs.confirm) {
            var d = $.Deferred();
            Dialog.confirm(this, attrs.confirm, {
                confirm_callback: saveAndExecuteAction,
            }).on("closed", null, function () {
                d.resolve();
            });
            def = d.promise();
        } 
        else if (attrs.safe_confirm){
        	var d = $.Deferred();
            Dialog.safeConfirm(this, attrs.safe_confirm, {
                confirm_callback: saveAndExecuteAction,
            }).on("closed", null, function () {
                d.resolve();
            });
            def = d.promise();
        }
        else if (attrs.special === 'cancel') {
            def = this._callButtonAction(attrs, event.data.record);
        } else if (!attrs.special || attrs.special === 'save') {
            // save the record but don't switch to readonly mode
            def = saveAndExecuteAction();
        }
        def.then(this._enableButtons.bind(this));
    },
});
});

