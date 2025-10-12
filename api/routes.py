# api/routes.py
from flask import Blueprint, request, jsonify, current_app
from pymongo import errors
from bson import json_util
from schemas.testcase_schema import TestCaseSchema
from utils.db import get_collection

bp = Blueprint("api", __name__, url_prefix="/api/v1")
schema = TestCaseSchema()

@bp.route("/test_cases", methods=["GET"])
def read_test_cases():
    """
    Read test cases by platform
    ---
    parameters:
      - name: platform
        in: query
        type: string
        required: false
        description: Platform filter (LLM, web, mobile, API)
    responses:
      200:
        description: list of test cases
    """
    coll = get_collection()
    platform = request.args.get("platform")
    query = {}
    if platform:
        # rely on normalization similar to schema
        try:
            # reuse schema's normalization by calling load on a fake payload
            validated = schema.load({"vuln_id": "TCS_DUMMY_1", "vuln_name": "dummy", "platform": platform})
            # we only use normalized platform value
            normalized_platform = validated["platform"]
            query["platform"] = normalized_platform
        except Exception:
            return jsonify({"error": "Invalid platform value"}), 400
    try:
        docs = list(coll.find(query))
        return current_app.response_class(response=json_util.dumps({"test_cases": docs}), status=200, mimetype="application/json")
    except errors.PyMongoError:
        return jsonify({"error": "Database read error"}), 500

@bp.route("/test_cases", methods=["POST"])
def add_test_cases():
    """
    Add one or multiple test cases
    ---
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        schema:
          oneOf:
            - $ref: '#/definitions/TestCase'
            - type: array
              items:
                $ref: '#/definitions/TestCase'
    responses:
      201:
        description: Inserted
      400:
        description: Validation error
    """
    coll = get_collection()
    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({"error": "Invalid or missing JSON"}), 400

    # normalize to list
    items = []
    if isinstance(payload, dict) and "test_cases" in payload and isinstance(payload["test_cases"], list):
        items = payload["test_cases"]
    elif isinstance(payload, list):
        items = payload
    elif isinstance(payload, dict):
        items = [payload]
    else:
        return jsonify({"error": "Payload must be an object or array"}), 400

    clean_docs = []
    for item in items:
        try:
            validated = schema.load(item)
            clean_docs.append(validated)
        except Exception as e:
            return jsonify({"error": "Validation failed", "message": str(e), "item": item}), 400

    try:
        if len(clean_docs) == 1:
            coll.insert_one(clean_docs[0])
            return jsonify({"inserted": 1, "vuln_id": clean_docs[0]["vuln_id"]}), 201
        else:
            result = coll.insert_many(clean_docs, ordered=False)
            return jsonify({"inserted": len(result.inserted_ids)}), 201
    except errors.BulkWriteError as bwe:
        return jsonify({"error": "Bulk write error", "details": bwe.details}), 409
    except errors.DuplicateKeyError:
        return jsonify({"error": "Duplicate vuln_id detected"}), 409
    except errors.PyMongoError:
        return jsonify({"error": "Database write error"}), 500

@bp.route("/test_cases", methods=["PUT"])
def update_test_cases():
    """
    Update one or multiple test cases by vuln_id (partial update)
    ---
    consumes:
      - application/json
    responses:
      200:
        description: update processed
    """
    coll = get_collection()
    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({"error": "Invalid or missing JSON"}), 400

    items = []
    if isinstance(payload, dict) and "test_cases" in payload and isinstance(payload["test_cases"], list):
        items = payload["test_cases"]
    elif isinstance(payload, list):
        items = payload
    elif isinstance(payload, dict) and "vuln_id" in payload:
        items = [payload]
    else:
        return jsonify({"error": "Payload must be object/array or contain vuln_id"}), 400

    results = {"updated": 0, "not_found": []}
    for item in items:
        if "vuln_id" not in item:
            return jsonify({"error": "Each update object must include vuln_id", "item": item}), 400
        vuln_id = item["vuln_id"]
        # ensure incoming fields are valid except vuln_id
        up = dict(item)
        up.pop("vuln_id")
        if not up:
            continue
        # validate partial update by merging with minimal required fields (schema requires vuln_id & vuln_name)
        # create dummy payload to run normalization and validation for fields present
        dummy = {"vuln_id": vuln_id, "vuln_name": "DUMMY_NAME"}
        dummy.update(up)
        try:
            validated = schema.load(dummy)
            # only keep fields that were actually in the user payload (not dummy)
            for k in list(validated.keys()):
                if k in ("vuln_id","vuln_name") and k not in item:
                    # remove dummy-required fields if they were not provided originally
                    validated.pop(k,None)
            update_doc = {k: v for k, v in validated.items() if k in item and k != "vuln_id"}
        except Exception as e:
            return jsonify({"error": "Validation failed for update", "message": str(e), "item": item}), 400

        try:
            res = coll.update_one({"vuln_id": vuln_id}, {"$set": update_doc})
            if res.matched_count == 0:
                results["not_found"].append(vuln_id)
            else:
                results["updated"] += 1
        except errors.PyMongoError:
            return jsonify({"error": f"Database update error for {vuln_id}"}), 500

    return jsonify(results), 200

@bp.route("/test_cases", methods=["DELETE"])
def delete_test_cases():
    """
    Delete one or multiple test cases by vuln_id
    ---
    consumes:
      - application/json
    responses:
      200:
        description: delete result
    """
    coll = get_collection()
    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({"error": "Invalid or missing JSON"}), 400

    vuln_ids = []
    if isinstance(payload, dict) and "vuln_ids" in payload and isinstance(payload["vuln_ids"], list):
        vuln_ids = payload["vuln_ids"]
    elif isinstance(payload, list):
        for p in payload:
            if isinstance(p, str):
                vuln_ids.append(p)
            elif isinstance(p, dict) and "vuln_id" in p:
                vuln_ids.append(p["vuln_id"])
    elif isinstance(payload, dict) and "test_cases" in payload:
        for tc in payload["test_cases"]:
            if isinstance(tc, dict) and "vuln_id" in tc:
                vuln_ids.append(tc["vuln_id"])
    elif isinstance(payload, dict) and "vuln_id" in payload:
        vuln_ids.append(payload["vuln_id"])
    else:
        return jsonify({"error": "Provide vuln_ids list or test_cases array or vuln_id"}), 400

    if not vuln_ids:
        return jsonify({"error": "No vuln_ids found to delete"}), 400

    try:
        res = coll.delete_many({"vuln_id": {"$in": vuln_ids}})
        return jsonify({"deleted_count": res.deleted_count}), 200
    except errors.PyMongoError:
        return jsonify({"error": "Database delete error"}), 500
