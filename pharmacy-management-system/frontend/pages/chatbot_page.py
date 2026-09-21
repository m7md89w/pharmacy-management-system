import streamlit as st
import requests

def render_chatbot_page():
    st.title("🤖 المساعد الذكي المحلي للصيدلية")
    st.markdown("تفاعل مع النظام بلغة طبيعية للاستعلام عن المخزون، الأسعار، تواريخ الصلاحية، أو للحصول على استشارات طبية عامة (يعمل محلياً بالكامل دون إنترنت).")

    # تهيئة سجل المحادثة في حالة الجلسة
    if "chatbot_messages" not in st.session_state:
        st.session_state.chatbot_messages = []

    # عرض رسائل المحادثة السابقة
    for message in st.session_state.chatbot_messages:
        with st.chat_message(message["role"]):
        # استخدام صيغة Markdown القياسية للنصوص دون استخدام أي ترميز رياضي أو LaTeX
            st.markdown(message["content"])
            if "source" in message:
                source_label = "قاعدة البيانات المحلية" if message["source"] == "database" else "الذكاء الاصطناعي المحلي (Ollama)"
                st.caption(f"المصدر: {source_label}")

    # حقل إدخال رسالة المستخدم
    if user_input := st.chat_input("اكتب سؤالك هنا (مثل: كم سعر الباراسيتامول؟ أو ما هي استخدامات الأموكسيسيلين؟)..."):
        # إضافة رسالة المستخدم إلى السجل وعرضها
        st.session_state.chatbot_messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # إرسال الطلب إلى الـ Backend API الخاص بالشات بوت
        with st.chat_message("assistant"):
            with st.spinner("جاري المعالجة محلياً..."):
                try:
                    api_url = "http://127.0.0.1:5000/api/chatbot/ask"
                    response = requests.post(api_url, json={"message": user_input}, timeout=60)
                    
                    if response.status_code == 200:
                        data = response.json()
                        bot_reply = data.get("message", "عذراً، لمادخل رد صحيح من النظام.")
                        source = data.get("source", "unknown")
                        
                        st.markdown(bot_reply)
                        source_label = "قاعدة البيانات المحلية" if source == "database" else "الذكاء الاصطناعي المحلي (Ollama)"
                        st.caption(f"المصدر: {source_label}")
                        
                        # حفظ رد المساعد في السجل
                        st.session_state.chatbot_messages.append({
                            "role": "assistant",
                            "content": bot_reply,
                            "source": source
                        })
                    else:
                        error_msg = f"خطأ في الاتصال بالخادم (رمز الاستجابة: {response.status_code})"
                        st.error(error_msg)
                except requests.exceptions.RequestException:
                    st.error("تعذر الاتصال بالخادم الخلفي (Flask Backend). تأكد من تشغيل main.py أولاً.")

if __name__ == "__main__":
    render_chatbot_page()