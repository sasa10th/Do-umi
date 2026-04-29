from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from .models import User, Penalty, Document, Notification, PenaltyStandard
from . import db

api = Blueprint('api', __name__)


@api.route('/me')
@login_required
def me():
    return jsonify({
        'id': current_user.id,
        'name': current_user.name,
        'email': current_user.email,
        'total_penalty_points': current_user.total_penalty_points,
        'total_merit_points': current_user.total_merit_points,
        'stage': current_user.stage,
        'exemption_count': current_user.exemption_count,
        'room_number': current_user.room_number,
    })


@api.route('/penalties')
@login_required
def get_penalties():
    penalties = Penalty.query.filter_by(
        student_id=current_user.id, is_cancelled=False
    ).order_by(Penalty.date.desc()).all()

    return jsonify([{
        'id': p.id,
        'date': p.date.isoformat(),
        'category': p.category,
        'reason': p.reason,
        'points': p.points,
        'merit_points': p.merit_points,
        'is_confirmed': p.is_confirmed,
    } for p in penalties])


@api.route('/documents')
@login_required
def get_documents():
    docs = Document.query.filter_by(
        student_id=current_user.id, is_submitted=False
    ).order_by(Document.due_date.asc()).all()

    return jsonify([{
        'id': d.id,
        'title': d.title,
        'doc_type': d.doc_type,
        'due_date': d.due_date.isoformat(),
        'days_remaining': d.days_remaining,
        'is_overdue': d.is_overdue,
        'is_extended': d.is_extended,
    } for d in docs])


@api.route('/notifications/unread-count')
@login_required
def unread_count():
    count = Notification.query.filter_by(
        user_id=current_user.id, is_read=False
    ).count()
    return jsonify({'count': count})


@api.route('/notifications/mark-read', methods=['POST'])
@login_required
def mark_notifications_read():
    Notification.query.filter_by(
        user_id=current_user.id, is_read=False
    ).update({'is_read': True})
    db.session.commit()
    return jsonify({'status': 'ok'})


@api.route('/search')
@login_required
def search():
    q = request.args.get('q', '').strip()
    if not q or len(q) < 1:
        return jsonify({'penalties': [], 'documents': []})

    penalties = Penalty.query.filter(
        Penalty.student_id == current_user.id,
        Penalty.reason.ilike(f'%{q}%')
    ).limit(5).all()

    docs = Document.query.filter(
        Document.student_id == current_user.id,
        Document.title.ilike(f'%{q}%')
    ).limit(5).all()

    return jsonify({
        'penalties': [{'id': p.id, 'reason': p.reason, 'date': p.date.isoformat()} for p in penalties],
        'documents': [{'id': d.id, 'title': d.title, 'due_date': d.due_date.isoformat()} for d in docs],
    })


@api.route('/standards')
@login_required
def get_standards():
    standards = PenaltyStandard.query.filter_by(is_active=True).all()
    return jsonify([{
        'id': s.id,
        'category': s.category,
        'description': s.description,
        'penalty_points': s.penalty_points,
        'merit_points': s.merit_points,
    } for s in standards])


# Admin APIs
@api.route('/admin/students')
@login_required
def admin_students():
    if not current_user.is_admin:
        return jsonify({'error': 'Forbidden'}), 403

    students = User.query.filter_by(is_admin=False).all()
    return jsonify([{
        'id': s.id,
        'name': s.name,
        'student_id': s.student_id,
        'room_number': s.room_number,
        'total_penalty_points': s.total_penalty_points,
        'stage': s.stage,
        'exemption_count': s.exemption_count,
    } for s in students])