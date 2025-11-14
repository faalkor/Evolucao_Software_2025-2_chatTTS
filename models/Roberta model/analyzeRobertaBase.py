from transformers import pipeline
from collections import Counter
import json

# === CONFIGURAÇÃO ===
MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"
INPUT_FILE = "../../PRs_comments/pr_comments_2noise_ChatTTS_closed_nobots_True.json"
OUTPUT_FILE = "sentiments_roberta.json"

# === FUNÇÃO DE NORMALIZAÇÃO DE LABEL ===
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

# === CARREGAR MODELO ===
print(f"Carregando modelo {MODEL_NAME}...")
analyzer = pipeline("sentiment-analysis", model=MODEL_NAME)
print("✅ Modelo carregado com sucesso!\n")

# === LER JSON DOS 100 PRs ===
with open(INPUT_FILE, encoding="utf-8") as f:
    data = json.load(f)

# === EXTRAIR TODOS OS COMENTÁRIOS ===
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

print(f"Total de comentários coletados: {len(comments)}\n")

# === RODAR ANÁLISE DE SENTIMENTOS ===
results = []
for c in comments:
    text = c["text"][:512]
    sentiment = analyzer(text)[0]

    label = normalize_label(sentiment["label"])
    score = round(sentiment["score"], 3)

    results.append({
        "pr_number": c["pr_number"],
        "user": c["user"],
        "text": text,
        "label": label,
        "score": score
    })

# === SALVAR RESULTADOS DETALHADOS ===
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"✅ Resultados salvos em {OUTPUT_FILE}\n")

# === GERAR RESUMO ESTATÍSTICO ===
counts = Counter([r["label"] for r in results])
total = sum(counts.values())

print("=== 📊 RESUMO DE SENTIMENTOS ===")
for label in ["POSITIVE", "NEUTRAL", "NEGATIVE"]:
    count = counts.get(label, 0)
    print(f"{label:<8}: {count:3} ({count/total:.1%})")

print(f"\nTotal de comentários analisados: {total}")
