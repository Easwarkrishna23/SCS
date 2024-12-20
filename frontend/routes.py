from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from backend.authentication import login_required, admin_required
from backend.authentication import auth_manager, graph_manager, message_handler

routes = Blueprint('routes', __name__)

@routes.route('/')
def index():
    return render_template('login.html')

@routes.route('/login', methods=['POST'])
def login():
    role = request.form.get('role')
    username = request.form.get('username')
    password = request.form.get('password')
    
    if role == 'admin':
        token = auth_manager.authenticate_admin(username, password)
        if token:
            session['token'] = token
            session['role'] = 'admin'
            session['username'] = username
            return redirect(url_for('routes.admin_dashboard'))
    else:
        token = auth_manager.authenticate_user(username, password)
        if token:
            session['token'] = token
            session['role'] = 'user'
            session['username'] = username
            return redirect(url_for('routes.user_dashboard'))
    
    flash('Invalid credentials')
    return redirect(url_for('routes.index'))

@routes.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('routes.index'))

# Admin routes
@routes.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    admins = auth_manager.get_all_admins()
    network_status = graph_manager.get_network_status()
    return render_template('admin/dashboard.html', 
                         admins=admins, 
                         network_status=network_status)

@routes.route('/admin/add_admin', methods=['POST'])
@admin_required
def add_admin():
    username = request.form.get('username')
    password = request.form.get('password')
    success, message = auth_manager.create_admin(username, password, seniority=1)
    return jsonify({'success': success, 'message': message})

@routes.route('/admin/network')
@admin_required
def network_view():
    graph_data = graph_manager.visualize_graph()
    nodes = graph_manager.get_all_nodes()
    return render_template('admin/network.html', 
                         graph_data=graph_data, 
                         nodes=nodes)

@routes.route('/admin/users')
@admin_required
def manage_users():
    users = auth_manager.get_all_users()
    return render_template('admin/users.html', users=users)

# User routes
@routes.route('/user/dashboard')
@login_required
def user_dashboard():
    user_id = auth_manager.get_user_id_from_token(session['token'])
    user_details = auth_manager.get_user_details(user_id)
    message_summary = message_handler.get_user_messages_summary(user_id)
    return render_template('user/dashboard.html', 
                         user=user_details, 
                         message_summary=message_summary)

@routes.route('/user/messages')
@login_required
def messages():
    user_id = auth_manager.get_user_id_from_token(session['token'])
    conversations = message_handler.get_conversation_history(user_id)
    unread = message_handler.get_unread_messages(user_id)
    return render_template('user/messages.html', 
                         conversations=conversations, 
                         unread=unread)

@routes.route('/user/send_message', methods=['POST'])
@login_required
def send_message():
    user_id = auth_manager.get_user_id_from_token(session['token'])
    receiver_id = request.form.get('receiver_id')
    message = request.form.get('message')
    success, msg = message_handler.send_message(user_id, receiver_id, message)
    return jsonify({'success': success, 'message': msg})

# API endpoints for AJAX calls
@routes.route('/api/update_password', methods=['POST'])
@login_required
def update_password():
    user_id = auth_manager.get_user_id_from_token(session['token'])
    new_password = request.json.get('new_password')
    success = auth_manager.update_user_password(user_id, new_password)
    return jsonify({'success': success})

@routes.route('/api/mark_message_read', methods=['POST'])
@login_required
def mark_message_read():
    message_id = request.json.get('message_id')
    success = message_handler.mark_as_read(message_id)
    return jsonify({'success': success})

# Error handlers
@routes.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@routes.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500