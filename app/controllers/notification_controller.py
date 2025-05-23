from flask import Request,Blueprint,jsonify,request,current_app
from flask_jwt_extended import jwt_required,get_jwt_identity
from app.services.notification_service import NotificationService
from app.services.user_service import UserService

notification_bp = Blueprint('notification',__name__)

@notification_bp.get("/")
@jwt_required()
def get_notification_user():
    user_id = get_jwt_identity()
    notifiations_all:list = NotificationService.get_all_notification(user_id)
    
    if len(notifiations_all) == 0 :
        return jsonify({'message':' Empty notifications tray'}),404
    return jsonify({'notifications':notifiations_all}),200

@notification_bp.delete("/<notification_id>")
@jwt_required()
def delete_notification(notification_id):
    user_id = get_jwt_identity()
    success:bool = NotificationService.delete_notification(notification_id=notification_id,user_id=user_id)
    
    if success == False:
        return jsonify({'message':'No se pudo eliminar la notificaion'})
    
    return jsonify({'message':'Notification deleted'})
    
@notification_bp.route('/notifications', methods=['PUT'])
@jwt_required()
def update_notifications():
    """Update notification settings"""
    data = request.get_json()
    user_id = get_jwt_identity()
    
    try:
        # Get notification settings
        notification_settings = {}
        for field in ['new_follower', 'likes', 'mentions', 'direct_messages']:
            if field in data:
                notification_settings[field] = bool(data[field])
                
        if not notification_settings:
            return jsonify({'message': 'No valid notification settings to update'}), 400
                
        # Update notifications
        if UserService.update_notification_settings(user_id, notification_settings):
            return jsonify({'message': 'Notification settings updated successfully'}), 200
        else:
            return jsonify({'message': 'Error updating notification settings'}), 400
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error updating notifications: {str(e)}")
        return jsonify({'message': 'Error updating notification settings'}), 500