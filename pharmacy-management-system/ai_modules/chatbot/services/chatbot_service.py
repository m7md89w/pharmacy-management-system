import logging
from sqlalchemy.orm import Session
from ai_modules.chatbot.repositories.chatbot_repository import ChatbotRepository
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

logger = logging.getLogger(__name__)

class ChatbotService:
    def __init__(self, db: Session, model_name: str = "llama3"):
        self.db = db
        self.repo = ChatbotRepository(db)
        self.model_name = model_name
        
        try:
            self.model = OllamaLLM(model=self.model_name)
            self.template = """
            You are a helpful pharmacy assistant AI. Answer the medical or general question below professionally. 
            Do NOT invent or fabricate any inventory quantities, prices, or batch details. If stock or pricing information is needed, rely strictly on the provided database context if available.

            Context / Inventory Data: {context}

            Question: {question}

            Answer:
            """
            self.prompt = ChatPromptTemplate.from_template(self.template)
            self.chain = self.prompt | self.model
        except Exception as e:
            logger.error(f"Failed to initialize OllamaLLM chain: {e}", exc_info=True)
            self.chain = None

    def process_message(self, user_message: str, history_context: str = "") -> dict:
        """
        معالجة رسالة المستخدم بالمنهجية الهجينة مع التمييز بين أسئلة المخزون والأسئلة العامة.
        """
        # 1. قائمة كلمات الاستفهام التي تدل على سؤال عام أو استشارة تقنية/طبية
        general_question_words = ["كيف", "لماذا", "اشرح", "آلية", "طريقة", "ما هي", "هل يمكن", "متى", "how", "why", "explain", "what is"]
        is_general_question = any(q_word in user_message.lower() for q_word in general_question_words)

        # 2. البحث في قاعدة البيانات أولاً
        db_results = self.repo.get_medicine_stock_info(user_message)
        
        # 3. كلمات مفتاحية تشير إلى نية الاستعلام عن المخزون أو الأسعار
        stock_keywords = ["كمية", "سعر", "مخزون", "صلاحية", "متوفر", "باقي", "دواء", "بانادول", "panadol", "stock", "price", "available", "how many", "batch"]
        
        # نعتبره استعلام قاعدة بيانات فقط إذا كان يحتوي كلمات مخزون ولم يكن سؤالاً نظرياً/استفهامياً
        is_query_intent = (any(kw in user_message.lower() for kw in stock_keywords) or len(db_results) > 0) and not is_general_question

        if is_query_intent:
            if not db_results:
                return {
                    "message": "عذراً، هذا الدواء غير موجود بالنظام أصلاً ولا يوجد أي سجل مسجل له.",
                    "source": "database"
                }
            
            response_lines = ["بيانات الدفعات والمخزون في النظام المحلي:"]
            for item in db_results:
                name = item["commercial_name"]
                sci_name = item["scientific_name"]
                barcode = item["barcode"]
                price = item["selling_price"]
                qty = item["batch_quantity"]
                batch_num = item["batch_number"]
                expiry_date = item["expiry_date"]
                is_expired = item["is_expired"]
                has_batches = item["has_batches"]
                
                if not has_batches or batch_num is None:
                    response_lines.append(f"- الدواء ({name} / العلمي: {sci_name}) [الباركود: {barcode}]: مسجّل بالنظام لكن **لا توجد أي دفعات مرتبطة به حالياً**.")
                elif is_expired:
                    response_lines.append(f"- الدواء: {name} | الباركود: {barcode} | رقم الدفعة: {batch_num} | الكمية: {qty} | تاريخ الانتهاء: {expiry_date} ⚠️ **(دفعة منتهية الصلاحية)**")
                else:
                    response_lines.append(f"- الدواء: {name} | العلمي: {sci_name} | الباركود: {barcode} | رقم الدفعة: {batch_num} | الكمية المتوفرة: {qty} | تاريخ الانتهاء: {expiry_date} | سعر البيع: {price} ✅ **(دفعة صالحة ونشطة)**")
            
            return {
                "message": "\n".join(response_lines),
                "source": "database"
            }
        
        # 4. إذا كان سؤالاً استفهامياً يتم توجيهه لـ Ollama
        if self.chain:
            try:
                result = self.chain.invoke({
                    "context": history_context,
                    "question": user_message
                })
                return {
                    "message": result,
                    "source": "local_ai"
                }
            except Exception as e:
                logger.error(f"Error invoking LangChain model: {e}", exc_info=True)
                return {
                    "message": "حدث خطأ أثناء التواصل مع نموذج الذكاء الاصطناعي المحلي (Ollama).",
                    "source": "local_ai"
                }
        else:
            return {
                "message": "نموذج الذكاء الاصطناعي المحلي غير متوفر حالياً.",
                "source": "local_ai"
            }