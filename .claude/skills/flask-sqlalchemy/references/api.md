# REST API احترافي مع Flask

## هيكل API كامل

```python
from flask import Blueprint, jsonify, request
from app import db
from app.models import User
from sqlalchemy import or_

api = Blueprint('api', __name__)

# ===== Pagination Helper =====
def paginate_query(query, page, per_page=20):
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return {
        'items': [item.to_dict() for item in pagination.items],
        'pagination': {
            'page': pagination.page,
            'pages': pagination.pages,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }
```

## CRUD كامل مع Pagination وSearch

```python
@api.route('/users', methods=['GET'])
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'created_at')
    order = request.args.get('order', 'desc')

    query = User.query

    # بحث
    if search:
        query = query.filter(
            or_(
                User.username.ilike(f'%{search}%'),
                User.email.ilike(f'%{search}%')
            )
        )

    # ترتيب
    sort_column = getattr(User, sort_by, User.created_at)
    if order == 'desc':
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    return jsonify(paginate_query(query, page, per_page))


@api.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    user = db.session.get(User, id)
    if not user:
        return {'error': 'المستخدم غير موجود'}, 404
    return jsonify(user.to_dict())


@api.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    errors = validate_user_data(data)
    if errors:
        return {'errors': errors}, 422

    try:
        user = User(username=data['username'], email=data['email'])
        db.session.add(user)
        db.session.commit()
        return jsonify(user.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return {'error': 'خطأ في الخادم'}, 500


@api.route('/users/<int:id>', methods=['PUT', 'PATCH'])
def update_user(id):
    user = db.session.get(User, id)
    if not user:
        return {'error': 'المستخدم غير موجود'}, 404

    data = request.get_json()
    if 'username' in data:
        user.username = data['username']
    if 'email' in data:
        user.email = data['email']

    db.session.commit()
    return jsonify(user.to_dict())


@api.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = db.session.get(User, id)
    if not user:
        return {'error': 'المستخدم غير موجود'}, 404

    db.session.delete(user)
    db.session.commit()
    return '', 204
```

## Validation

```python
def validate_user_data(data, partial=False):
    errors = {}

    if not partial or 'username' in data:
        username = data.get('username', '')
        if not username:
            errors['username'] = 'اسم المستخدم مطلوب'
        elif len(username) < 3:
            errors['username'] = 'اسم المستخدم يجب أن يكون 3 أحرف على الأقل'
        elif User.query.filter_by(username=username).first():
            errors['username'] = 'اسم المستخدم مستخدم مسبقاً'

    if not partial or 'email' in data:
        email = data.get('email', '')
        if not email:
            errors['email'] = 'البريد الإلكتروني مطلوب'
        elif '@' not in email:
            errors['email'] = 'البريد الإلكتروني غير صحيح'

    return errors
```

## معالجة الأخطاء العامة

```python
# في __init__.py أو ملف منفصل
@app.errorhandler(404)
def not_found(e):
    return {'error': 'المورد غير موجود'}, 404

@app.errorhandler(405)
def method_not_allowed(e):
    return {'error': 'الطريقة غير مسموحة'}, 405

@app.errorhandler(422)
def unprocessable(e):
    return {'error': 'بيانات غير صالحة'}, 422

@app.errorhandler(500)
def server_error(e):
    return {'error': 'خطأ في الخادم'}, 500
```

## Flask-RESTful (الطريقة المنظمة)

```python
from flask_restful import Api, Resource, reqparse, fields, marshal_with

# تعريف شكل الاستجابة
user_fields = {
    'id': fields.Integer,
    'username': fields.String,
    'email': fields.String,
    'created_at': fields.DateTime(dt_format='iso8601')
}

# Parser للتحقق من المدخلات
user_parser = reqparse.RequestParser()
user_parser.add_argument('username', type=str, required=True, help='اسم المستخدم مطلوب')
user_parser.add_argument('email', type=str, required=True, help='البريد مطلوب')

class UserListResource(Resource):
    @marshal_with(user_fields)
    def get(self):
        return User.query.all()

    @marshal_with(user_fields)
    def post(self):
        args = user_parser.parse_args()
        user = User(username=args['username'], email=args['email'])
        db.session.add(user)
        db.session.commit()
        return user, 201

class UserResource(Resource):
    @marshal_with(user_fields)
    def get(self, id):
        return db.session.get(User, id) or ({'error': 'غير موجود'}, 404)

    def delete(self, id):
        user = db.session.get(User, id)
        if not user:
            return {'error': 'غير موجود'}, 404
        db.session.delete(user)
        db.session.commit()
        return '', 204

# التسجيل
api_ext = Api(api_blueprint)
api_ext.add_resource(UserListResource, '/users')
api_ext.add_resource(UserResource, '/users/<int:id>')
```

## رموز HTTP الشائعة

| الرمز | المعنى        | متى تستخدمه              |
| ----- | ------------- | ------------------------ |
| 200   | OK            | طلب ناجح                 |
| 201   | Created       | إنشاء سجل جديد           |
| 204   | No Content    | حذف ناجح                 |
| 400   | Bad Request   | بيانات مفقودة أو خاطئة   |
| 401   | Unauthorized  | يحتاج تسجيل دخول         |
| 403   | Forbidden     | لا يملك الصلاحية         |
| 404   | Not Found     | السجل غير موجود          |
| 409   | Conflict      | تعارض (مثل بيانات مكررة) |
| 422   | Unprocessable | فشل التحقق من البيانات   |
| 500   | Server Error  | خطأ غير متوقع            |
