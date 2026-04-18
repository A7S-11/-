import requests
import logging
from config import SMM_API_URL, SMM_API_KEY

logger = logging.getLogger(__name__)

class SMMApi:

    def create_order(self, service_id, link, quantity):
        try:
            response = requests.post(SMM_API_URL, data={
                "key": SMM_API_KEY,
                "action": "add",
                "service": service_id,
                "link": link,
                "quantity": quantity
            }, timeout=15)
            return response.json()
        except Exception as e:
            logger.error(f"SMM Error: {e}")
            return {"error": str(e)}

smm_api = SMMApi()