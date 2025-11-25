from decimal import Decimal, InvalidOperation
from marshmallow import Schema, fields, validate, validates, ValidationError, pre_load


def _strip_string(v):
    if isinstance(v, str):
        v = v.strip()
        if not v:
            raise ValidationError("string cannot be empty")
        return v
    raise ValidationError("string expected")


class BaseSchema(Schema):
    @pre_load
    def strip_all_strings(self, data, **kwargs):
        if isinstance(data, dict):
            for k, v in list(data.items()):
                if isinstance(v, str):
                    data[k] = v.strip()
        return data


class UserIdPathSchema(BaseSchema):
    user_id = fields.Integer(
        required=True,
        strict=True,
        validate=validate.Range(min=1),
        error_messages={"required": "user_id is required"},
    )


class UserCreateSchema(BaseSchema):
    name = fields.String(
        required=True,
        validate=[validate.Length(min=1, max=64)],
        error_messages={"required": "name is required"},
    )

    @pre_load
    def strip_name(self, data, **kwargs):
        if "name" in data:
            data["name"] = _strip_string(data["name"])
        return data


class CategoryCreateSchema(BaseSchema):
    name = fields.String(
        required=True,
        validate=[validate.Length(min=1, max=64)],
        error_messages={"required": "name is required"},
    )
    user_id = fields.Integer(
        required=False,
        strict=True,
        validate=validate.Range(min=1),
    )

    @pre_load
    def strip_name(self, data, **kwargs):
        if "name" in data:
            data["name"] = _strip_string(data["name"])
        return data


class CategoryDeleteSchema(BaseSchema):
    id = fields.Integer(
        required=True,
        strict=True,
        validate=validate.Range(min=1),
        error_messages={"required": "category id is required"},
    )


class CategoryQuerySchema(BaseSchema):
    user_id = fields.Integer(
        required=False,
        strict=True,
        validate=validate.Range(min=1),
    )


class RecordIdPathSchema(BaseSchema):
    record_id = fields.Integer(
        required=True,
        strict=True,
        validate=validate.Range(min=1),
        error_messages={"required": "record_id is required"},
    )
class RecordUserQuerySchema(BaseSchema):
    user_id = fields.Integer(
        required=True,
        strict=True,
        validate=validate.Range(min=1),
        error_messages={"required": "user_id is required"},
    )

class RecordCreateSchema(BaseSchema):
    user_id = fields.Integer(
        required=True,
        strict=True,
        validate=validate.Range(min=1),
        error_messages={"required": "user_id is required"},
    )
    category_id = fields.Integer(
        required=True,
        strict=True,
        validate=validate.Range(min=1),
        error_messages={"required": "category_id is required"},
    )
    datetime = fields.DateTime(
        required=True,
        format="iso",
        error_messages={"required": "datetime (ISO 8601) is required"},
    )
    amount = fields.String(
        required=True,
        error_messages={"required": "amount is required"},
    )

    @pre_load
    def normalize(self, data, **kwargs):
        if "amount" in data and isinstance(data["amount"], str):
            data["amount"] = data["amount"].strip()
        return data

    @validates("amount")
    def validate_amount(self, value):
        try:
            dec = Decimal(str(value))
        except (InvalidOperation, ValueError):
            raise ValidationError("amount must be a number")
        if dec == Decimal("NaN"):
            raise ValidationError("amount is invalid (NaN)")
        if dec <= Decimal("0"):
            raise ValidationError("amount must be > 0")


class RecordQuerySchema(BaseSchema):
    user_id = fields.Integer(
        required=False,
        strict=True,
        validate=validate.Range(min=1),
    )
    category_id = fields.Integer(
        required=False,
        strict=True,
        validate=validate.Range(min=1),
    )

record_user_query_schema = RecordUserQuerySchema()
user_id_path_schema = UserIdPathSchema()
user_create_schema = UserCreateSchema()
category_create_schema = CategoryCreateSchema()
category_delete_schema = CategoryDeleteSchema()
category_query_schema = CategoryQuerySchema()
record_id_path_schema = RecordIdPathSchema()
record_create_schema = RecordCreateSchema()
record_query_schema = RecordQuerySchema()
