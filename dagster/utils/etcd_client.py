import etcd3
from loguru import logger
import os
from dotenv import load_dotenv

load_dotenv()

class EtcdClient:
    def __init__(self):
        self.client = etcd3.client(
            host=os.getenv("ETCD_HOST"),
            port=int(os.getenv("ETCD_PORT"))
        )
        logger.info("Initialized etcd client")

    def put(self, key, value):
        try:
            self.client.put(key, value)
            logger.info(f"Stored {key} in etcd")
        except Exception as e:
            logger.error(f"Failed to store {key} in etcd: {e}")

    def get(self, key):
        try:
            value, _ = self.client.get(key)
            logger.info(f"Retrieved {key} from etcd")
            return value.decode('utf-8') if value else None
        except Exception as e:
            logger.error(f"Failed to retrieve {key} from etcd: {e}")
            return None

etcd_client = EtcdClient()