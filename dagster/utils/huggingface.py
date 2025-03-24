from transformers import pipeline, AutoTokenizer, AutoModel
import torch
from loguru import logger

class HuggingFaceProcessor:
    def __init__(self):
        # 情緒分析使用 distilbert-base-multilingual-cased
        self.sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-multilingual-cased")
        # 摘要生成使用 facebook/bart-large-cnn
        self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        # 向量嵌入使用 sentence-transformers/all-MiniLM-L6-v2
        self.tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        self.model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

    def get_sentiment(self, text):
        result = self.sentiment_analyzer(text[:512])[0]  # 限制長度
        return {"label": result["label"], "score": result["score"]}

    def get_summary(self, text):
        return self.summarizer(text, max_length=130, min_length=30, do_sample=False)[0]["summary_text"]

    def get_embedding(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).squeeze().tolist()

hf_processor = HuggingFaceProcessor()