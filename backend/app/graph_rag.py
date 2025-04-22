from neo4j import GraphDatabase
from app.dagster_pipeline.utils.database import db
from loguru import logger
import traceback

class GraphRAG:
    def __init__(self):
        uri = "bolt://neo4j:7687"
        user = "neo4j"
        password = "grostock123"
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            logger.info("成功連接到 Neo4j")
        except Exception as e:
            logger.error(f"無法連接到 Neo4j: {str(e)}\n{traceback.format_exc()}")
            raise
        self.conn = db.connect_postgres()
        self.mongo_db = db.connect_mongo()

    def initialize_graph(self):
        """初始化股票關係圖，整合 PostgreSQL 和 MongoDB 資料"""
        with self.driver.session() as session:
            try:
                # 清空現有圖
                session.run("MATCH (n) DETACH DELETE n")
                logger.info("Cleared existing Neo4j graph")

                # 從 PostgreSQL 添加股票節點
                cursor = self.conn.cursor()
                cursor.execute("SELECT stock_id, stock_name FROM stock_list;")
                stocks = cursor.fetchall()
                if stocks:
                    for stock_id, stock_name in stocks:
                        session.run("""
                            CREATE (s:Stock {stock_id: $stock_id, stock_name: $stock_name})
                        """, stock_id=stock_id, stock_name=stock_name or "未知名稱")
                    logger.info(f"添加了 {len(stocks)} 個股票節點")
                else:
                    logger.warning("stock_list 表為空，跳過股票節點創建")

                # 添加價格預測關係
                cursor.execute("SELECT stock_id, date, lstm_pred FROM predictions;")
                predictions = cursor.fetchall()
                if predictions:
                    for stock_id, date, lstm_pred in predictions:
                        session.run("""
                            MATCH (s:Stock {stock_id: $stock_id})
                            CREATE (p:Prediction {date: $date, lstm_pred: $lstm_pred})
                            CREATE (s)-[:HAS_PREDICTION]->(p)
                        """, stock_id=stock_id, date=str(date), lstm_pred=float(lstm_pred or 0))
                    logger.info(f"添加了 {len(predictions)} 個預測關係")
                else:
                    logger.warning("predictions 表為空，跳過預測關係創建")

                # 添加策略關係
                cursor.execute("SELECT stock_id, date, momentum_signal FROM strategies;")
                strategies = cursor.fetchall()
                if strategies:
                    for stock_id, date, momentum_signal in strategies:
                        session.run("""
                            MATCH (s:Stock {stock_id: $stock_id})
                            CREATE (t:Strategy {date: $date, momentum_signal: $momentum_signal})
                            CREATE (s)-[:HAS_STRATEGY]->(t)
                        """, stock_id=stock_id, date=str(date), momentum_signal=int(momentum_signal or 0))
                    logger.info(f"添加了 {len(strategies)} 個策略關係")
                else:
                    logger.warning("strategies 表為空，跳過策略關係創建")

                # 從 MongoDB 添加新聞關係
                news = list(self.mongo_db["news"].find())
                if news:
                    for item in news:
                        stock_id = item.get("stock_id", "unknown")
                        date = item.get("date", "unknown")
                        title = item.get("title", "未知標題")
                        sentiment = item.get("sentiment", {"label": "NEUTRAL", "score": 0.5}).get("label", "NEUTRAL")
                        session.run("""
                            MATCH (s:Stock {stock_id: $stock_id})
                            CREATE (n:News {date: $date, title: $title, sentiment: $sentiment})
                            CREATE (s)-[:HAS_NEWS]->(n)
                        """, stock_id=stock_id, date=date, title=title, sentiment=sentiment)
                    logger.info(f"添加了 {len(news)} 個新聞關係")
                else:
                    logger.warning("MongoDB news 集合為空，跳過新聞關係創建")

                logger.info("股票關係圖初始化完成，整合 PostgreSQL 和 MongoDB")
            except Exception as e:
                logger.error(f"Neo4j 圖初始化失敗: {str(e)}\n{traceback.format_exc()}")
                raise
            finally:
                cursor.close()

    def query_graph(self, query: str) -> str:
        """查詢圖資料"""
        with self.driver.session() as session:
            try:
                if "預測" in query or "價格" in query:
                    stock_id = query.split()[-1]
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
                elif "新聞" in query:
                    stock_id = query.split()[-1]
                    result = session.run("""
                        MATCH (s:Stock {stock_id: $stock_id})-[:HAS_NEWS]->(n:News)
                        RETURN n.date, n.title, n.sentiment
                        ORDER BY n.date DESC LIMIT 1
                    """, stock_id=stock_id)
                    data = result.single()
                    if data:
                        return f"股票 {stock_id} 最新新聞: {data['n.title']} (日期: {data['n.date']}, 情緒: {data['n.sentiment']})"
                return "無法從圖中找到相關資訊"
            except Exception as e:
                logger.error(f"查詢 Neo4j 圖失敗: {str(e)}\n{traceback.format_exc()}")
                return "查詢失敗"

graph_rag = GraphRAG()