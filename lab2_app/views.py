from datetime import datetime
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from flask_jwt_extended import (
    jwt_required,
    create_access_token,
)
from passlib.hash import pbkdf2_sha256

from . import app, jwt
from . import Schemas
from .Models import db, User, Category, Record




@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return (
        jsonify({"message": "The token has expired.", "error": "token_expired"}),
        401,
    )


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return (
        jsonify(
            {"message": "Signature verification failed.", "error": "invalid_token"}
        ),
        401,
    )


@jwt.unauthorized_loader
def missing_token_callback(error):
    return (
        jsonify(
            {
                "description": "Request does not contain an access token.",
                "error": "authorization_required",
            }
        ),
        401,
    )




@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>", 200


@app.route("/healthcheck")
def health_check():
    return {"status": "OK", "timestamp": datetime.now()}, 200


@app.post("/register")
def register():
    try:
        body = Schemas.user_create_schema.load(request.get_json() or {})
    except ValidationError as e:
        return {"error": "invalid registration data", "details": e.messages}, 400

    user = User(
        name=body["name"],
        password=pbkdf2_sha256.hash(body["password"]),
    )
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        return {"error": "invalid registration data", "details": str(e.orig)}, 400

    return {"id": user.id, "user_name": user.name}, 201


@app.post("/login")
def login():
    try:
        body = Schemas.login_schema.load(request.get_json() or {})
    except ValidationError as e:
        return {"error": "invalid login data", "details": e.messages}, 400

    user = User.query.filter_by(name=body["name"]).first()
    if user is None or not pbkdf2_sha256.verify(body["password"], user.password):
        return {"error": "bad username or password"}, 401
    access_token = create_access_token(identity=str(user.id))
    return {"access_token": access_token}, 200




@app.get("/user/<int:user_id>")
@jwt_required()
def read_person(user_id: int):
    user = User.query.get(user_id)
    if user is None:
        return {"error": "user not found"}, 404
    return {"id": user.id, "user_name": user.name}, 200


@app.get("/users")
@jwt_required()
def read_people():
    users = User.query.order_by(User.id.asc()).all()
    return [{"id": u.id, "user_name": u.name} for u in users], 200


@app.post("/user")
@jwt_required()
def create_person():
    try:
        body = Schemas.user_create_schema.load(request.get_json() or {})
    except ValidationError as e:
        return {"error": "invalid user data", "details": e.messages}, 400

    user = User(
        name=body["name"],
        password=pbkdf2_sha256.hash(body["password"]),
    )
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        return {"error": "invalid user data", "details": str(e.orig)}, 400

    return {"id": user.id, "user_name": user.name}, 201


@app.delete("/user/<int:user_id>")
@jwt_required()
def drop_person(user_id: int):
    try:
        Schemas.user_id_path_schema.load({"user_id": user_id})
    except ValidationError as e:
        return {"error": "invalid user_id", "details": e.messages}, 400

    user = User.query.get(user_id)
    if user is None:
        return {"error": "user not found"}, 404

    name = user.name
    db.session.delete(user)
    db.session.commit()
    return {"result": f"id: {user_id} successfully deleted", "user_name": name}, 200


@app.get("/category")
@jwt_required()
def read_kinds():
    uid = request.args.get("user_id", type=int)
    raw = {}
    if uid is not None:
        raw["user_id"] = uid

    try:
        params = Schemas.category_query_schema.load(raw)
    except ValidationError as e:
        return {"error": "invalid query params", "details": e.messages}, 400

    uid = params.get("user_id")

    q = Category.query
    if uid is None:
        q = q.filter(Category.owner_id.is_(None))
    else:
        q = q.filter(Category.owner_id == uid)

    cats = q.order_by(Category.id.asc()).all()
    return [
        {
            "id": c.id,
            "category_name": c.name,
            "user_id": c.owner_id,
        }
        for c in cats
    ], 200


@app.post("/category")
@jwt_required()
def create_kind():
    try:
        body = Schemas.category_create_schema.load(request.get_json() or {})
    except ValidationError as e:
        return {"error": "invalid category data", "details": e.messages}, 400

    owner_id = body.get("user_id")

    if owner_id is not None:
        owner = User.query.get(owner_id)
        if owner is None:
            return {"error": "user not found"}, 404

    cat = Category(
        name=body["name"],
        owner_id=owner_id,
    )
    db.session.add(cat)
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        return {"error": "invalid category data", "details": str(e.orig)}, 400

    return {
        "id": cat.id,
        "category_name": cat.name,
        "user_id": cat.owner_id,
    }, 201


@app.delete("/category")
@jwt_required()
def drop_kind():
    try:
        body = Schemas.category_delete_schema.load(request.get_json() or {})
    except ValidationError as e:
        return {"error": "invalid category id", "details": e.messages}, 400

    cid = body["id"]
    cat = Category.query.get(cid)
    if cat is None:
        return {"error": "category not found"}, 404

    name = cat.name
    db.session.delete(cat)
    db.session.commit()
    return {"result": f"id: {cid} successfully deleted", "category_name": name}, 200


@app.get("/record/<int:record_id>")
@jwt_required()
def read_entry(record_id: int):
    try:
        Schemas.record_id_path_schema.load({"record_id": record_id})
    except ValidationError as e:
        return {"error": "invalid record_id", "details": e.messages}, 400

    rec = Record.query.get(record_id)
    if rec is None:
        return {"error": "record not found"}, 404

    return {
        "id": rec.id,
        "user_id": rec.user_id,
        "category_id": rec.category_id,
        "datetime": rec.datetime,
        "amount": str(rec.amount),
    }, 200


@app.delete("/record/<int:record_id>")
@jwt_required()
def drop_entry(record_id: int):
    try:
        Schemas.record_id_path_schema.load({"record_id": record_id})
    except ValidationError as e:
        return {"error": "invalid record_id", "details": e.messages}, 400

    rec = Record.query.get(record_id)
    if rec is None:
        return {"error": "record not found"}, 404

    deleted = {
        "id": rec.id,
        "user_id": rec.user_id,
        "category_id": rec.category_id,
        "datetime": rec.datetime,
        "amount": str(rec.amount),
    }

    db.session.delete(rec)
    db.session.commit()

    return {"result": f"id: {record_id} successfully deleted", "deleted": deleted}, 200


@app.post("/record")
@jwt_required()
def create_entry():
    try:
        body = Schemas.record_create_schema.load(request.get_json() or {})
    except ValidationError as e:
        return {"error": "invalid record data", "details": e.messages}, 400

    user = User.query.get(body["user_id"])
    if user is None:
        return {"error": "user not found"}, 404

    cat = Category.query.get(body["category_id"])
    if cat is None:
        return {"error": "category not found"}, 404

    if cat.owner_id is not None and cat.owner_id != user.id:
        return {"error": "category not available for this user"}, 403

    rec = Record(
        user_id=user.id,
        category_id=cat.id,
        datetime=body["datetime"],
        amount=float(body["amount"]),
    )
    db.session.add(rec)
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        return {"error": "invalid record data", "details": str(e.orig)}, 400

    return {
        "record_id": rec.id,
        "user_id": rec.user_id,
        "category_id": rec.category_id,
        "datetime": rec.datetime,
        "amount": str(rec.amount),
    }, 201


@app.get("/record")
@jwt_required()
def query_entries():
    uid = request.args.get("user_id", type=int)
    cid = request.args.get("category_id", type=int)
    if uid is None and cid is None:
        return {"error": "provide user_id and/or category_id"}, 400

    raw = {}
    if uid is not None:
        raw["user_id"] = uid
    if cid is not None:
        raw["category_id"] = cid

    try:
        params = Schemas.record_query_schema.load(raw)
    except ValidationError as e:
        return {"error": "invalid query params", "details": e.messages}, 400

    uid = params.get("user_id")
    cid = params.get("category_id")

    q = Record.query
    if uid is not None:
        q = q.filter(Record.user_id == uid)
    if cid is not None:
        q = q.filter(Record.category_id == cid)

    records = q.order_by(Record.datetime.desc(), Record.id.desc()).all()

    items = [
        {
            "id": r.id,
            "user_id": r.user_id,
            "category_id": r.category_id,
            "datetime": r.datetime,
            "amount": str(r.amount),
        }
        for r in records
    ]

    return {"items": items, "counter": len(items)}, 200
