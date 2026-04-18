# ==========================================
# SMM API - smm_api.py
# ==========================================

import requests
import logging
from config import SMM_API_URL, SMM_API_KEY

logger = logging.getLogger(__name__)


class SMMApi:
    """كلاس للتعامل مع SMM Panel API"""

    def __init__(self):
        self.url = SMM_API_URL
        self.key = SMM_API_KEY
        self.timeout = 30

    def _post(self, data: dict) -> dict:
        """إرسال طلب POST إلى الـ API"""
        data["key"] = self.key
        try:
            response = requests.post(self.url, data=data, timeout=self.timeout)
            response.raise_for_status()

            # حماية من الرد غير JSON
            if "application/json" in response.headers.get("Content-Type", ""):
                return response.json()
            else:
                logger.error(f"Non-JSON response: {response.text[:100]}")
                return {"error": "الرد من السيرفر غير صالح"}

        except requests.exceptions.Timeout:
            logger.error("SMM API: Timeout")
            return {"error": "انتهت مهلة الاتصال بالخادم"}

        except requests.exceptions.ConnectionError:
            logger.error("SMM API: Connection failed")
            return {"error": "تعذر الاتصال بخادم SMM"}

        except requests.exceptions.HTTPError as e:
            logger.error(f"SMM API HTTP Error: {e}")
            return {"error": f"خطأ HTTP: {e}"}

        except Exception as e:
            logger.error(f"SMM API Unknown Error: {e}")
            return {"error": "خطأ غير متوقع في API"}

    def create_order(self, service_id: int, link: str, quantity: int) -> dict:
        """إنشاء طلب جديد"""
        result = self._post({
            "action": "add",
            "service": service_id,
            "link": link,
            "quantity": quantity,
        })

        logger.info(f"SMM Order → service={service_id}, qty={quantity}, result={result}")
        return result

    def get_order_status(self, order_id: str) -> dict:
        """جلب حالة الطلب"""
        return self._post({
            "action": "status",
            "order": order_id,
        })

    def get_balance(self) -> dict:
        """جلب رصيد لوحة SMM"""
        return self._post({"action": "balance"})

    def get_services(self) -> list:
        """جلب الخدمات"""
        result = self._post({"action": "services"})
        return result if isinstance(result, list) else []


# ================= ترجمة الحالات =================

ORDER_STATUS_MAP = {
    "Pending": ("⏳", "قيد الانتظار"),
    "In progress": ("⚙️", "جاري التنفيذ"),
    "Completed": ("✅", "تم بنجاح"),
    "Partial": ("⚠️", "منفذ جزئياً"),
    "Canceled": ("❌", "ملغى"),
    "Processing": ("🔄", "قيد المعالجة"),
    "Refunded": ("💸", "تم الاسترداد"),
}


def translate_status(status: str) -> tuple:
    """ترجمة الحالة"""
    return ORDER_STATUS_MAP.get(status, ("❓", status))


# instance
smm_api = SMMApi()