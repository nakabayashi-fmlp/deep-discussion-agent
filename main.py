import streamlit as st
from langchain.chat_models import ChatOpenAI
from notion_save import save_discussion_to_notion
from datetime import datetime
import os
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# LLMの初期化
llm = ChatOpenAI(temperature=0.5, model_name="gpt-4")

# タイトル
st.title("Deep Discussion AI Agent")

# 入力UI
with st.form("discussion_form"):
    prompt = st.text_area("Prompt", height=150, placeholder="議論したいテーマを入力（改行可）")
    submitted = st.form_submit_button("Start")

# 議論スタート
if submitted and prompt:
    st.write("🚀 プロンプト実行中...")

    # ステータスバー（進捗表示）
    step_placeholder = st.empty()
    step_placeholder.info("Step 0 / 11 進行中...")

    # ステップ出力表示
    output_placeholder = st.container()
    discussion_log = []

    # ステップ 1: 初回スピーカー応答
    step_placeholder.info("Step 1 / 11")
    system_prompt = "あなたはSpeakerです。以下のテーマについてあなたの推論の限界まで考え、明晰かつ論理的に整理してください。"
    user_prompt = f"テーマ: {prompt}"
    response = llm.predict(system_prompt + "\n" + user_prompt)
    output_placeholder.markdown(f"### Step 1 - Speaker\n{response}")
    discussion_log.append(f"### Step 1 - Speaker\n{response}")

    # ステップ 2〜10: 交互対話（Speaker/Listener）
    for step in range(2, 11):
        role = "Listener" if step % 2 == 0 else "Speaker"

        if role == "Speaker":
            system_prompt = (
                "あなたはSpeakerです。以下の前の発言に対して、"
                "自分の考えを推論の限界まで掘り下げ、明晰で論理的に回答してください。"
            )
            user_prompt = discussion_log[-1]
            response = llm.predict(system_prompt + "\n" + user_prompt)
            output_placeholder.markdown(f"### Step {step} - Speaker\n{response}")
            discussion_log.append(f"### Step {step} - Speaker\n{response}")

        else:
            system_prompt = (
                "あなたはListenerです。以下の発言に対して、より深く掘り下げるための質問を3つ生成してください。\n"
                "次の3つの観点からそれぞれ1問ずつ作成してください：\n"
                "1. Clarify（明確化）\n"
                "2. Challenge（批判的検討）\n"
                "3. Connect（他の文脈との関連）"
            )
            user_prompt = discussion_log[-1]
            response = llm.predict(system_prompt + "\n" + user_prompt)
            output_placeholder.markdown(f"### Step {step} - Listener\n{response}")
            discussion_log.append(f"### Step {step} - Listener\n{response}")

        step_placeholder.info(f"Step {step} / 11")

    # ステップ 11: Speakerによるまとめ
    step_placeholder.info("Step 11 / 11")
    system_prompt = "あなたはSpeakerです。これまでの対話を踏まえ、論点が最も深まった内容を抽出して論理的に要約してください。日本語で。"
    user_prompt = "\n".join(discussion_log)
    response = llm.predict(system_prompt + "\n" + user_prompt)
    output_placeholder.markdown(f"### Step 11 - Speaker Summary\n{response}")
    discussion_log.append(f"### Step 11 - Speaker Summary\n{response}")

    # 保存処理
    title = prompt.strip().split("\n")[0][:30]
    success = save_discussion_to_notion(title=title, content="\n\n".join(discussion_log))
    if success:
        st.success("✅ 議論内容をNotionに保存しました")
    else:
        st.error("❌ Notionへの保存に失敗しました")
