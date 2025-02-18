from marshmallow import Schema, fields

class CatalogQuerySchema(Schema):
    page = fields.Int(missing=1)
    items_per_page = fields.Int(missing=8)
    search = fields.Str(missing="")
    search_type = fields.Str(
        missing="name",
        validate=lambda x: x.lower() in ["name", "brand", "specs"] if x else True
    )