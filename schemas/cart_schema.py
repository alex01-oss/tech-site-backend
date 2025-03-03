from marshmallow import Schema, fields

class CartItemSchema(Schema):
    article = fields.String(required=True)
    quantity = fields.Integer(required=True, validate=lambda x: x > 0)

class CartUpdateSchema(Schema):
    article = fields.String(required=True)
    quantity = fields.Integer(required=True, validate=lambda x: x >= 0)

class CartResponseSchema(Schema):
    article = fields.String()
    title = fields.String()
    price = fields.Float()
    quantity = fields.Integer()
    currency = fields.String()
