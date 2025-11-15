from models.BERTweet.analise_bertweet import run_bertweet
from models.Multilingual.analyzeMultilingual import run_multilingual
from models.Roberta.analyzeRobertaBase import run_roberta

def main():
    print("=== Executando BERTweet ===")
    bertweet_results = run_bertweet()

    print("\n=== Executando Multilingual ===")
    multilingual_results = run_multilingual()

    print("\n=== Executando RoBERTa ===")
    roberta_results = run_roberta()

    print("\n\n=== FINALIZADO ===")
    print(f"BERTweet: {len(bertweet_results)} comentários analisados")
    print(f"Multilingual: {len(multilingual_results)} comentários analisados")
    print(f"RoBERTa: {len(roberta_results)} comentários analisados")

if __name__ == "__main__":
    main()
