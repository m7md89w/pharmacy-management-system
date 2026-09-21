import logging
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from models.all_models import Medicine, MedicineBatch

logger = logging.getLogger(__name__)

class ChatbotRepository:
    def __init__(self, db: Session):
        self.db = db

    def _normalize_arabic(self, text: str) -> str:
        """
        تطبيع بسيط للنص العربي لضمان مطابقة أدق (توحيد الألفات، إزالة التشكيل، إلخ).
        """
        if not text:
            return ""
        text = text.strip()
        # توحيد أشكال الألف
        for char in ['أ', 'إ', 'آ']:
            text = text.replace(char, 'ا')
        # توحيد الهاء والتاء المربوطة إذا رغبت، أو إزالة التشكيل البسيط
        return text

    def get_medicine_stock_info(self, user_message: str) -> list[dict]:
        """
        البحث في جدول الأدوية (commercial_name, scientific_name, barcode) 
        باستخدام LEFT JOIN لضمان ظهور الأدوية المسجلة حتى لو لم يكن لها دفعات حالياً.
        """
        try:
            # استخدام outerjoin للربط اليساري (LEFT JOIN)
            query = self.db.query(Medicine, MedicineBatch).outerjoin(
                MedicineBatch, Medicine.medicine_id == MedicineBatch.medicine_id
            )
            
            # استخراج الكلمات المفتاحية للبحث
            stop_words = ["كم", "كرتون", "حبة", "مخزون", "سعر", "صلاحية", "متوفر", "باقي", "دواء", "عنا", "في", "من", "الحالي", "the", "is", "for", "in", "stock"]
            words = [w for w in user_message.split() if w.lower() not in stop_words]
            
            if words:
                filters = []
                for word in words:
                    norm_word = self._normalize_arabic(word)
                    filters.append(Medicine.commercial_name.ilike(f"%{norm_word}%"))
                    filters.append(Medicine.scientific_name.ilike(f"%{norm_word}%"))
                    filters.append(Medicine.barcode.ilike(f"%{norm_word}%"))
                query = query.filter(or_(*filters))
            
            rows = query.all()
            results = []
            today = date.today()
            
            for med, batch in rows:
                batch_qty = batch.quantity if batch and batch.quantity is not None else 0
                is_expired = False
                if batch and batch.expiry_date:
                    is_expired = batch.expiry_date < today
                
                in_stock = batch_qty > 0 and not is_expired
                
                results.append({
                    "medicine_id": med.medicine_id,
                    "commercial_name": med.commercial_name,
                    "scientific_name": med.scientific_name,
                    "barcode": med.barcode,
                    "selling_price": float(med.selling_price) if med.selling_price else 0.0,
                    "batch_number": batch.batch_number if batch else None,
                    "batch_quantity": batch_qty,
                    "expiry_date": str(batch.expiry_date) if batch and batch.expiry_date else None,
                    "is_expired": is_expired,
                    "in_stock": in_stock,
                    "has_batches": batch is not None
                })
                
            return results
            
        except Exception as e:
            logger.error(f"Error in ChatbotRepository.get_medicine_stock_info: {e}", exc_info=True)
            return []