from flask import Request,Blueprint,jsonify
from flask_jwt_extended import jwt_required
from app.services.notification_service import NotificationService


notification_bp = Blueprint('notification',__name__)

@notification_bp.get("/<user_id>")
@jwt_required()
def get_notification_user(user_id):
    notifiations_all:list = NotificationService.get_all_notification(user_id)
    
    if len(notifiations_all) == 0 :
        return jsonify({'message':' Empty notifications tray'}),404
    return jsonify({'notifications':notifiations_all}),200

@notification_bp.delete("/<user_id>")
@jwt_required()
def delete_notification(user_id):
    success:bool = NotificationService.delete_notification(user_id)
    
    if success == False:
        return jsonify({'message':'No se pudo eliminar la notificaion'})
    
    return jsonify({'message':'Notification deleted'})
    