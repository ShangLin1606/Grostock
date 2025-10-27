from app.services.agents.base_agent import BaseAgent
from neo4j import GraphDatabase
from app.config.settings import settings

class GraphAgent(BaseAgent):
    name = "GraphAgent"
    description = "產業關聯圖譜分析 Agent"

    def __init__(self):
        super().__init__()
        self.driver = GraphDatabase.driver(settings.NEO4J_URI, auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD))

    def query_graph(self, keyword: str):
        with self.driver.session() as session:
            result = session.run(
                "MATCH (a:Company)-[r:RELATION]->(b:Company) "
                "WHERE a.name CONTAINS $kw OR b.name CONTAINS $kw "
                "RETURN a.name AS source, type(r) AS relation, b.name AS target LIMIT 10", kw=keyword)
            rels = [f"{r['source']} --{r['relation']}--> {r['target']}" for r in result]
            return "\n".join(rels) if rels else "未找到相關產業關聯。"

    async def run(self, query: str):
        relations = self.query_graph(query)
        prompt = f"根據以下關聯資料，說明該公司在產業鏈中的角色：\n{relations}"
        answer = await self.ask_llm("你是產業分析師。", prompt)
        return {"agent": self.name, "content": answer}
