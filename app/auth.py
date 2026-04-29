from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from .models import User
from . import db

auth = Blueprint('auth', __name__)

ALLOWED_DOMAIN = 'sasa.hs.kr'


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)

        if not email or not password:
            flash('이메일과 비밀번호를 입력해주세요.', 'danger')
            return render_template('auth/login.html')

        user = User.query.filter_by(email=email).first()
        if user is None or not user.verify_password(password):
            flash('이메일 또는 비밀번호가 올바르지 않습니다.', 'danger')
            return render_template('auth/login.html')

        if not user.is_active:
            flash('비활성화된 계정입니다. 관리자에게 문의하세요.', 'danger')
            return render_template('auth/login.html')

        login_user(user, remember=bool(remember))
        next_page = request.args.get('next')
        return redirect(next_page or url_for('main.dashboard'))

    return render_template('auth/login.html')


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        name = request.form.get('name', '').strip()
        password = request.form.get('password', '')
        password2 = request.form.get('password2', '')
        phone = request.form.get('phone', '').strip()
        student_id = request.form.get('student_id', '').strip()
        room_number = request.form.get('room_number', '').strip()

        errors = []

        if not email.endswith(f'@{ALLOWED_DOMAIN}'):
            errors.append(f'이메일은 @{ALLOWED_DOMAIN} 도메인만 허용됩니다.')

        if User.query.filter_by(email=email).first():
            errors.append('이미 사용 중인 이메일입니다.')

        if student_id and User.query.filter_by(student_id=student_id).first():
            errors.append('이미 등록된 학번입니다.')

        if len(password) < 8:
            errors.append('비밀번호는 8자 이상이어야 합니다.')

        if password != password2:
            errors.append('비밀번호가 일치하지 않습니다.')

        if not name:
            errors.append('이름을 입력해주세요.')

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('auth/signup.html',
                                   email=email, name=name, phone=phone,
                                   student_id=student_id, room_number=room_number)

        user = User(
            email=email,
            name=name,
            phone=phone if phone else None,
            student_id=student_id if student_id else None,
            room_number=room_number if room_number else None,
        )
        user.password = password
        db.session.add(user)
        db.session.commit()

        flash('회원가입이 완료되었습니다. 로그인해주세요.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/signup.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('로그아웃되었습니다.', 'info')
    return redirect(url_for('auth.login'))


@auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'change_password':
            current_pw = request.form.get('current_password', '')
            new_pw = request.form.get('new_password', '')
            new_pw2 = request.form.get('new_password2', '')

            if not current_user.verify_password(current_pw):
                flash('현재 비밀번호가 올바르지 않습니다.', 'danger')
            elif len(new_pw) < 8:
                flash('새 비밀번호는 8자 이상이어야 합니다.', 'danger')
            elif new_pw != new_pw2:
                flash('새 비밀번호가 일치하지 않습니다.', 'danger')
            else:
                current_user.password = new_pw
                db.session.commit()
                flash('비밀번호가 변경되었습니다.', 'success')

        elif action == 'update_phone':
            phone = request.form.get('phone', '').strip()
            current_user.phone = phone if phone else None
            db.session.commit()
            flash('전화번호가 업데이트되었습니다.', 'success')

        elif action == 'save_signature':
            signature_data = request.form.get('signature_data', '')
            if signature_data:
                current_user.signature = signature_data
                db.session.commit()
                flash('전자서명이 등록되었습니다.', 'success')
            else:
                flash('서명 데이터가 없습니다.', 'danger')

        return redirect(url_for('auth.profile'))

    return render_template('dashboard/profile.html')