from marshmallow import Schema, fields

class CartWoodItemSchema(Schema):
    code = fields.String(required=True)
    quantity = fields.Integer(required=True, validate=lambda x: x > 0)

class CartWoodUpdateSchema(Schema):
    code = fields.String(required=True)
    quantity = fields.Integer(required=True, validate=lambda x: x >= 0)

class CartWoodResponseSchema(Schema):
    code = fields.String()
    shape = fields.String()
    dimensions = fields.String()
    quantity = fields.Integer()
    images = fields.String()
