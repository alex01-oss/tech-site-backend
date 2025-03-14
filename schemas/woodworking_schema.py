from marshmallow import Schema, fields

class WoodWorkingQuerySchema(Schema):
    page = fields.Int(missing=1)
    items_per_page = fields.Int(missing=8)
    search = fields.Str(missing="")
    search_type = fields.Str(
        missing="name",
        validate=lambda x: x.lower() in ["code", "shape", "dimensions"] if x else True
    )