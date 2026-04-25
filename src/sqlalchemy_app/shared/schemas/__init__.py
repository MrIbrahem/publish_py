"""
Validation schemas using marshmallow.
"""

from flask import request
from marshmallow import Schema, ValidationError, fields, post_load, validate, validates


class PublishRequestSchema(Schema):
    """Schema for /publish/ endpoint request validation."""

    user = fields.Str(required=True, validate=validate.Length(min=1, max=120))
    title = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    text = fields.Str(required=True, validate=validate.Length(min=1))
    target = fields.Str(required=True, validate=validate.Length(min=2, max=10))
    sourcetitle = fields.Str(validate=validate.Length(max=255))
    revid = fields.Str(validate=validate.Length(max=50))
    revision = fields.Str(validate=validate.Length(max=50))
    campaign = fields.Str(validate=validate.Length(max=100))
    # translate_type = fields.Str(validate=validate.Length(max=50))
    translate_type = fields.Str(validate=validate.OneOf(["lead", "all"]))
    wpCaptchaId = fields.Str(validate=validate.Length(max=100))
    wpCaptchaWord = fields.Str(validate=validate.Length(max=50))

    @post_load
    def process_fields(self, data, **kwargs):
        """Clean up fields after load."""
        if "user" in data:
            data["user"] = data["user"].strip()
        if "title" in data:
            data["title"] = data["title"].strip()
        return data


class PublishReportsQuerySchema(Schema):
    """Schema for /api/publish_reports query parameters validation."""

    year = fields.Int(validate=validate.Range(min=2000, max=2100))
    month = fields.Int(validate=validate.Range(min=1, max=12))
    title = fields.Str(validate=validate.Length(max=255))
    user = fields.Str(validate=validate.Length(max=120))
    lang = fields.Str(validate=validate.Length(min=2, max=10))
    sourcetitle = fields.Str(validate=validate.Length(max=255))
    result = fields.Str(validate=validate.Length(max=50))
    select = fields.Str(validate=validate.Length(max=500))
    limit = fields.Int(validate=validate.Range(min=1, max=1000))

    # Special filter values
    ALLOWED_SPECIAL_VALUES = {"not_empty", "not_mt", "empty", "mt", ">0", "all"}

    @validates("result")
    def validate_result(self, value):
        if value and value not in self.ALLOWED_SPECIAL_VALUES and len(value) > 50:
            raise ValidationError("Invalid result value")
        return value


class CXTokenRequestSchema(Schema):
    """Schema for /cxtoken/ endpoint request validation."""

    wiki = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    user = fields.Str(required=True, validate=validate.Length(min=2, max=150))


def validate_json(schema_class):
    """Decorator to validate JSON request data using marshmallow schema."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            schema = schema_class()
            data = request.get_json(silent=True)

            if data is None:
                data = request.form.to_dict()

            if not data:
                from flask import jsonify

                response = jsonify({"error": "No data provided"})
                response.status_code = 400
                return response

            errors = schema.validate(data)
            if errors:
                from flask import jsonify

                response = jsonify({"error": errors})
                response.status_code = 400
                return response

            # Add validated data to request context
            request.validated_data = schema.load(data)
            return func(*args, **kwargs)

        wrapper.__name__ = func.__name__
        return wrapper

    return decorator


__all__ = [
    "PublishRequestSchema",
    "PublishReportsQuerySchema",
    "CXTokenRequestSchema",
    "validate_json",
]
