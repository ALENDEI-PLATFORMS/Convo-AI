import sys
import pandas as pd
import openai
import numpy as np
from openai.embeddings_utils import distances_from_embeddings
from ast import literal_eval



def create_context(
        question, df, max_len=1800, size="ada"
):

    q_embeddings = openai.Embedding.create(input=question, engine='text-embedding-ada-002')['data'][0]['embedding']
    df['distances'] = distances_from_embeddings(q_embeddings, df['embeddings'].values, distance_metric='cosine')
    returns = []
    cur_len = 0

    for i, row in df.sort_values('distances', ascending=True).iterrows():
        cur_len += row['n_tokens'] + 4
        if cur_len > max_len:
            break
        returns.append(row["text"])

    # Return the context
    return "\n\n###\n\n".join(returns)


def answer_question(
        df,
        model="gpt-3.5-turbo-instruct",
        question="Am I allowed to publish model outputs to Twitter, without a human review?",
        max_len=1800,
        size="ada",
        debug=False,
        max_tokens=150,
        stop_sequence=None
):
    context = create_context(
        question,
        df,
        max_len=max_len,
        size=size,
    )
    # If debug, print the raw model response
    if debug:
        print("Context:\n" + context)
        print("\n\n")

    try:
        # Create a completions using the questin and context
        response = openai.Completion.create(
            prompt=f"Answer the question based on the context below, and if the question can't be answered based on the context, say \"I don't know\"\n\n\n\n---\n\nQuestion: {question}\nAnswer:",
            temperature=0,
            max_tokens=max_tokens,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=stop_sequence,
            model=model,
        )
        return response["choices"][0]["text"].strip()
    except Exception as e:
        print(e)
        return ""


def load_embeddings(file_path):
    df = pd.read_csv(file_path, index_col=0)
    df['embeddings'] = df['embeddings'].apply(literal_eval).apply(np.array)
    return df


def main():
    # Load embeddings from CSV file
    df = load_embeddings('embeddings.csv')
    answer = answer_question(df, question=Question, debug=False)
    print(answer)
    # print(answer_question(df, question="what does alndei do?", debug=False))


if __name__ == "__main__":
    Question = sys.argv[1]
    main()
