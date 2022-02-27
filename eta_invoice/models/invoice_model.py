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

from datetime import datetime
import dateutil.parser


def from_str(x):
    assert isinstance(x, str)
    return x


def from_datetime(x):
    return dateutil.parser.parse(x)


def from_float(x):
    assert isinstance(x, (float, int)) and not isinstance(x, bool)
    return float(x)


def to_float(x):
    assert isinstance(x, float)
    return x


def from_int(x):
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def from_list(f, x):
    assert isinstance(x, list)
    return [f(y) for y in x]


def to_class(c, x):
    assert isinstance(x, c)
    return x.to_dict()


def from_none(x):
    assert x is None
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except:
            pass
    assert False


def is_type(t, x):
    assert isinstance(x, t)
    return x


class Delivery:
    def __init__(self, approach, packaging, date_validity, export_port, country_of_origin, gross_weight, net_weight, terms):
        self.approach = approach
        self.packaging = packaging
        self.date_validity = date_validity
        self.export_port = export_port
        self.country_of_origin = country_of_origin
        self.gross_weight = gross_weight
        self.net_weight = net_weight
        self.terms = terms

    @staticmethod
    def from_dict(obj):
        assert isinstance(obj, dict)
        approach = from_str(obj.get("approach"))
        packaging = from_str(obj.get("packaging"))
        date_validity = from_datetime(obj.get("dateValidity"))
        export_port = from_str(obj.get("exportPort"))
        country_of_origin = from_str(obj.get("countryOfOrigin"))
        gross_weight = from_float(obj.get("grossWeight"))
        net_weight = from_float(obj.get("netWeight"))
        terms = from_str(obj.get("terms"))
        return Delivery(approach, packaging, date_validity, export_port, country_of_origin, gross_weight, net_weight, terms)

    def to_dict(self):
        result = {}
        result["approach"] = from_str(self.approach)
        result["packaging"] = from_str(self.packaging)
        result["dateValidity"] = self.date_validity.isoformat()
        result["exportPort"] = from_str(self.export_port)
        result["countryOfOrigin"] = from_str(self.country_of_origin)
        result["grossWeight"] = to_float(self.gross_weight)
        result["netWeight"] = to_float(self.net_weight)
        result["terms"] = from_str(self.terms)
        return result


class Discount:
    def __init__(self, rate, amount):
        self.rate = rate
        self.amount = amount

    @staticmethod
    def from_dict(obj):
        assert isinstance(obj, dict)
        rate = from_int(obj.get("rate"))
        amount = from_float(obj.get("amount"))
        return Discount(rate, amount)

    def to_dict(self):
        result = {}
        result["rate"] = from_int(self.rate)
        result["amount"] = to_float(self.amount)
        return result


class TaxableItem:
    def __init__(self, tax_type, amount, sub_type, rate):
        self.tax_type = tax_type
        self.amount = amount
        self.sub_type = sub_type
        self.rate = rate

    @staticmethod
    def from_dict(obj):
        assert isinstance(obj, dict)
        tax_type = from_str(obj.get("taxType"))
        amount = from_float(obj.get("amount"))
        sub_type = from_str(obj.get("subType"))
        rate = from_int(obj.get("rate"))
        return TaxableItem(tax_type, amount, sub_type, rate)

    def to_dict(self):
        result = {}
        result["taxType"] = from_str(self.tax_type)
        result["amount"] = to_float(self.amount)
        result["subType"] = from_str(self.sub_type)
        result["rate"] = from_int(self.rate)
        return result


class UnitValue:
    def __init__(self, currency_sold, amount_egp, amount_sold, currency_exchange_rate):
        self.currency_sold = currency_sold
        self.amount_egp = amount_egp
        self.amount_sold = amount_sold
        self.currency_exchange_rate = currency_exchange_rate

    @staticmethod
    def from_dict(obj):
        assert isinstance(obj, dict)
        currency_sold = from_str(obj.get("currencySold"))
        amount_egp = from_float(obj.get("amountEGP"))
        amount_sold = from_int(obj.get("amountSold"))
        currency_exchange_rate = from_float(obj.get("currencyExchangeRate"))
        return UnitValue(currency_sold, amount_egp, amount_sold, currency_exchange_rate)

    def to_dict(self):
        result = {}
        result["currencySold"] = from_str(self.currency_sold)
        result["amountEGP"] = to_float(self.amount_egp)
        result["amountSold"] = from_int(self.amount_sold)
        result["currencyExchangeRate"] = to_float(self.currency_exchange_rate)
        return result


class InvoiceLine:
    def __init__(self, description, item_type, item_code, unit_type, quantity, internal_code, sales_total, total, value_difference, total_taxable_fees, net_total, items_discount, unit_value, discount, taxable_items):
        self.description = description
        self.item_type = item_type
        self.item_code = item_code
        self.unit_type = unit_type
        self.quantity = quantity
        self.internal_code = internal_code
        self.sales_total = sales_total
        self.total = total
        self.value_difference = value_difference
        self.total_taxable_fees = total_taxable_fees
        self.net_total = net_total
        self.items_discount = items_discount
        self.unit_value = unit_value
        self.discount = discount
        self.taxable_items = taxable_items

    @staticmethod
    def from_dict(obj):
        assert isinstance(obj, dict)
        description = from_str(obj.get("description"))
        item_type = from_str(obj.get("itemType"))
        item_code = int(from_str(obj.get("itemCode")))
        unit_type = from_str(obj.get("unitType"))
        quantity = from_int(obj.get("quantity"))
        internal_code = from_str(obj.get("internalCode"))
        sales_total = from_float(obj.get("salesTotal"))
        total = from_float(obj.get("total"))
        value_difference = from_int(obj.get("valueDifference"))
        total_taxable_fees = from_float(obj.get("totalTaxableFees"))
        net_total = from_float(obj.get("netTotal"))
        items_discount = from_int(obj.get("itemsDiscount"))
        unit_value = UnitValue.from_dict(obj.get("unitValue"))
        discount = Discount.from_dict(obj.get("discount"))
        taxable_items = from_list(TaxableItem.from_dict, obj.get("taxableItems"))
        return InvoiceLine(description, item_type, item_code, unit_type, quantity, internal_code, sales_total, total, value_difference, total_taxable_fees, net_total, items_discount, unit_value, discount, taxable_items)

    def to_dict(self):
        result = {}
        result["description"] = from_str(self.description)
        result["itemType"] = from_str(self.item_type)
        result["itemCode"] = from_str(str(self.item_code))
        result["unitType"] = from_str(self.unit_type)
        result["quantity"] = from_int(self.quantity)
        result["internalCode"] = from_str(self.internal_code)
        result["salesTotal"] = to_float(self.sales_total)
        result["total"] = to_float(self.total)
        result["valueDifference"] = from_int(self.value_difference)
        result["totalTaxableFees"] = to_float(self.total_taxable_fees)
        result["netTotal"] = to_float(self.net_total)
        result["itemsDiscount"] = from_int(self.items_discount)
        result["unitValue"] = to_class(UnitValue, self.unit_value)
        result["discount"] = to_class(Discount, self.discount)
        result["taxableItems"] = from_list(lambda x: to_class(TaxableItem, x), self.taxable_items)
        return result


class Address:
    def __init__(self, branch_id, country, governate, region_city, street, building_number, postal_code, floor, room, landmark, additional_information):
        self.branch_id = branch_id
        self.country = country
        self.governate = governate
        self.region_city = region_city
        self.street = street
        self.building_number = building_number
        self.postal_code = postal_code
        self.floor = floor
        self.room = room
        self.landmark = landmark
        self.additional_information = additional_information

    @staticmethod
    def from_dict(obj):
        assert isinstance(obj, dict)
        branch_id = from_union([from_none, lambda x: int(from_str(x))], obj.get("branchID"))
        country = from_str(obj.get("country"))
        governate = from_str(obj.get("governate"))
        region_city = from_str(obj.get("regionCity"))
        street = from_str(obj.get("street"))
        building_number = from_str(obj.get("buildingNumber"))
        postal_code = int(from_str(obj.get("postalCode")))
        floor = int(from_str(obj.get("floor")))
        room = int(from_str(obj.get("room")))
        landmark = from_str(obj.get("landmark"))
        additional_information = from_str(obj.get("additionalInformation"))
        return Address(branch_id, country, governate, region_city, street, building_number, postal_code, floor, room, landmark, additional_information)

    def to_dict(self):
        result = {}
        result["branchID"] = from_union([lambda x: from_none((lambda x: is_type(type(None), x))(x)), lambda x: from_str((lambda x: str((lambda x: is_type(int, x))(x)))(x))], self.branch_id)
        result["country"] = from_str(self.country)
        result["governate"] = from_str(self.governate)
        result["regionCity"] = from_str(self.region_city)
        result["street"] = from_str(self.street)
        result["buildingNumber"] = from_str(self.building_number)
        result["postalCode"] = from_str(str(self.postal_code))
        result["floor"] = from_str(str(self.floor))
        result["room"] = from_str(str(self.room))
        result["landmark"] = from_str(self.landmark)
        result["additionalInformation"] = from_str(self.additional_information)
        return result


class Issuer:
    def __init__(self, address, type, id, name):
        self.address = address
        self.type = type
        self.id = id
        self.name = name

    @staticmethod
    def from_dict(obj):
        assert isinstance(obj, dict)
        address = Address.from_dict(obj.get("address"))
        type = from_str(obj.get("type"))
        id = int(from_str(obj.get("id")))
        name = from_str(obj.get("name"))
        return Issuer(address, type, id, name)

    def to_dict(self):
        result = {}
        result["address"] = to_class(Address, self.address)
        result["type"] = from_str(self.type)
        result["id"] = from_str(str(self.id))
        result["name"] = from_str(self.name)
        return result


class Payment:
    def __init__(self, bank_name, bank_address, bank_account_no, bank_account_iban, swift_code, terms):
        self.bank_name = bank_name
        self.bank_address = bank_address
        self.bank_account_no = bank_account_no
        self.bank_account_iban = bank_account_iban
        self.swift_code = swift_code
        self.terms = terms

    @staticmethod
    def from_dict(obj):
        assert isinstance(obj, dict)
        bank_name = from_str(obj.get("bankName"))
        bank_address = from_str(obj.get("bankAddress"))
        bank_account_no = from_str(obj.get("bankAccountNo"))
        bank_account_iban = from_str(obj.get("bankAccountIBAN"))
        swift_code = from_str(obj.get("swiftCode"))
        terms = from_str(obj.get("terms"))
        return Payment(bank_name, bank_address, bank_account_no, bank_account_iban, swift_code, terms)

    def to_dict(self):
        result = {}
        result["bankName"] = from_str(self.bank_name)
        result["bankAddress"] = from_str(self.bank_address)
        result["bankAccountNo"] = from_str(self.bank_account_no)
        result["bankAccountIBAN"] = from_str(self.bank_account_iban)
        result["swiftCode"] = from_str(self.swift_code)
        result["terms"] = from_str(self.terms)
        return result


class TaxTotal:
    def __init__(self, tax_type, amount):
        self.tax_type = tax_type
        self.amount = amount

    @staticmethod
    def from_dict(obj):
        assert isinstance(obj, dict)
        tax_type = from_str(obj.get("taxType"))
        amount = from_float(obj.get("amount"))
        return TaxTotal(tax_type, amount)

    def to_dict(self):
        result = {}
        result["taxType"] = from_str(self.tax_type)
        result["amount"] = to_float(self.amount)
        return result


class Document:
    def __init__(self, issuer, receiver, document_type, document_type_version, date_time_issued, taxpayer_activity_code, internal_id, purchase_order_reference, purchase_order_description, sales_order_reference, sales_order_description, proforma_invoice_number, payment, delivery, invoice_lines, total_discount_amount, total_sales_amount, net_amount, tax_totals, total_amount, extra_discount_amount, total_items_discount_amount):
        self.issuer = issuer
        self.receiver = receiver
        self.document_type = document_type
        self.document_type_version = document_type_version
        self.date_time_issued = date_time_issued
        self.taxpayer_activity_code = taxpayer_activity_code
        self.internal_id = internal_id
        self.purchase_order_reference = purchase_order_reference
        self.purchase_order_description = purchase_order_description
        self.sales_order_reference = sales_order_reference
        self.sales_order_description = sales_order_description
        self.proforma_invoice_number = proforma_invoice_number
        self.payment = payment
        self.delivery = delivery
        self.invoice_lines = invoice_lines
        self.total_discount_amount = total_discount_amount
        self.total_sales_amount = total_sales_amount
        self.net_amount = net_amount
        self.tax_totals = tax_totals
        self.total_amount = total_amount
        self.extra_discount_amount = extra_discount_amount
        self.total_items_discount_amount = total_items_discount_amount

    @staticmethod
    def from_dict(obj):
        assert isinstance(obj, dict)
        issuer = Issuer.from_dict(obj.get("issuer"))
        receiver = Issuer.from_dict(obj.get("receiver"))
        document_type = from_str(obj.get("documentType"))
        document_type_version = from_str(obj.get("documentTypeVersion"))
        date_time_issued = from_datetime(obj.get("dateTimeIssued"))
        taxpayer_activity_code = int(from_str(obj.get("taxpayerActivityCode")))
        internal_id = from_str(obj.get("internalID"))
        purchase_order_reference = from_str(obj.get("purchaseOrderReference"))
        purchase_order_description = from_str(obj.get("purchaseOrderDescription"))
        sales_order_reference = int(from_str(obj.get("salesOrderReference")))
        sales_order_description = from_str(obj.get("salesOrderDescription"))
        proforma_invoice_number = from_str(obj.get("proformaInvoiceNumber"))
        payment = Payment.from_dict(obj.get("payment"))
        delivery = Delivery.from_dict(obj.get("delivery"))
        invoice_lines = from_list(InvoiceLine.from_dict, obj.get("invoiceLines"))
        total_discount_amount = from_float(obj.get("totalDiscountAmount"))
        total_sales_amount = from_float(obj.get("totalSalesAmount"))
        net_amount = from_float(obj.get("netAmount"))
        tax_totals = from_list(TaxTotal.from_dict, obj.get("taxTotals"))
        total_amount = from_float(obj.get("totalAmount"))
        extra_discount_amount = from_int(obj.get("extraDiscountAmount"))
        total_items_discount_amount = from_int(obj.get("totalItemsDiscountAmount"))
        return Document(issuer, receiver, document_type, document_type_version, date_time_issued, taxpayer_activity_code, internal_id, purchase_order_reference, purchase_order_description, sales_order_reference, sales_order_description, proforma_invoice_number, payment, delivery, invoice_lines, total_discount_amount, total_sales_amount, net_amount, tax_totals, total_amount, extra_discount_amount, total_items_discount_amount)

    def to_dict(self):
        result = {}
        result["issuer"] = to_class(Issuer, self.issuer)
        result["receiver"] = to_class(Issuer, self.receiver)
        result["documentType"] = from_str(self.document_type)
        result["documentTypeVersion"] = from_str(self.document_type_version)
        result["dateTimeIssued"] = self.date_time_issued.isoformat()
        result["taxpayerActivityCode"] = from_str(str(self.taxpayer_activity_code))
        result["internalID"] = from_str(self.internal_id)
        result["purchaseOrderReference"] = from_str(self.purchase_order_reference)
        result["purchaseOrderDescription"] = from_str(self.purchase_order_description)
        result["salesOrderReference"] = from_str(str(self.sales_order_reference))
        result["salesOrderDescription"] = from_str(self.sales_order_description)
        result["proformaInvoiceNumber"] = from_str(self.proforma_invoice_number)
        result["payment"] = to_class(Payment, self.payment)
        result["delivery"] = to_class(Delivery, self.delivery)
        result["invoiceLines"] = from_list(lambda x: to_class(InvoiceLine, x), self.invoice_lines)
        result["totalDiscountAmount"] = to_float(self.total_discount_amount)
        result["totalSalesAmount"] = to_float(self.total_sales_amount)
        result["netAmount"] = to_float(self.net_amount)
        result["taxTotals"] = from_list(lambda x: to_class(TaxTotal, x), self.tax_totals)
        result["totalAmount"] = to_float(self.total_amount)
        result["extraDiscountAmount"] = from_int(self.extra_discount_amount)
        result["totalItemsDiscountAmount"] = from_int(self.total_items_discount_amount)
        return result


class Invoice:
    def __init__(self, documents):
        self.documents = documents

    @staticmethod
    def from_dict(obj):
        assert isinstance(obj, dict)
        documents = from_list(Document.from_dict, obj.get("documents"))
        return Invoice(documents)

    def to_dict(self):
        result = {}
        result["documents"] = from_list(lambda x: to_class(Document, x), self.documents)
        return result


def invoice_from_dict(s):
    return Invoice.from_dict(s)


def invoice_to_dict(x):
    return to_class(Invoice, x)
