from neo4j import GraphDatabase
from ...dagster.utils.database import db
from loguru import logger
import pandas as pd

class GraphRAG:
    def __init__(self):
        self.driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "neo4j"))
        self.conn = db.connect_postgres()

    def initialize_graph(self):
        """初始化股票關係圖"""
        with self.driver.session() as session:
            # 清空現有圖
            session.run("MATCH (n) DETACH DELETE n")
            
            # 添加股票節點
            cursor = self.conn.cursor()
            cursor.execute("SELECT stock_id, stock_name FROM stock_list;")
            stocks = cursor.fetchall()
            for stock_id, stock_name in stocks:
                session.run("""
                    CREATE (s:Stock {stock_id: $stock_id, stock_name: $stock_name})
                """, stock_id=stock_id, stock_name=stock_name)

            # 添加價格預測關係
            cursor.execute("SELECT stock_id, date, lstm_pred FROM predictions;")
            predictions = cursor.fetchall()
            for stock_id, date, lstm_pred in predictions:
                session.run("""
                    MATCH (s:Stock {stock_id: $stock_id})
                    CREATE (p:Prediction {date: $date, lstm_pred: $lstm_pred})
                    CREATE (s)-[:HAS_PREDICTION]->(p)
                """, stock_id=stock_id, date=str(date), lstm_pred=float(lstm_pred))

            # 添加策略關係
            cursor.execute("SELECT stock_id, date, momentum_signal FROM strategies;")
            strategies = cursor.fetchall()
            for stock_id, date, momentum_signal in strategies:
                session.run("""
                    MATCH (s:Stock {stock_id: $stock_id})
                    CREATE (t:Strategy {date: $date, momentum_signal: $momentum_signal})
                    CREATE (s)-[:HAS_STRATEGY]->(t)
                """, stock_id=stock_id, date=str(date), momentum_signal=int(momentum_signal))

            logger.info("股票關係圖初始化完成")
            cursor.close()

    def query_graph(self, query: str) -> str:
        """查詢圖資料"""
        with self.driver.session() as session:
            if "預測" in query or "價格" in query:
                stock_id = query.split()[-1]  # 假設股票代碼在最後
                result = session.run("""
                    MATCH (s:Stock {stock_id: $stock_id})-[:HAS_PREDICTION]->(p:Prediction)
                    RETURN p.date, p.lstm_pred
                    ORDER BY p.date DESC LIMIT 1
                """, stock_id=stock_id)
                data = result.single()
                if data:
                    return f"股票 {stock_id} 最新預測價格 (LSTM): {data['p.lstm_pred']} (日期: {data['p.date']})"
            elif "策略" in query:
                stock_id = query.split()[-1]
                result = session.run("""
                    MATCH (s:Stock {stock_id: $stock_id})-[:HAS_STRATEGY]->(t:Strategy)
                    RETURN t.date, t.momentum_signal
                    ORDER BY t.date DESC LIMIT 1
                """, stock_id=stock_id)
                data = result.single()
                if data:
                    return f"股票 {stock_id} 最新動量策略信號: {data['t.momentum_signal']} (日期: {data['t.date']})"
            return "無法從圖中找到相關資訊"

graph_rag = GraphRAG()