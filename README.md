<!-- Project Title / プロジェクト名 -->
<h1 align="center">ChatGPT for Home Robots: Emotionally-Aware Robotics & AI</h1>
<!-- <p align="center">
  <a href="https://github.com/PLACEHOLDER/actions"><img alt="CI" src="https://img.shields.io/github/actions/workflow/status/PLACEHOLDER/ci.yml?label=CI"></a>
  <a href="https://github.com/PLACEHOLDER/stargazers"><img alt="Stars" src="https://img.shields.io/github/stars/PLACEHOLDER?style=social"></a>
  <a href="https://opensource.org/licenses/MIT"><img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-green.svg"></a>
</p> -->

<p align="center">
  <!-- <i>Robotics × LLM × Human connection — because technology should help people feel seen, heard, and valued.</i><br/>
  <i>テクノロジーを「便利」から「幸せ」へ。人の感情とつながるロボティクス&AI。</i> -->
</p>

---
## Abstract / 概要
ChatGPT for Home Robots is a research & engineering program exploring how **LLM-powered communication styles** (task-oriented, empathetic, and pratfall-friendly) affect **trust, task success, and user experience** in **home robotics**. We integrate LLM planning and a human-in-the-loop evaluation platform (Streamlit). Our aim is technology that supports emotional well-being, not just convenience.

ChatGPT for Home Robots は、**LLM のコミュニケーションスタイル**（情報提供型・共感型・雑談型）が、**家庭内ロボット**における**信頼・タスク成功・ユーザ体験**に与える影響を検証する研究開発プログラムです。LLM による計画、Streamlit による評価基盤を統合し、「便利さ」だけでなく感情的な充実に資するテクノロジーを目指します。

---

## 🎬 Demo / デモ

<!-- ▼ どちらか使いやすい方を：YouTube 埋め込み（サムネイルリンク） -->
<!-- <p align="center">
  <a href="https://youtu.be/PLACEHOLDER" target="_blank">
    <img src="assets/thumbnail_main.jpg" alt="Demo Video" width="75%"/>
  </a>
</p>
<p align="center">
  <a href="https://youtu.be/PLACEHOLDER">▶ Watch the full demo on YouTube</a> | 
  <a href="https://youtu.be/PLACEHOLDER2">▶ Short: 60s overview</a>
</p> -->

<!-- ▼ もしくは GIF（軽量プレビュー） -->
<p align="center"><img src="assets/demo_loop.gif" width="75%" /></p>

<!-- ### Video Layout Suggestion（動画レイアウト例）
- **Main demo**（全体像）＋ **Shorts/clip**（要点60秒）
- **Use-case grid**: 3 つの短い動画を横並び（対話計画 / 実機動作 / 評価GUI）  
  <table>
    <tr>
      <td align="center"><a href="https://youtu.be/PLACEHOLDER_A"><img src="assets/thumb_plan.jpg" width="100%"><br/>Planning</a></td>
      <td align="center"><a href="https://youtu.be/PLACEHOLDER_B"><img src="assets/thumb_control.jpg" width="100%"><br/>Robot Control</a></td>
      <td align="center"><a href="https://youtu.be/PLACEHOLDER_C"><img src="assets/thumb_eval.jpg" width="100%"><br/>Evaluation UI</a></td>
    </tr>
  </table> -->

---

## 🧭 Features / 主な機能

- **Dialogue → Plan(JSON) → Action**: 自然言語から構造化プランを生成し、実行まで接続  
- **Style Switching**: 情報提供型 / 共感型 / 雑談型の対話スタイル切替  
- **Evaluation UI**: `streamlit_app.py` による評価・デモ UI（同意取得モジュール `consent.py` あり）  
- **Planning & Motion Helpers**: `move_functions.py`, `strips.py`, `room_utils.py` など  
- **Data/Logging**: `clarify_logger.py`, `jsonl.py` でログ・データ出力

---

## 🚀 Quickstart / クイックスタート

```bash
# 0) Python
# Use Python 3.10+ (check requirements.txt for exact pins)
# requirements.txt is included in the repo.
# 1) Clone
git clone https://github.com/kochamii-312/chatgpt_for_home_robots
cd chatgpt_for_home_robots

# 2) Install
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3) Run the Streamlit demo UI
streamlit run streamlit_app.py

# 4) (Optional) API server (if you use backend endpoints)
python api.py
```

---

## 🔧 Configuration / 設定

- Env / Secrets: API キーや評価用の保存先がある場合は .env などで管理
- Firebase / GCP: firebase_utils.py と .gcloudignore があるため、Firebase/GCP 連携の構成を想定（必要に応じて認証情報を配置）
- Procfile: プロセス定義があるため、PaaS（Render/Heroku 等）へのデプロイの雛形として利用可能
- Task completion images: デプロイ環境で `images/` ディレクトリを含めない場合は、同じパス構造の画像をホスティングした CDN / Cloud Storage の URL を `st.secrets["image_base_url"]` または環境変数 `IMAGE_BASE_URL` で指定してください（HTTP(S) URL はローカルファイルと同様に表示されます）。

---

## 🖼️ Suggested Repo Structure Highlights / 構成ハイライト
```bash
images/           # サムネイル・GIF 等（README から参照）
pages/            # UI ページ/セクション（Streamlit マルチページ運用時）
models/           # モデル関連（プロンプト/重み/設定など）
tasks/            # タスク定義・サンプル
api.py            # バックエンド API
streamlit_app.py  # 評価・デモ UI のエントリ
consent.py        # 研究用の同意取得
move_functions.py # アクション/モーション補助
strips.py         # 計画ロジック補助（STRIPS 風）
```

---

## 🗣️ Communication Styles / 対話スタイル

- **Logical（情報提供型）**: 手順を簡潔に提示
- **Empathetic（共感型）**: 感情に寄り添い安心感を提供
- **Pratfall（雑談型）**: 親近感・温かみを演出

---

## ✨ Supported by LLMATCH program

This project is supported by LLMATCH program conducted by LLM community by Matsuo-Iwasawa lab in the University of Tokyo.
LLMATCH is a program designed to meet the diverse needs of students—whether you have an idea but don't know how to proceed, want to gain experience in LLM development, or wish to apply LLMs to your research.

このプロジェクトは、東京大学松尾・岩澤研究所LLMコミュニティ主催のLLMATCHプログラムからサポートを受けています。
LLMATCH は、アイデアはあるけどどう進めればいいかわからない、LLM開発の実績を積みたい、自分の研究でLLMを応用したいなど、学生の様々な希望に応えるプログラムです。
