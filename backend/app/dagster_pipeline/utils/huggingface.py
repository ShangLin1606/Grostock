from transformers import pipeline, AutoTokenizer, AutoModel
import torch
from loguru import logger
import os

class HuggingFaceProcessor:
    def __init__(self):
        models_dir = os.path.join(os.path.dirname(__file__), "models")
        sentiment_model_path = os.path.join(models_dir, "distilbert-base-multilingual-cased")
        summarization_model_path = os.path.join(models_dir, "facebook-bart-large-cnn")
        embedding_model_path = os.path.join(models_dir, "sentence-transformers-all-MiniLM-L6-v2")

        # 使用本地模型路徑
        if os.path.exists(sentiment_model_path):
            self.sentiment_analyzer = pipeline("sentiment-analysis", model=sentiment_model_path)
            logger.info(f"Loaded sentiment analysis model from local: {sentiment_model_path}")
        else:
            self.sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-multilingual-cased")
            logger.info("Loaded sentiment analysis model from HuggingFace Hub")

        if os.path.exists(summarization_model_path):
            self.summarizer = pipeline("summarization", model=summarization_model_path)
            logger.info(f"Loaded summarization model from local: {summarization_model_path}")
        else:
            self.summarizer = pipeline("summarization", model="facebook-bart-large-cnn")
            logger.info("Loaded summarization model from HuggingFace Hub")

        if os.path.exists(embedding_model_path):
            self.tokenizer = AutoTokenizer.from_pretrained(embedding_model_path)
            self.embedding_model = AutoModel.from_pretrained(embedding_model_path)
            logger.info(f"Loaded embedding model from local: {embedding_model_path}")
        else:
            self.tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
            self.embedding_model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
            logger.info("Loaded embedding model from HuggingFace Hub")

    def get_sentiment(self, text):
        logger.info(f"Analyzing sentiment for text: {text[:50]}...")
        result = self.sentiment_analyzer(text[:512])[0]
        logger.info(f"Sentiment result: {result}")
        return {"label": result["label"], "score": result["score"]}

    def get_summary(self, text):
        logger.info(f"Generating summary for text: {text[:50]}...")
        summary = self.summarizer(text, max_length=130, min_length=30, do_sample=False)[0]["summary_text"]
        logger.info(f"Summary: {summary}")
        return summary

    def get_embedding(self, text):
        logger.info(f"Generating embedding for text: {text[:50]}...")
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)
        embedding = outputs.last_hidden_state.mean(dim=1).squeeze().tolist()
        logger.info(f"Embedding generated (length: {len(embedding)})")
        return embedding

# 實例化處理器
hf_processor = HuggingFaceProcessor()

if __name__ == "__main__":
    sample_text = """
    The stock market has been performing exceptionally well this year, with major indices reaching all-time highs. 
    Investors are optimistic about the economic recovery, despite some concerns about inflation and interest rates. 
    Technology stocks, in particular, have seen significant gains, driven by strong earnings reports and innovation.
    """
    sentiment = hf_processor.get_sentiment(sample_text)
    print("Sentiment:", sentiment)
    summary = hf_processor.get_summary(sample_text)
    print("Summary:", summary)
    embedding = hf_processor.get_embedding(sample_text)
    print("Embedding (first 5 values):", embedding[:5])