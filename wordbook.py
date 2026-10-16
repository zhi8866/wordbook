import streamlit as st
import json
import os
import pandas as pd

DATA_FILE = "word_list.json"

def load_words():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_words(word_list):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(word_list, f, ensure_ascii=False, indent=2)

words = load_words()

st.set_page_config(page_title="单词本", layout="wide")
st.title("📖 我的单词本（带朗读+Excel导入）")

st.subheader("📥 从Excel批量导入单词")
upload_file = st.file_uploader("上传你的单词.xlsx，表头必须为：单词、词义、例句", type=["xlsx"])
if upload_file is not None:
    try:
        df = pd.read_excel(upload_file, engine="openpyxl")
        df = df[["单词", "词义", "例句"]].dropna(how="all")
        st.dataframe(df, use_container_width=True)
        if st.button("✅ 确认导入到词库"):
            add_count = 0
            for _, row in df.iterrows():
                wd = str(row["单词"]).strip()
                mean = str(row["词义"]).strip()
                sent = str(row["例句"]).strip()
                exist = any(item["word"] == wd for item in words)
                if wd and not exist:
                    words.append({
                        "word": wd,
                        "mean": mean,
                        "sentence": sent
                    })
                    add_count += 1
            save_words(words)
            st.success(f"导入完成！新增 {add_count} 条单词")
    except Exception as e:
        st.error(f"读取Excel失败：{e}\n检查表头名称是否是【单词、词义、例句】")

st.divider()
st.subheader("➕ 添加新单词")
col1, col2, col3 = st.columns(3)
with col1:
    new_word = st.text_input("单词")
with col2:
    new_mean = st.text_input("词义")
with col3:
    new_sent = st.text_input("例句")

if st.button("保存单词"):
    if new_word.strip():
        exists = any(x["word"] == new_word.strip() for x in words)
        if exists:
            st.warning("该单词已存在！")
        else:
            words.append({
                "word": new_word.strip(),
                "mean": new_mean.strip(),
                "sentence": new_sent.strip()
            })
            save_words(words)
            st.success("保存成功！")

st.divider()
st.subheader("📚 单词列表（点击朗读，可删除）")
if len(words) == 0:
    st.info("单词库为空，请添加单词或上传Excel！")
else:
    for idx, item in enumerate(words):
        w = item["word"]
        m = item["mean"]
        s = item["sentence"]
        c1,c2,c3,c4 = st.columns([2,2,3,1])
        with c1:
            st.write(f"**{w}**")
        with c2:
            st.write(m)
        with c3:
            st.write(s)
        with c4:
            if st.button("朗读", key=f"read_{idx}"):
                st.markdown(f'<script>window.speechSynthesis.speak(new SpeechSynthesisUtterance("{w}"))</script>', unsafe_allow_html=True)
        with st.expander("删除本条"):
            if st.button("确认删除", key=f"del_{idx}"):
                del words[idx]
                save_words(words)
                st.rerun()

st.divider()
st.subheader("🎲 随机复习")
if st.button("抽取单词复习"):
    import random
    if words:
        pick = random.choice(words)
        st.info(f"""
**单词：{pick['word']}**
词义：{pick['mean']}
例句：{pick['sentence']}
""")
    else:
        st.warning("词库为空！")
