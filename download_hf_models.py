from transformers import pipeline, AutoTokenizer, AutoModel
import os

# 設置儲存目錄
models_dir = "backend/app/dagster/utils/models"
os.makedirs(models_dir, exist_ok=True)

# 下載並儲存情感分析模型
print("Downloading distilbert-base-multilingual-cased...")
sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-multilingual-cased")
sentiment_analyzer.save_pretrained(os.path.join(models_dir, "distilbert-base-multilingual-cased"))

# 下載並儲存摘要模型
print("Downloading facebook/bart-large-cnn...")
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
summarizer.save_pretrained(os.path.join(models_dir, "facebook-bart-large-cnn"))

# 下載並儲存嵌入模型
print("Downloading sentence-transformers/all-MiniLM-L6-v2...")
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
tokenizer.save_pretrained(os.path.join(models_dir, "sentence-transformers-all-MiniLM-L6-v2"))
model.save_pretrained(os.path.join(models_dir, "sentence-transformers-all-MiniLM-L6-v2"))

print("All models downloaded and saved locally.")