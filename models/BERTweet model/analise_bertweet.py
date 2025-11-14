from transformers import pipeline
from collections import Counter
import json
import os

# Configurações gerais
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_NAME = "finiteautomata/bertweet-base-sentiment-analysis"
INPUT_FILE = os.path.join(
    BASE_DIR,
    '..',
    "PRs_comments",
    "pr_comments_2noise_ChatTTS_closed_nobots_True.json"
)
OUTPUT_FILE = "sentiments_bertweet.json"

# Função auxiliar para normalizar labels
def normalize_label(label: str) -> str:
    label = label.strip().lower()
    if "neg" in label:
        return "NEGATIVE"
    elif "neu" in label:
        return "NEUTRAL"
    elif "pos" in label:
        return "POSITIVE"
    else:
        return label.upper()
 
# Inicialização do modelo
print(f"🚀 Carregando modelo {MODEL_NAME}...")
analyzer = pipeline(
    "sentiment-analysis",
    model=MODEL_NAME,
    tokenizer=MODEL_NAME,
    truncation=True,
    max_length=128
)
print("✅ Modelo carregado com sucesso!\n")

# Leitura do arquivos JSON de PRs
with open(INPUT_FILE, encoding="utf-8") as f:
    data = json.load(f)

comments = []
for pr in data["prs"]:
    for comment in pr["comments"]:
        body = comment["body"].strip()
        if body:  # ignora comentários vazios
            comments.append({
                "pr_number": pr["number"],
                "user": comment["user"],
                "text": body
            })

print(f"💬 Total de comentários coletados: {len(comments)}\n")

# Análise de sentimentos
results = []
for i, c in enumerate(comments, 1):
    text = c["text"]
    try:
        sentiment = analyzer(text, truncation=True, max_length=128)[0]
        label = normalize_label(sentiment["label"])
        score = round(sentiment["score"], 3)

        results.append({
            "pr_number": c["pr_number"],
            "user": c["user"],
            "text": text,
            "label": label,
            "score": score
        })

        if i % 20 == 0:
            print(f"🔎 Processados {i}/{len(comments)} comentários...")

    except Exception as e:
        print(f"⚠️ Erro ao processar comentário do PR #{c['pr_number']}: {e}")

# Salvando resultados
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"💾 Resultados salvos em {OUTPUT_FILE}\n")

# Gerando resumo dos sentimentos
counts = Counter([r["label"] for r in results])
total = sum(counts.values())

print("--- 📊 Resultados ---")
for label in ["POSITIVE", "NEUTRAL", "NEGATIVE"]:
    count = counts.get(label, 0)
    print(f"{label:<8}: {count:3} ({count/total:.1%})")

print(f"\nTotal de comentários analisados: {total}")