# schemas/testcase_schema.py
from marshmallow import Schema, fields, validates, ValidationError, pre_load
from utils.logger import get_logger

logger = get_logger("Schema")
PLATFORMS = {"LLM": "LLM", "WEB": "Web", "MOBILE": "Mobile", "API": "API"}

def normalize_platform(value):
    if not isinstance(value, str):
        raise ValidationError("platform must be a string")
    v = value.strip()
    # allow common variants, case-insensitive
    for key in PLATFORMS:
        if v.upper() == key:
            return PLATFORMS[key]
    # accept lowercase tokens
    vl = v.lower()
    for _, token in PLATFORMS.items():
        if vl == token.lower():
            return token
    raise ValidationError(f"platform must be one of {list(PLATFORMS.values())}")

def normalize_automated(value):
    # accept boolean or "yes"/"no"
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        val = value.strip().lower()
        if val in ("yes", "y", "true", "1"):
            return True
        if val in ("no", "n", "false", "0"):
            return False
    raise ValidationError("Automated must be boolean or 'yes'/'no'")

class TestCaseSchema(Schema):
    vuln_id = fields.Str(required=True)
    vuln_name = fields.Str(required=True)
    platform = fields.Str(required=True)
    analysis_type = fields.Str(required=False)
    owasp_ref = fields.Str(required=False)
    compliance = fields.Str(required=False)
    vuln_abstract = fields.Str(required=False)
    description = fields.Str(required=False)
    recommendation = fields.Str(required=False)
    example = fields.Str(required=False)
    cvss_score = fields.Str(required=False, allow_none=True)
    automated = fields.Raw(required=False, allow_none=True)
    severity = fields.Str(required=False)
    @pre_load
    def normalize(self, data, **kwargs):
        # normalize platform if present
        if "platform" in data and data["platform"] is not None:
            data["platform"] = normalize_platform(data["platform"])
        if "Automated" in data and data["Automated"] is not None:
            data["Automated"] = normalize_automated(data["Automated"])
        return data

    # @validates("cvss_score")
    # def validate_cvss(self, value):
    #     if value is None or "":
    #         return
    #     if not (0.0 <= float(value) <= 10.0):
    #         raise ValidationError("cvss_score must be between 0.0 and 10.0")

# ------------------------------------------------------------------------------
# Input Schema
# ------------------------------------------------------------------------------

class GenerateSchema(Schema):
    vuln_name = fields.Str(required=True)
    platform = fields.Str(required=True)

    @validates("platform")
    def validate_platform(self, value, **kwargs):
        allowed = {"LLM", "Web", "Mobile", "API"}

        if value not in allowed:
            logger.info(f"Not allowed: {value}")
            raise ValidationError(f"platform must be one of {sorted(list(allowed))}")

