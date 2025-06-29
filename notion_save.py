### 📄 notion_save.py — Markdown整形 + 長文分割に対応（改行・見出し・強調付き）

import os
from notion_client import Client
from datetime import datetime
import re

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
DATABASE_ID = "21a37769f27c80b890c9c22b5a25219e"

notion = Client(auth=NOTION_API_KEY)

def split_text(text, max_length=1900):
    """
    テキストをNotionの制限（2000文字未満）で分割する
    """
    chunks = []
    while len(text) > max_length:
        split_point = text[:max_length].rfind("\n")
        if split_point == -1:
            split_point = max_length
        chunks.append(text[:split_point].strip())
        text = text[split_point:].strip()
    chunks.append(text)
    return chunks

def markdown_to_notion_blocks(md_text):
    """
    Markdown形式のテキストをNotionのリッチテキストブロックに変換
    - 見出し（#）
    - 太字（**）
    - 改行
    """
    blocks = []
    lines = md_text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.startswith("### "):
            blocks.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{"type": "text", "text": {"content": line[4:]}}]
                }
            })
        elif line.startswith("## "):
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": line[3:]}}]
                }
            })
        elif line.startswith("# "):
            blocks.append({
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"type": "text", "text": {"content": line[2:]}}]
                }
            })
        else:
            segments = re.split(r"(\\*\\*.*?\\*\\*)", line)
            rich_text = []
            for segment in segments:
                if segment.startswith("**") and segment.endswith("**"):
                    bold_text = segment[2:-2]
                    rich_text.append({"type": "text", "text": {"content": bold_text}, "annotations": {"bold": True}})
                else:
                    rich_text.append({"type": "text", "text": {"content": segment}})

            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": rich_text
                }
            })
    return blocks

def save_discussion_to_notion(title, content):
    try:
        page = notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "Name": {"title": [{"text": {"content": f"{title}_{datetime.now().strftime('%Y%m%d')}"}}]}
            }
        )

        text_chunks = split_text(content)
        for chunk in text_chunks:
            blocks = markdown_to_notion_blocks(chunk)
            for i in range(0, len(blocks), 10):
                notion.blocks.children.append(
                    block_id=page["id"],
                    children=blocks[i:i+10]
                )

        return True
    except Exception as e:
        print(f"Error saving to Notion: {e}")
        return False
