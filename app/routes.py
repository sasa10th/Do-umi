from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from datetime import date, datetime
from .models import User, Penalty, Document, Exemption, Notification, PenaltyStandard
from . import db

main = Blueprint('main', __name__)


@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))


@main.route('/dashboard')
@login_required
def dashboard():
    recent_penalties = Penalty.query.filter_by(
        student_id=current_user.id, is_cancelled=False
    ).order_by(Penalty.date.desc()).limit(3).all()

    upcoming_docs = Document.query.filter_by(
        student_id=current_user.id, is_submitted=False
    ).order_by(Document.due_date.asc()).first()

    unread_count = Notification.query.filter_by(
        user_id=current_user.id, is_read=False
    ).count()

    return render_template('dashboard/index.html',
                           recent_penalties=recent_penalties,
                           upcoming_docs=upcoming_docs,
                           unread_count=unread_count,
                           today=date.today())


# ── 벌점 현황 ────────────────────────────────────────────
@main.route('/penalties')
@login_required
def penalties():
    sort = request.args.get('sort', 'date_desc')
    query = Penalty.query.filter_by(student_id=current_user.id, is_cancelled=False)

    if sort == 'date_asc':
        query = query.order_by(Penalty.date.asc())
    elif sort == 'points_desc':
        query = query.order_by(Penalty.points.desc())
    elif sort == 'points_asc':
        query = query.order_by(Penalty.points.asc())
    else:
        query = query.order_by(Penalty.date.desc())

    penalties_list = query.all()
    standards = PenaltyStandard.query.filter_by(is_active=True).all()

    return render_template('dashboard/penalty.html',
                           penalties=penalties_list,
                           standards=standards,
                           sort=sort)


@main.route('/penalties/<int:penalty_id>/confirm', methods=['POST'])
@login_required
def confirm_penalty(penalty_id):
    penalty = Penalty.query.get_or_404(penalty_id)
    if penalty.student_id != current_user.id:
        abort(403)

    signature_data = request.form.get('signature_data', '')
    if not signature_data:
        flash('전자서명이 필요합니다.', 'danger')
        return redirect(url_for('main.penalties'))

    penalty.is_confirmed = True
    penalty.student_signature = signature_data
    penalty.confirmed_at = datetime.utcnow()
    db.session.commit()

    flash('벌점 내역이 전자서명으로 확인되었습니다.', 'success')
    return redirect(url_for('main.penalties'))


# ── 천자문 기한 ────────────────────────────────────────────
@main.route('/documents')
@login_required
def documents():
    docs = Document.query.filter_by(student_id=current_user.id).order_by(
        Document.due_date.asc()
    ).all()
    exemptions = current_user.exemptions.filter_by(is_used=False).all()
    today = date.today()

    return render_template('dashboard/document.html',
                           documents=docs,
                           exemptions=exemptions,
                           exemption_count=len(exemptions),
                           today=today)


@main.route('/documents/<int:doc_id>/extend', methods=['POST'])
@login_required
def extend_document(doc_id):
    doc = Document.query.get_or_404(doc_id)
    if doc.student_id != current_user.id:
        abort(403)
    if doc.is_submitted:
        flash('이미 제출된 문서입니다.', 'warning')
        return redirect(url_for('main.documents'))

    # 면제권 확인
    exemption = Exemption.query.filter_by(
        student_id=current_user.id, is_used=False
    ).first()

    if not exemption:
        flash('사용 가능한 면제권이 없습니다.', 'danger')
        return redirect(url_for('main.documents'))

    # 면제권 사용 → 천자문 제거(완료 처리)
    exemption.is_used = True
    exemption.used_for_document_id = doc.id
    exemption.used_at = datetime.utcnow()
    doc.is_submitted = True
    doc.submitted_at = datetime.utcnow()
    db.session.commit()

    flash('면제권을 사용하여 천자문이 처리되었습니다.', 'success')
    return redirect(url_for('main.documents'))


@main.route('/documents/<int:doc_id>/delay', methods=['POST'])
@login_required
def delay_document(doc_id):
    """시험 기간 천자문 연기"""
    doc = Document.query.get_or_404(doc_id)
    if doc.student_id != current_user.id:
        abort(403)
    if doc.is_submitted or doc.is_extended:
        flash('연기할 수 없는 상태입니다.', 'warning')
        return redirect(url_for('main.documents'))

    from datetime import timedelta
    doc.original_due_date = doc.due_date
    doc.due_date = doc.due_date + timedelta(days=14)
    doc.is_extended = True
    db.session.commit()

    flash('천자문 기한이 2주 연기되었습니다.', 'success')
    return redirect(url_for('main.documents'))


# ── 알림 ────────────────────────────────────────────
@main.route('/notifications')
@login_required
def notifications():
    notifs = Notification.query.filter_by(user_id=current_user.id).order_by(
        Notification.created_at.desc()
    ).all()
    # 읽음 처리
    for n in notifs:
        n.is_read = True
    db.session.commit()
    return render_template('dashboard/notifications.html', notifications=notifs)


# ── 관리자 기능 ────────────────────────────────────────────
@main.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        abort(403)

    students = User.query.filter_by(is_admin=False).all()
    recent_penalties = Penalty.query.order_by(Penalty.created_at.desc()).limit(20).all()
    total_students = len(students)

    return render_template('dashboard/admin.html',
                           students=students,
                           recent_penalties=recent_penalties,
                           total_students=total_students)


@main.route('/admin/penalty/add', methods=['GET', 'POST'])
@login_required
def admin_add_penalty():
    if not current_user.is_admin:
        abort(403)

    students = User.query.filter_by(is_admin=False).order_by(User.name).all()
    standards = PenaltyStandard.query.filter_by(is_active=True).all()

    if request.method == 'POST':
        student_id = request.form.get('student_id', type=int)
        category = request.form.get('category', '')
        reason = request.form.get('reason', '').strip()
        points = request.form.get('points', 0, type=int)
        merit_points = request.form.get('merit_points', 0, type=int)
        penalty_date_str = request.form.get('date', '')

        if not student_id or not reason:
            flash('필수 항목을 입력해주세요.', 'danger')
        else:
            try:
                p_date = datetime.strptime(penalty_date_str, '%Y-%m-%d').date() if penalty_date_str else date.today()
            except ValueError:
                p_date = date.today()

            penalty = Penalty(
                student_id=student_id,
                issued_by_id=current_user.id,
                date=p_date,
                category=category,
                reason=reason,
                points=points,
                merit_points=merit_points
            )
            db.session.add(penalty)

            # 알림 생성
            student = User.query.get(student_id)
            if points > 0:
                notif = Notification(
                    user_id=student_id,
                    title='벌점 부과 알림',
                    body=f'[{category}] {reason} - {points}점이 부과되었습니다. (현재 누적 벌점: {student.total_penalty_points + points}점)',
                    ntype='danger'
                )
            else:
                notif = Notification(
                    user_id=student_id,
                    title='상점 부여 알림',
                    body=f'[{category}] {reason} - 상점 {merit_points}점이 부여되었습니다.',
                    ntype='success'
                )
            db.session.add(notif)
            db.session.commit()

            from .utils.mail import send_penalty_notification
            try:
                send_penalty_notification(student, penalty)
            except Exception:
                pass

            flash('벌점/상점이 등록되었습니다.', 'success')
            return redirect(url_for('main.admin_dashboard'))

    return render_template('dashboard/admin_add_penalty.html',
                           students=students, standards=standards, today=date.today())


@main.route('/admin/exemption/grant', methods=['POST'])
@login_required
def admin_grant_exemption():
    if not current_user.is_admin:
        abort(403)

    student_id = request.form.get('student_id', type=int)
    count = request.form.get('count', 1, type=int)
    note = request.form.get('note', '')

    if not student_id:
        flash('학생을 선택해주세요.', 'danger')
        return redirect(url_for('main.admin_dashboard'))

    for _ in range(count):
        ex = Exemption(
            student_id=student_id,
            granted_by_id=current_user.id,
            note=note
        )
        db.session.add(ex)

    student = User.query.get(student_id)
    notif = Notification(
        user_id=student_id,
        title='천자문 면제권 지급',
        body=f'면제권 {count}개가 지급되었습니다.',
        ntype='info'
    )
    db.session.add(notif)
    db.session.commit()

    flash(f'{student.name} 학생에게 면제권 {count}개를 지급했습니다.', 'success')
    return redirect(url_for('main.admin_dashboard'))


@main.route('/admin/document/assign', methods=['POST'])
@login_required
def admin_assign_document():
    if not current_user.is_admin:
        abort(403)

    student_id = request.form.get('student_id', type=int)
    title = request.form.get('title', '').strip()
    doc_type = request.form.get('doc_type', '천자문')
    due_date_str = request.form.get('due_date', '')

    if not student_id or not title or not due_date_str:
        flash('필수 항목을 입력해주세요.', 'danger')
        return redirect(url_for('main.admin_dashboard'))

    try:
        due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
    except ValueError:
        flash('날짜 형식이 올바르지 않습니다.', 'danger')
        return redirect(url_for('main.admin_dashboard'))

    doc = Document(
        student_id=student_id,
        title=title,
        doc_type=doc_type,
        due_date=due_date
    )
    db.session.add(doc)
    db.session.commit()

    flash('천자문 과제가 등록되었습니다.', 'success')
    return redirect(url_for('main.admin_dashboard'))