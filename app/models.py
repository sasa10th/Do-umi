from datetime import datetime, date
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    student_id = db.Column(db.String(20), unique=True, nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    room_number = db.Column(db.String(10), nullable=True)
    grade = db.Column(db.Integer, nullable=True)  # 학년
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 전자서명 이미지 (base64 또는 파일경로)
    signature = db.Column(db.Text, nullable=True)

    # 관계
    penalties = db.relationship('Penalty', backref='student', lazy='dynamic',
                                foreign_keys='Penalty.student_id')
    
    # [수정됨] Exemption 테이블에 student_id와 granted_by_id 두 개의 User 외래키가 있으므로, 
    # student 관계가 어떤 키를 사용하는지 명시해야 합니다.
    exemptions = db.relationship('Exemption', 
                                backref='student', 
                                lazy='dynamic',
                                foreign_keys='Exemption.student_id')

    @property
    def password(self):
        raise AttributeError('password is not readable')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def total_penalty_points(self):
        """현재 유효한 벌점 합계"""
        total = sum(p.points for p in self.penalties if not p.is_cancelled)
        total_merit = sum(p.merit_points for p in self.penalties if not p.is_cancelled)
        return max(0, total - total_merit)

    @property
    def total_merit_points(self):
        return sum(p.merit_points for p in self.penalties if not p.is_cancelled)

    @property
    def stage(self):
        """벌점 단계 계산 (기준표 기반)"""
        pts = self.total_penalty_points
        if pts < 5:
            return 1
        elif pts < 10:
            return 2
        elif pts < 15:
            return 3
        else:
            return 4

    @property
    def exemption_count(self):
        return self.exemptions.filter_by(is_used=False).count()

    def __repr__(self):
        return f'<User {self.email}>'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Penalty(db.Model):
    __tablename__ = 'penalties'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    issued_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    date = db.Column(db.Date, default=date.today, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # 생활규정, 학업규정, 생활불량 등
    reason = db.Column(db.String(200), nullable=False)
    points = db.Column(db.Integer, default=0)  # 벌점
    merit_points = db.Column(db.Integer, default=0)  # 상점
    is_cancelled = db.Column(db.Boolean, default=False)
    is_confirmed = db.Column(db.Boolean, default=False)  # 전자서명 확인 여부
    student_signature = db.Column(db.Text, nullable=True)  # 학생 전자서명
    confirmed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    issued_by = db.relationship('User', foreign_keys=[issued_by_id])

    def __repr__(self):
        return f'<Penalty {self.id}: {self.reason} ({self.points}점)>'


class Document(db.Model):
    """천자문 기한 관리"""
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    doc_type = db.Column(db.String(50), nullable=False)  # 천자문 등
    due_date = db.Column(db.Date, nullable=False)
    original_due_date = db.Column(db.Date, nullable=True)  # 연기 전 기한
    is_submitted = db.Column(db.Boolean, default=False)
    is_extended = db.Column(db.Boolean, default=False)
    submitted_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship('User', backref='documents', foreign_keys=[student_id])

    @property
    def days_remaining(self):
        delta = self.due_date - date.today()
        return delta.days

    @property
    def is_overdue(self):
        return date.today() > self.due_date and not self.is_submitted

    def __repr__(self):
        return f'<Document {self.title} due {self.due_date}>'


class Exemption(db.Model):
    """천자문 면제권"""
    __tablename__ = 'exemptions'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    granted_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    is_used = db.Column(db.Boolean, default=False)
    used_for_document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=True)
    used_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    note = db.Column(db.String(200), nullable=True)

    # 이 관계들은 위 User 모델의 설정을 보조합니다.
    # student_id를 사용하는 관계는 User.exemptions와 연결됩니다.
    granted_by = db.relationship('User', foreign_keys=[granted_by_id])
    used_for_document = db.relationship('Document', foreign_keys=[used_for_document_id])

    def __repr__(self):
        return f'<Exemption {self.id} used={self.is_used}>'


class Notification(db.Model):
    """알림 내역"""
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    ntype = db.Column(db.String(50), default='info')  # info, warning, danger
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='notifications', foreign_keys=[user_id])

    def __repr__(self):
        return f'<Notification {self.title}>'


class PenaltyStandard(db.Model):
    """벌점 기준표"""
    __tablename__ = 'penalty_standards'

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    sub_category = db.Column(db.String(100), nullable=True)
    description = db.Column(db.String(200), nullable=False)
    penalty_points = db.Column(db.Integer, default=0)
    merit_points = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Standard {self.description}: {self.penalty_points}점>'