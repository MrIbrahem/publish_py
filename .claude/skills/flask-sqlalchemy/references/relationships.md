# العلاقات بين الجداول في SQLAlchemy

## One-to-One (واحد لواحد)

```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    profile = db.relationship('Profile', backref='user', uselist=False)

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    bio = db.Column(db.Text)
    avatar_url = db.Column(db.String(255))

# الاستخدام
user.profile        # كائن Profile واحد
profile.user        # كائن User
```

## One-to-Many (واحد لكثير)

```python
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    products = db.relationship('Product', backref='category', lazy='dynamic')

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    name = db.Column(db.String(100))
    price = db.Column(db.Float)

# الاستخدام
category.products.all()           # جميع المنتجات
category.products.count()         # عدد المنتجات
category.products.filter_by(price=...).all()  # فلترة (lazy='dynamic' مطلوب)
product.category                  # التصنيف
```

## Many-to-Many (كثير لكثير)

```python
# الطريقة 1: جدول ربط بسيط
enrollments = db.Table('enrollments',
    db.Column('student_id', db.Integer, db.ForeignKey('students.id'), primary_key=True),
    db.Column('course_id', db.Integer, db.ForeignKey('courses.id'), primary_key=True)
)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    courses = db.relationship('Course', secondary=enrollments, backref='students')

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))

# الاستخدام
student.courses.append(course)   # تسجيل
student.courses.remove(course)   # إلغاء تسجيل
db.session.commit()
course.students                  # جميع الطلاب في الكورس
```

```python
# الطريقة 2: موديل ربط (عند الحاجة لبيانات إضافية)
class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), primary_key=True)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    grade = db.Column(db.Float)

    student = db.relationship('Student', backref='enrollments')
    course = db.relationship('Course', backref='enrollments')

# الاستخدام
enrollment = Enrollment(student_id=1, course_id=2, grade=95.0)
db.session.add(enrollment)
db.session.commit()

# جلب كل كورسات طالب مع الدرجات
for e in student.enrollments:
    print(e.course.title, e.grade)
```

## Self-Referential (علاقة مع نفس الجدول)

```python
# مثال: متابعة المستخدمين
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('users.id'))
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    followed = db.relationship(
        'User',
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'),
        lazy='dynamic'
    )

# الاستخدام
user.follow(other_user)    # يتابع
user.unfollow(other_user)  # يلغي متابعة
user.followed.all()        # من يتابعهم
user.followers.all()       # من يتابعونه
```

## خيارات lazy Loading

| القيمة       | الوصف                              | متى تستخدمها               |
| ------------ | ---------------------------------- | -------------------------- |
| `'select'`   | يحمّل البيانات عند الطلب (افتراضي) | معظم الحالات               |
| `'dynamic'`  | يعيد query قابل للفلترة            | عند الحاجة لـ filter/count |
| `'joined'`   | يحمّل مع الجدول الأصلي بـ JOIN     | عند الحاجة المتكررة        |
| `'subquery'` | يحمّل بـ subquery منفصل            | قوائم كبيرة                |

## Cascade — التأثير على السجلات المرتبطة

```python
# حذف تلقائي للسجلات المرتبطة
posts = db.relationship('Post', backref='author', cascade='all, delete-orphan')

# لا تحذف السجلات المرتبطة (الافتراضي)
posts = db.relationship('Post', backref='author')
```
