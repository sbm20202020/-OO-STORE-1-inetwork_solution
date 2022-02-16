# This code parses date/times, so please
#
#     pip install python-dateutil
#
# To use this code, make sure you
#
#     import json
#
# and then, to convert JSON from a string, do
#
#     result = invoice_from_dict(json.loads(json_string))

from dataclasses import dataclass
from typing import Optional, Any, List, TypeVar, Callable, Type, cast
import dateutil.parser

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import requests
from datetime import datetime
from typing import List, Optional

from ...account.models import account_move
import json
from json.encoder import JSONEncoder
import sys
import requests


# class AccountMove(models.Model):
#     _inherit = 'account.move'
#selections = [('1','1'),('2','2')]


class AccountMove(models.Model):
    _inherit = 'account.move'

    document_type = fields.Char( required=False, )
    taxpayer_activity_code = fields.Char(default="1030", required=False, track_visibility='always' )
    document_type_version = fields.Char(default="1.0", required=True, )
    total_sales_amount = fields.Monetary(compute='_compute_total', currency_field='company_currency_id')
    total_discount_amount = fields.Monetary(compute='_compute_total', currency_field='company_currency_id')
    net_amount = fields.Monetary(compute='_compute_total', currency_field='company_currency_id')
    extra_discount_amount = fields.Monetary(compute='_compute_total', currency_field='company_currency_id')
    total_amount = fields.Monetary(compute='_compute_total', currency_field='company_currency_id')
    total_items_discount_amount = fields.Monetary(compute='_compute_total', currency_field='company_currency_id')

    eta_uuid = fields.Char(copy=False)
    eta_url = fields.Char(copy=False)
    eta_public_url = fields.Char(copy=False)

    def get_tax_total(self):
        tax_total = {}
        for line in self.invoice_line_ids:
            taxable_items = line.get_taxable_items()
            for key,val in taxable_items.items():
                if not key in tax_total:
                    tax_total[key] = taxable_items[key].copy()
                else:
                    tax_total[key]['amount'] += taxable_items[key]['amount']

        return tax_total

    @api.depends('invoice_line_ids','invoice_line_ids.sales_total','invoice_line_ids.price_total','invoice_line_ids.discount')
    def _compute_total(self):
        for rec in self:
            currency = rec.currency_id
            comp_currency = rec.company_currency_id
            inv_date = rec.date
            company = rec.company_id or self.env.user.company_id
            # price_unit = currency._convert(rec.price_unit, comp_currency, company, inv_date)
            rec.total_sales_amount = sum( line.sales_total for line in rec.invoice_line_ids )
            rec.total_discount_amount = sum( line.sales_total * (line.discount / 100.0) for line in rec.invoice_line_ids )
            rec.net_amount = sum( line.net_total for line in rec.invoice_line_ids )
            rec.extra_discount_amount = currency._convert(rec.ks_amount_discount, comp_currency, company, inv_date)
            rec.total_items_discount_amount = currency._convert(0 , comp_currency, company, inv_date)
            rec.total_amount = rec.net_amount + currency._convert(rec.amount_tax , comp_currency, company, inv_date)  - rec.extra_discount_amount - rec.total_items_discount_amount


    def action_post_tax(self):
        print("ahmed Fahmy")

        testNames=["EG-200148796-041","EG-200148796-042","EG-200148796-043","EG-200148796-043","EG-200148796-044","EG-200148796-003"]
        i=-1

        # refresh and show status every 3 min
        # set decimal number up to 5
        # add status and uuid to db
        # set eta submit invoice as stand alone button
        # handle the url in messages
        # invoice = Invoice()
        to_post = self
        # invoice.documents = []
        for move in to_post:
            i+=1
            invoice = Invoice()
            document = Document()

            invoice.documents = []
            print('move.document_type')
            print(move.document_type)
            document.document_type = move.document_type #"I"
            document.document_type_version = move.document_type_version #"1.0"
            document.date_time_issued = move.date.strftime('%Y-%m-%dT%H:%M:%SZ')#"2021-01-29T03:59:59Z"
            document.taxpayer_activity_code = move.taxpayer_activity_code #"1010"
            document.internal_id = move.name

            document.total_items_discount_amount = move.total_items_discount_amount
            document.total_amount = move.total_amount
            document.extra_discount_amount = move.extra_discount_amount
            # document.totalItemsDiscountAmount = move.extra_discount_amount #init
            document.total_discount_amount = move.total_discount_amount
            document.total_sales_amount = move.total_sales_amount
            document.net_amount = move.net_amount
            # document.tax_totals = list(move.get_tax_total().values())
            document.tax_totals = []
            for taxItem in move.get_tax_total().values():
                taxtotal_item = TaxTotal()
                taxtotal_item.amount = taxItem['amount']
                taxtotal_item.tax_type = taxItem['tax_type']
                taxtotal_item.rate = taxItem['rate']
                taxtotal_item.sub_type = taxItem['sub_type']
                document.tax_totals.append(taxtotal_item)

            # taxTotal = TaxTotal()
            # taxTotal.tax_type = "T1" ##need dynamic
            # taxTotal.amount = 0.0#init
            # document.tax_totals.append(taxTotal)
            print('tax_totals')
            print(document.tax_totals)

            document.issuer = Issuer()
            document.issuer.name = move.company_id.name
            document.issuer.type = "B"
            document.issuer.id = move.company_id.vat
            document.issuer.address = Address()
            document.issuer.address.branch_id = move.company_id.branch_id #"0"
            document.issuer.address.country = move.company_id.country_id.code
            document.issuer.address.governate = move.company_id.city
            document.issuer.address.region_city = move.company_id.region_city
            document.issuer.address.street =move.company_id.street
            document.issuer.address.building_number = move.company_id.building_number #"0"

            document.receiver = Issuer()
            document.receiver.name = move.invoice_partner_display_name
            document.receiver.type = move.partner_id.get_company_type() #"B"
            document.receiver.id =  move.partner_id.vat
            document.receiver.address = Address()
            document.receiver.address.country = move.partner_id.country_id.code
            document.receiver.address.governate = move.partner_id.city
            document.receiver.address.region_city =move.partner_id.region_city# "Nasr City"
            document.receiver.address.street = move.partner_id.street#"580 Clementina Key"
            document.receiver.address.building_number = move.partner_id.building_number #"0"

            document.invoice_lines = []
            for line in move.invoice_line_ids:
                invoiceLine = InvoiceLine()

                invoiceLine.quantity = line.quantity
                invoiceLine.description = line.name# "Carton of 6 Apple drink glass bottles 1L"  # line.name
                invoiceLine.item_type =  line.product_id.item_type #"EGS"
                invoiceLine.item_code =  line.product_id.item_code #testNames[i]#"EG-200148796-043"# line.tax_line_id.name
                invoiceLine.unit_type = line.product_uom_id.unit_type #"KGM" #line.product_uom_id.uom_type

                invoiceLine.sales_total = line.sales_total
                # document.total_sales_amount+=invoiceLine.sales_total
                invoiceLine.total =  line.total  #line.price_total#invoiceLine.sales_total *(1-line.discount)+move.amount_tax.real #114.0
                invoiceLine.value_difference = 0.0
                invoiceLine.total_taxable_fees = line.total_taxable_fees
                invoiceLine.net_total =  line.net_total #line.price_unit*line.quantity
                invoiceLine.items_discount = line.items_discount

                invoiceLine.taxable_items = []
                # for taxItem in line.tax_ids:
                for taxItem in line.get_taxable_items().values():
                    taxable_item = TaxableItem()
                    # taxable_item.amount = (taxItem.amount/100)*line.price_unit*line.quantity
                    # taxable_item.tax_type = "T1" ##need dynamic
                    # taxable_item.rate = taxItem.amount
                    # document.tax_totals[0].amount +=(taxItem.amount/100)*line.price_unit*line.quantity ##need dynamic
                    # taxable_item.sub_type = "V009" ##need dynamic
                    # invoiceLine.taxable_items.append(taxable_item)
                    taxable_item.amount = taxItem['amount']
                    taxable_item.tax_type = taxItem['tax_type']
                    taxable_item.rate = taxItem['rate']
                    taxable_item.sub_type = taxItem['sub_type']
                    invoiceLine.taxable_items.append(taxable_item)

                currency = line.currency_id
                comp_currency = line.company_currency_id
                inv_date = line.move_id.date
                company = line.company_id or self.env.user.company_id
                invoiceLine.unit_value = UnitValue()
                invoiceLine.unit_value.currency_sold = move.currency_id.name
                invoiceLine.unit_value.amount_egp = currency._convert( line.price_unit, comp_currency, company, inv_date) if move.currency_id != move.company_id.currency_id else line.price_unit
                invoiceLine.unit_value.amount_sold = line.price_unit if move.currency_id != move.company_id.currency_id else 0.0
                invoiceLine.unit_value.currency_exchange_rate = invoiceLine.unit_value.amount_egp / line.price_unit if move.currency_id != move.company_id.currency_id else 0.0
                document.invoice_lines.append(invoiceLine)

                invoiceLine.discount = Discount()
                invoiceLine.discount.amount = line.sales_total * line.discount / 100.0
                invoiceLine.discount.rate = line.discount

            invoice.documents.append(document)
            print(move.date)

            # todo convert invoice to json using to_dict
            filtered = remove_none(invoice_to_dict(invoice))
            # raise ValidationError(_('%s')%(filtered))

            print(filtered)
            res = requests.post('http://41.130.144.84:8080/api/invoice/signJson', json=filtered, verify=False)
            res = json.loads(res.text)
            if res.get('acceptedDocuments'):
                move.eta_uuid = res["acceptedDocuments"][0]["uuid"]
                move.eta_url = res["url"]
                move.eta_public_url = res["publicUrl"]
                message = "uuid: " + res["acceptedDocuments"][0]["uuid"] + " submission Id: " + res[
                    "submissionId"] + " URL: " + \
                          res["url"] + " publicUrl: " + res["publicUrl"]
                move.message_post(body=message)
            else:
                raise ValidationError(_('Document is not accepted %s ! \n sent data : %s' % (res, filtered)))
            # return super(AccountMove, self).action_post()

    @api.model
    def create(self, values):
        default_type = self._context.get('default_type')
        if default_type == 'out_invoice':
            values['document_type'] = 'I'
        elif default_type == 'out_refund':
            values['document_type'] = 'C'
        # elif default_type == 'in_invoice':
        #     values['document_type'] = 'C'
        elif default_type == 'in_refund':
            values['document_type'] = 'D'

        return super(AccountMove, self).create(values)




T = TypeVar("T")


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except:
            pass
    # assert False


def from_datetime(x: Any) -> datetime:
    return dateutil.parser.parse(x)


def from_float(x: Any) -> float:
    assert isinstance(x, (float, int)) and not isinstance(x, bool)
    return round(float(x), 5)


def to_float(x: Any) -> float:
    assert isinstance(x, float)
    return round(float(x), 5)


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def is_type(t: Type[T], x: Any) -> T:
    assert isinstance(x, t)
    return x


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


@dataclass
class Delivery:
    approach: Optional[str] = None
    packaging: Optional[str] = None
    date_validity: Optional[datetime] = None
    export_port: Optional[str] = None
    country_of_origin: Optional[str] = None
    gross_weight: Optional[float] = None
    net_weight: Optional[float] = None
    terms: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any):
        assert isinstance(obj, dict)
        approach = from_union([from_str, from_none], obj.get("approach"))
        packaging = from_union([from_str, from_none], obj.get("packaging"))
        date_validity = from_union([from_datetime, from_none], obj.get("dateValidity"))
        export_port = from_union([from_str, from_none], obj.get("exportPort"))
        country_of_origin = from_union([from_str, from_none], obj.get("countryOfOrigin"))
        gross_weight = from_union([from_float, from_none], obj.get("grossWeight"))
        net_weight = from_union([from_float, from_none], obj.get("netWeight"))
        terms = from_union([from_str, from_none], obj.get("terms"))
        return Delivery(approach, packaging, date_validity, export_port, country_of_origin, gross_weight, net_weight,
                        terms)

    def to_dict(self) -> dict:
        result: dict = {}
        result["approach"] = from_union([from_str, from_none], self.approach)
        result["packaging"] = from_union([from_str, from_none], self.packaging)
        result["dateValidity"] = from_union([lambda x: x.isoformat(), from_none], self.date_validity)
        result["exportPort"] = from_union([from_str, from_none], self.export_port)
        result["countryOfOrigin"] = from_union([from_str, from_none], self.country_of_origin)
        result["grossWeight"] = from_union([to_float, from_none], self.gross_weight)
        result["netWeight"] = from_union([to_float, from_none], self.net_weight)
        result["terms"] = from_union([from_str, from_none], self.terms)
        return result


@dataclass
class Discount:
    rate: Optional[float] = None
    amount: Optional[float] = None

    @staticmethod
    def from_dict(obj: Any):
        assert isinstance(obj, dict)
        rate = from_union([from_float, from_none], obj.get("rate"))
        amount = from_union([from_float, from_none], obj.get("amount"))
        return Discount(rate, amount)

    def to_dict(self) -> dict:
        result: dict = {}
        result["rate"] = from_union([from_float, from_none], self.rate)
        result["amount"] = from_union([to_float, from_none], self.amount)
        return result


@dataclass
class TaxableItem:
    tax_type: Optional[str] = None
    amount: Optional[float] = None
    sub_type: Optional[str] = None
    rate: Optional[float] = None


    @staticmethod
    def from_dict(obj: Any):
        assert isinstance(obj, dict)
        tax_type = from_union([from_str, from_none], obj.get("taxType"))
        amount = from_union([from_float, from_none], obj.get("amount"))
        sub_type = from_union([from_str, from_none], obj.get("subType"))
        rate = from_union([from_float, from_none], obj.get("rate"))
        return TaxableItem(tax_type, amount, sub_type, rate)

    def to_dict(self) -> dict:
        result: dict = {}
        result["taxType"] = from_union([from_str, from_none], self.tax_type)
        result["amount"] = from_union([to_float, from_none], self.amount)
        result["subType"] = from_union([from_str, from_none], self.sub_type)
        result["rate"] = from_union([from_float, from_none], self.rate)
        return result


@dataclass
class UnitValue:
    currency_sold: Optional[str] = None
    amount_egp: Optional[float] = None
    amount_sold: Optional[float] = None
    currency_exchange_rate: Optional[float] = None

    @staticmethod
    def from_dict(obj: Any):
        assert isinstance(obj, dict)
        currency_sold = from_union([from_str, from_none], obj.get("currencySold"))
        amount_egp = from_union([from_float, from_none], obj.get("amountEGP"))
        amount_sold = from_union([from_float, from_none], obj.get("amountSold"))
        currency_exchange_rate = from_union([from_float, from_none], obj.get("currencyExchangeRate"))
        return UnitValue(currency_sold, amount_egp, amount_sold, currency_exchange_rate)

    def to_dict(self) -> dict:
        result: dict = {}
        result["currencySold"] = from_union([from_str, from_none], self.currency_sold)
        result["amountEGP"] = from_union([to_float, from_none], self.amount_egp)
        result["amountSold"] = from_union([from_float, from_none], self.amount_sold)
        result["currencyExchangeRate"] = from_union([to_float, from_none], self.currency_exchange_rate)
        return result


@dataclass
class InvoiceLine:
    item_code: Optional[str] = None
    description: Optional[str] = None
    item_type: Optional[str] = None
    unit_type: Optional[str] = None
    quantity: Optional[float] = None
    internal_code: Optional[str] = None
    sales_total: Optional[float] = None
    total: Optional[float] = None
    value_difference: Optional[float] = None
    total_taxable_fees: Optional[float] = None
    net_total: Optional[float] = None
    items_discount: Optional[float] = None
    unit_value: Optional[UnitValue] = None
    discount: Optional[Discount] = None
    taxable_items: Optional[List[TaxableItem]] = None

    @staticmethod
    def from_dict(obj: Any):
        assert isinstance(obj, dict)
        item_code = from_union([from_str, from_none], obj.get("itemCode"))
        description = from_union([from_str, from_none], obj.get("description"))
        item_type = from_union([from_str, from_none], obj.get("itemType"))
        unit_type = from_union([from_str, from_none], obj.get("unitType"))
        quantity = from_union([from_float, from_none], obj.get("quantity"))
        internal_code = from_union([from_str, from_none], obj.get("internalCode"))
        sales_total = from_union([from_float, from_none], obj.get("salesTotal"))
        total = from_union([from_float, from_none], obj.get("total"))
        value_difference = from_union([from_float, from_none], obj.get("valueDifference"))
        total_taxable_fees = from_union([from_float, from_none], obj.get("totalTaxableFees"))
        net_total = from_union([from_float, from_none], obj.get("netTotal"))
        items_discount = from_union([from_float, from_none], obj.get("itemsDiscount"))
        unit_value = from_union([UnitValue.from_dict, from_none], obj.get("unitValue"))
        discount = from_union([Discount.from_dict, from_none], obj.get("discount"))
        taxable_items = from_union([lambda x: from_list(TaxableItem.from_dict, x), from_none], obj.get("taxableItems"))
        return InvoiceLine(item_code, description, item_type, unit_type, quantity, internal_code, sales_total, total,
                           value_difference, total_taxable_fees, net_total, items_discount, unit_value, discount,
                           taxable_items)

    def to_dict(self) -> dict:
        result: dict = {}
        result["itemCode"] = from_union([from_str, from_none], self.item_code)
        result["description"] = from_union([from_str, from_none], self.description)
        result["itemType"] = from_union([from_str, from_none], self.item_type)
        result["unitType"] = from_union([from_str, from_none], self.unit_type)
        result["quantity"] = from_union([from_float, from_none], self.quantity)
        result["internalCode"] = from_union([from_str, from_none], self.internal_code)
        result["salesTotal"] = from_union([to_float, from_none], self.sales_total)
        result["total"] = from_union([to_float, from_none], self.total)
        result["valueDifference"] = from_union([from_float, from_none], self.value_difference)
        result["totalTaxableFees"] = from_union([to_float, from_none], self.total_taxable_fees)
        result["netTotal"] = from_union([to_float, from_none], self.net_total)
        result["itemsDiscount"] = from_union([from_float, from_none], self.items_discount)
        result["unitValue"] = from_union([lambda x: to_class(UnitValue, x), from_none], self.unit_value)
        result["discount"] = from_union([lambda x: to_class(Discount, x), from_none], self.discount)
        result["taxableItems"] = from_union([lambda x: from_list(lambda x: to_class(TaxableItem, x), x), from_none],
                                            self.taxable_items)
        return result


@dataclass
class Address:
    branch_id: Optional[str] = None
    postal_code: Optional[int] = None
    floor: Optional[int] = None
    room: Optional[int] = None
    country: Optional[str] = None
    governate: Optional[str] = None
    region_city: Optional[str] = None
    street: Optional[str] = None
    building_number: Optional[str] = None
    landmark: Optional[str] = None
    additional_information: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any):
        assert isinstance(obj, dict)
        branch_id = from_union([from_str, from_none], obj.get("branchID"))
        postal_code = from_union([from_none, lambda x: int(from_str(x))], obj.get("postalCode"))
        floor = from_union([from_none, lambda x: int(from_str(x))], obj.get("floor"))
        room = from_union([from_none, lambda x: int(from_str(x))], obj.get("room"))
        country = from_union([from_str, from_none], obj.get("country"))
        governate = from_union([from_str, from_none], obj.get("governate"))
        region_city = from_union([from_str, from_none], obj.get("regionCity"))
        street = from_union([from_str, from_none], obj.get("street"))
        building_number = from_union([from_str, from_none], obj.get("buildingNumber"))
        landmark = from_union([from_str, from_none], obj.get("landmark"))
        additional_information = from_union([from_str, from_none], obj.get("additionalInformation"))
        return Address(branch_id, postal_code, floor, room, country, governate, region_city, street, building_number,
                       landmark, additional_information)

    def to_dict(self) -> dict:
        result: dict = {}
        result["branchID"] = from_union([from_str, from_none], self.branch_id)
        result["postalCode"] = from_union([lambda x: from_none((lambda x: is_type(type(None), x))(x)),
                                           lambda x: from_str((lambda x: str((lambda x: is_type(int, x))(x)))(x))],
                                          self.postal_code)
        result["floor"] = from_union([lambda x: from_none((lambda x: is_type(type(None), x))(x)),
                                      lambda x: from_str((lambda x: str((lambda x: is_type(int, x))(x)))(x))],
                                     self.floor)
        result["room"] = from_union([lambda x: from_none((lambda x: is_type(type(None), x))(x)),
                                     lambda x: from_str((lambda x: str((lambda x: is_type(int, x))(x)))(x))], self.room)
        result["country"] = from_union([from_str, from_none], self.country)
        result["governate"] = from_union([from_str, from_none], self.governate)
        result["regionCity"] = from_union([from_str, from_none], self.region_city)
        result["street"] = from_union([from_str, from_none], self.street)
        result["buildingNumber"] = from_union([from_str, from_none], self.building_number)
        result["landmark"] = from_union([from_str, from_none], self.landmark)
        result["additionalInformation"] = from_union([from_str, from_none], self.additional_information)
        return result


@dataclass
class Issuer:
    id: Optional[str] = None
    address: Optional[Address] = None
    type: Optional[str] = None
    name: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any):
        assert isinstance(obj, dict)
        id = from_union([from_str, from_none], obj.get("id"))
        address = from_union([Address.from_dict, from_none], obj.get("address"))
        type = from_union([from_str, from_none], obj.get("type"))
        name = from_union([from_str, from_none], obj.get("name"))
        return Issuer(id, address, type, name)

    def to_dict(self) -> dict:
        result: dict = {}
        result["id"] = from_union([from_str, from_none], self.id)
        result["address"] = from_union([lambda x: to_class(Address, x), from_none], self.address)
        result["type"] = from_union([from_str, from_none], self.type)
        result["name"] = from_union([from_str, from_none], self.name)
        return result


@dataclass
class Payment:
    bank_name: Optional[str] = None
    bank_address: Optional[str] = None
    bank_account_no: Optional[str] = None
    bank_account_iban: Optional[str] = None
    swift_code: Optional[str] = None
    terms: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any):
        assert isinstance(obj, dict)
        bank_name = from_union([from_str, from_none], obj.get("bankName"))
        bank_address = from_union([from_str, from_none], obj.get("bankAddress"))
        bank_account_no = from_union([from_str, from_none], obj.get("bankAccountNo"))
        bank_account_iban = from_union([from_str, from_none], obj.get("bankAccountIBAN"))
        swift_code = from_union([from_str, from_none], obj.get("swiftCode"))
        terms = from_union([from_str, from_none], obj.get("terms"))
        return Payment(bank_name, bank_address, bank_account_no, bank_account_iban, swift_code, terms)

    def to_dict(self) -> dict:
        result: dict = {}
        result["bankName"] = from_union([from_str, from_none], self.bank_name)
        result["bankAddress"] = from_union([from_str, from_none], self.bank_address)
        result["bankAccountNo"] = from_union([from_str, from_none], self.bank_account_no)
        result["bankAccountIBAN"] = from_union([from_str, from_none], self.bank_account_iban)
        result["swiftCode"] = from_union([from_str, from_none], self.swift_code)
        result["terms"] = from_union([from_str, from_none], self.terms)
        return result


# @dataclass
# class TaxTotal:
#     tax_type: Optional[str] = None
#     amount: Optional[float] = None


@dataclass
class TaxTotal:
    tax_type: Optional[str] = None
    amount: Optional[float] = None
    sub_type: Optional[str] = None
    rate: Optional[float] = None

    @staticmethod
    def from_dict(obj: Any):
        assert isinstance(obj, dict)
        tax_type = from_union([from_str, from_none], obj.get("taxType"))
        amount = from_union([from_float, from_none], obj.get("amount"))
        return TaxTotal(tax_type, amount)

    def to_dict(self) -> dict:
        result: dict = {}
        result["taxType"] = from_union([from_str, from_none], self.tax_type)
        result["amount"] = from_union([to_float, from_none], self.amount)
        return result


@dataclass
class Document:
    taxpayer_activity_code: Optional[str] = None
    sales_order_reference: Optional[int] = None
    issuer: Optional[Issuer] = None
    receiver: Optional[Issuer] = None
    document_type: Optional[str] = None
    document_type_version: Optional[str] = None
    date_time_issued: Optional[str] = None
    internal_id: Optional[str] = None
    purchase_order_reference: Optional[str] = None
    purchase_order_description: Optional[str] = None
    sales_order_description: Optional[str] = None
    proforma_invoice_number: Optional[str] = None
    payment: Optional[Payment] = None
    delivery: Optional[Delivery] = None
    invoice_lines: Optional[List[InvoiceLine]] = None
    total_discount_amount: Optional[float] = None
    total_sales_amount: Optional[float] = None
    net_amount: Optional[float] = None
    tax_totals: Optional[List[TaxTotal]] = None
    total_amount: Optional[float] = None
    extra_discount_amount: Optional[float] = None
    total_items_discount_amount: Optional[float] = None

    @staticmethod
    def from_dict(obj: Any):
        assert isinstance(obj, dict)
        taxpayer_activity_code = from_union([from_str, from_none], obj.get("taxpayerActivityCode"))
        sales_order_reference = from_union([from_none, lambda x: int(from_str(x))], obj.get("salesOrderReference"))
        issuer = from_union([Issuer.from_dict, from_none], obj.get("issuer"))
        receiver = from_union([Issuer.from_dict, from_none], obj.get("receiver"))
        document_type = from_union([from_str, from_none], obj.get("documentType"))
        document_type_version = from_union([from_str, from_none], obj.get("documentTypeVersion"))
        date_time_issued = from_union([from_str, from_none], obj.get("dateTimeIssued"))
        internal_id = from_union([from_str, from_none], obj.get("internalID"))
        purchase_order_reference = from_union([from_str, from_none], obj.get("purchaseOrderReference"))
        purchase_order_description = from_union([from_str, from_none], obj.get("purchaseOrderDescription"))
        sales_order_description = from_union([from_str, from_none], obj.get("salesOrderDescription"))
        proforma_invoice_number = from_union([from_str, from_none], obj.get("proformaInvoiceNumber"))
        payment = from_union([Payment.from_dict, from_none], obj.get("payment"))
        delivery = from_union([Delivery.from_dict, from_none], obj.get("delivery"))
        invoice_lines = from_union([lambda x: from_list(InvoiceLine.from_dict, x), from_none], obj.get("invoiceLines"))
        total_discount_amount = from_union([from_float, from_none], obj.get("totalDiscountAmount"))
        total_sales_amount = from_union([from_float, from_none], obj.get("totalSalesAmount"))
        net_amount = from_union([from_float, from_none], obj.get("netAmount"))
        tax_totals = from_union([lambda x: from_list(TaxTotal.from_dict, x), from_none], obj.get("taxTotals"))
        total_amount = from_union([from_float, from_none], obj.get("totalAmount"))
        extra_discount_amount = from_union([from_float, from_none], obj.get("extraDiscountAmount"))
        total_items_discount_amount = from_union([from_float, from_none], obj.get("totalItemsDiscountAmount"))
        return Document(taxpayer_activity_code, sales_order_reference, issuer, receiver, document_type,
                        document_type_version, date_time_issued, internal_id, purchase_order_reference,
                        purchase_order_description, sales_order_description, proforma_invoice_number, payment, delivery,
                        invoice_lines, total_discount_amount, total_sales_amount, net_amount, tax_totals, total_amount,
                        extra_discount_amount, total_items_discount_amount)

    def to_dict(self) -> dict:
        result: dict = {}
        result["taxpayerActivityCode"] = from_union([from_str, from_none], self.taxpayer_activity_code)
        result["salesOrderReference"] = from_union([lambda x: from_none((lambda x: is_type(type(None), x))(x)),
                                                    lambda x: from_str(
                                                        (lambda x: str((lambda x: is_type(int, x))(x)))(x))],
                                                   self.sales_order_reference)
        result["issuer"] = from_union([lambda x: to_class(Issuer, x), from_none], self.issuer)
        result["receiver"] = from_union([lambda x: to_class(Issuer, x), from_none], self.receiver)
        result["documentType"] = from_union([from_str, from_none], self.document_type)
        result["documentTypeVersion"] = from_union([from_str, from_none], self.document_type_version)
        result["dateTimeIssued"] = from_union([from_str, from_none], self.date_time_issued)
        result["internalID"] = from_union([from_str, from_none], self.internal_id)
        result["purchaseOrderReference"] = from_union([from_str, from_none], self.purchase_order_reference)
        result["purchaseOrderDescription"] = from_union([from_str, from_none], self.purchase_order_description)
        result["salesOrderDescription"] = from_union([from_str, from_none], self.sales_order_description)
        result["proformaInvoiceNumber"] = from_union([from_str, from_none], self.proforma_invoice_number)
        result["payment"] = from_union([lambda x: to_class(Payment, x), from_none], self.payment)
        result["delivery"] = from_union([lambda x: to_class(Delivery, x), from_none], self.delivery)
        result["invoiceLines"] = from_union([lambda x: from_list(lambda x: to_class(InvoiceLine, x), x), from_none],
                                            self.invoice_lines)
        result["totalDiscountAmount"] = from_union([to_float, from_none], self.total_discount_amount)
        result["totalSalesAmount"] = from_union([to_float, from_none], self.total_sales_amount)
        result["netAmount"] = from_union([to_float, from_none], self.net_amount)
        result["taxTotals"] = from_union([lambda x: from_list(lambda x: to_class(TaxTotal, x), x), from_none],
                                         self.tax_totals)
        result["totalAmount"] = from_union([to_float, from_none], self.total_amount)
        result["extraDiscountAmount"] = from_union([from_float, from_none], self.extra_discount_amount)
        result["totalItemsDiscountAmount"] = from_union([from_float, from_none], self.total_items_discount_amount)
        return result


@dataclass
class Invoice:
    documents: Optional[List[Document]] = None

    @staticmethod
    def from_dict(obj: Any):
        assert isinstance(obj, dict)
        documents = from_union([lambda x: from_list(Document.from_dict, x), from_none], obj.get("documents"))
        return Invoice(documents)

    def to_dict(self) -> dict:
        result: dict = {}
        result["documents"] = from_union([lambda x: from_list(lambda x: to_class(Document, x), x), from_none],
                                         self.documents)
        return result


def invoice_from_dict(s: Any) -> Invoice:
    return Invoice.from_dict(s)


def invoice_to_dict(x: Invoice) -> Any:
    return to_class(Invoice, x)


def remove_none(obj):
    if isinstance(obj, (list, tuple, set)):
        return type(obj)(remove_none(x) for x in obj if x is not None)
    elif isinstance(obj, dict):
        return type(obj)((remove_none(k), remove_none(v))
                         for k, v in obj.items() if k is not None and v is not None)
    else:
        return obj