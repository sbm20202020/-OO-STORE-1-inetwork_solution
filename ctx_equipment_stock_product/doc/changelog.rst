v1.0.0
======
 - Installing this module will enable the Inventory Lot/Serial number automatically.
 - Add "Is Equipment?" field to product template.
 - If the user select "Is Equipment?" in product, the inventory tracking will changed to "Tracking by Serial Number".
 - If the user select "Is Equipment?" in product, A new tab named equipments will be shown and you can set a default value
   for equipment category, Maintenance Team, Technician and Used By fields, This fields will be used in creating
  equipment from shipment or inventory adjustments.
 - From Product form view, you can click on Equipments smart button to view all Equipments linked to the product.
 - When you do Inventory adjustment, you can select "Create Equipment" in Inventory lines to create equipment automatically,
   The created equipment will be linked to lot_id (serial number) and to the lot product and the serail number field will be
  filled automatically from lot. also all fields in product which related to equipments will passed to created equipment.
 - The created equipment will have a field named "current stock location" which filled from inventory adjustment or received shipment,
   When yuo do internal transfer for the product linked to the equipment, this field will be updated with the transfer destination location.
 - From equipment, you can track all movements of the product linked to equipment using "Moves History" smart button.
 - From lot/serial number, you will see the equipment linked to the product lot.
 - display Active/Archive smart button in equipment form.
