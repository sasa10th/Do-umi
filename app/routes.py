from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app, jsonify
from flask_login import login_required, current_user
from datetime import date, datetime, timedelta
from .models import User, Penalty, Document, Exemption, Notification, PenaltyStandard, ExamPeriod
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
def get_current_exam_period():
    """현재 시험 기간이거나, 시험 기간 2주 전이면 ExamPeriod 반환"""
    today = date.today()
    return ExamPeriod.query.filter(
        ExamPeriod.start_date <= today + timedelta(days=14),  # 2주 전부터
        ExamPeriod.end_date >= today                          # 아직 종료 안 됨
    ).first()


@main.route('/documents')
@login_required
def documents():
    docs = Document.query.filter_by(student_id=current_user.id).order_by(
        Document.due_date.asc()
    ).all()
    exemptions = current_user.exemptions.filter_by(is_used=False).all()
    today = date.today()
    exam_period = get_current_exam_period()

    return render_template('dashboard/document.html',
                           documents=docs,
                           exemptions=exemptions,
                           exemption_count=len(exemptions),
                           today=today,
                           exam_period=exam_period)


@main.route('/documents/<int:doc_id>/extend', methods=['POST'])
@login_required
def extend_document(doc_id):
    doc = Document.query.get_or_404(doc_id)
    if doc.student_id != current_user.id:
        abort(403)
    if doc.is_submitted:
        flash('이미 제출된 문서입니다.', 'warning')
        return redirect(url_for('main.documents'))

    exemption = Exemption.query.filter_by(
        student_id=current_user.id, is_used=False
    ).first()

    if not exemption:
        flash('사용 가능한 면제권이 없습니다.', 'danger')
        return redirect(url_for('main.documents'))

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
    # 시험 기간 확인 (백엔드에서 반드시 검증)
    if not get_current_exam_period():
        flash('시험 기간에만 연기할 수 있습니다.', 'danger')
        return redirect(url_for('main.documents'))

    doc = Document.query.get_or_404(doc_id)
    if doc.student_id != current_user.id:
        abort(403)
    if doc.is_submitted or doc.is_extended:
        flash('연기할 수 없는 상태입니다.', 'warning')
        return redirect(url_for('main.documents'))

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
    recent_penalties = Penalty.query.order_by(Penalty.created_at.desc()).limit(10).all()
    recent_documents = Document.query.filter_by(is_submitted=False).order_by(Document.created_at.desc()).limit(20).all()
    total_students = len(students)
    exam_periods = ExamPeriod.query.order_by(ExamPeriod.start_date.desc()).all()

    return render_template('dashboard/admin.html',
                           students=students,
                           recent_penalties=recent_penalties,
                           recent_documents=recent_documents,
                           total_students=total_students,
                           exam_periods=exam_periods,
                           today=date.today())


@main.route('/admin/search/penalties')
@login_required
def admin_search_penalties():
    if not current_user.is_admin:
        abort(403)

    q = request.args.get('q', '').strip()
    query = Penalty.query.join(User, Penalty.student_id == User.id).filter(Penalty.is_cancelled == False)
    if q:
        query = query.filter(User.student_id.ilike(f"%{q}%"))

    results = query.order_by(Penalty.created_at.desc()).limit(40).all()

    data = []
    for p in results:
        data.append({
            'id': p.id,
            'date': p.date.isoformat() if p.date else '',
            'student_name': p.student.name if p.student else '',
            'student_id': p.student.student_id if p.student else '',
            'reason': p.reason,
            'points': p.points,
            'merit_points': p.merit_points,
            'is_confirmed': bool(p.is_confirmed)
        })

    return jsonify(results=data)


@main.route('/admin/search/documents')
@login_required
def admin_search_documents():
    if not current_user.is_admin:
        abort(403)

    q = request.args.get('q', '').strip()
    query = Document.query.join(User, Document.student_id == User.id)
    query = query.filter(Document.is_submitted == False)
    if q:
        query = query.filter(User.student_id.ilike(f"%{q}%"))

    results = query.order_by(Document.created_at.desc()).limit(40).all()

    data = []
    for d in results:
        data.append({
            'id': d.id,
            'student_name': d.student.name if d.student else '',
            'student_id': d.student.student_id if d.student else '',
            'doc_type': d.doc_type,
            'due_date': d.due_date.isoformat() if d.due_date else '',
            'is_submitted': bool(d.is_submitted),
            'is_overdue': bool(d.is_overdue),
            'days_remaining': d.days_remaining
        })

    return jsonify(results=data)


@main.route('/admin/penalty/add', methods=['GET', 'POST'])
@login_required
def admin_add_penalty():
    if not current_user.is_admin:
        abort(403)

    students = User.query.filter_by(is_admin=False).order_by(User.name).all()
    standards = PenaltyStandard.query.filter_by(is_active=True).all()

    if request.method == 'POST':
        student_id = request.form.get('student_id', type=int)
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
                reason=reason,
                points=points,
                merit_points=merit_points
            )
            db.session.add(penalty)

            student = User.query.get(student_id)
            if points > merit_points:
                notif = Notification(
                    user_id=student_id,
                    title='벌점 부과 알림',
                    body=f'{reason} - 벌점 {points-merit_points}점이 부과되었습니다.',
                    ntype='danger'
                )
            else:
                notif = Notification(
                    user_id=student_id,
                    title='상점 부과 알림',
                    body=f'{reason} - 상점 {merit_points-points}점이 부과되었습니다.',
                    ntype='success'
                )
            db.session.add(notif)
            db.session.commit()

            from .utils.mail import send_penalty_notification
            try:
                send_penalty_notification(student, penalty)
            except Exception as e:
                current_app.logger.warning(f'벌점 메일 발송 실패: {e}')

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
    doc_type = request.form.get('doc_type', '천자문')
    due_date_str = request.form.get('due_date', '')

    if not student_id or not due_date_str:
        flash('필수 항목을 입력해주세요.', 'danger')
        return redirect(url_for('main.admin_dashboard'))

    try:
        due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
    except ValueError:
        flash('날짜 형식이 올바르지 않습니다.', 'danger')
        return redirect(url_for('main.admin_dashboard'))

    doc = Document(
        student_id=student_id,
        doc_type=doc_type,
        due_date=due_date
    )
    db.session.add(doc)
    db.session.commit()

    flash('천자문 과제가 등록되었습니다.', 'success')
    return redirect(url_for('main.admin_dashboard'))


@main.route('/admin/document/<int:doc_id>/delete', methods=['POST'])
@login_required
def admin_delete_document(doc_id):
    if not current_user.is_admin:
        abort(403)

    doc = Document.query.get_or_404(doc_id)
    student_name = doc.student.name

    db.session.delete(doc)
    db.session.commit()

    flash(f'{student_name} 학생의 천자문 과제가 삭제되었습니다.', 'success')
    return redirect(url_for('main.admin_dashboard'))


# ── 시험 기간 관리 ────────────────────────────────────────────
@main.route('/admin/exam-period/add', methods=['POST'])
@login_required
def admin_add_exam_period():
    if not current_user.is_admin:
        abort(403)

    name = request.form.get('name', '').strip()
    start_date_str = request.form.get('start_date', '')
    end_date_str = request.form.get('end_date', '')

    if not name or not start_date_str or not end_date_str:
        flash('모든 항목을 입력해주세요.', 'danger')
        return redirect(url_for('main.admin_dashboard'))

    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except ValueError:
        flash('날짜 형식이 올바르지 않습니다.', 'danger')
        return redirect(url_for('main.admin_dashboard'))

    if end_date < start_date:
        flash('종료일이 시작일보다 빠를 수 없습니다.', 'danger')
        return redirect(url_for('main.admin_dashboard'))

    exam_period = ExamPeriod(
        name=name,
        start_date=start_date,
        end_date=end_date,
        created_by_id=current_user.id
    )
    db.session.add(exam_period)
    db.session.commit()

    flash(f'시험 기간 "{name}"이 등록되었습니다.', 'success')
    return redirect(url_for('main.admin_dashboard'))


@main.route('/admin/exam-period/<int:period_id>/delete', methods=['POST'])
@login_required
def admin_delete_exam_period(period_id):
    if not current_user.is_admin:
        abort(403)

    period = ExamPeriod.query.get_or_404(period_id)
    db.session.delete(period)
    db.session.commit()

    flash('시험 기간이 삭제되었습니다.', 'success')
    return redirect(url_for('main.admin_dashboard'))