from marshmallow import Schema, fields

class CartItemSchema(Schema):
    code = fields.String(required=True)
    quantity = fields.Integer(required=True, validate=lambda x: x > 0)

class CartUpdateSchema(Schema):
    code = fields.String(required=True)
    quantity = fields.Integer(required=True, validate=lambda x: x >= 0)

class CartResponseSchema(Schema):
    code = fields.String()
    shape = fields.String()
    dimensions = fields.String()
    quantity = fields.Integer()
    images = fields.String()
