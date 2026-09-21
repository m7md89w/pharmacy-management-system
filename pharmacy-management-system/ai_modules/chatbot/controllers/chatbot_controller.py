from flask import Blueprint, request, jsonify
from ai_modules.chatbot.services.chatbot_service import ChatbotService
from database.session import SessionLocal

chatbot_bp = Blueprint('chatbot_bp', __name__, url_prefix='/api/chatbot')

@chatbot_bp.route('/ask', methods=['POST'])
def ask_chatbot():
    """
    نقطة نهاية (API Endpoint) لاستقبال رسالة المستخدم وتوجيهها للمساعد الذكي المحلي.
    """
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"error": "حقل الرسالة (message) مطلوب في الطلب."}), 400

    user_message = data['message']
    
    # فتح جلسة قاعدة البيانات بلطف وفق معمارية المشروع
    db = SessionLocal()
    try:
        service = ChatbotService(db=db)
        result = service.process_message(user_message)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()