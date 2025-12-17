# CHORD: Collaborative Home-Robot Dialogue

<p align="center">
  <a href="#english">English</a> | <a href="#japanese">日本語</a>
</p>

<a name="japanese"></a>

## 📖 概要
**CHORD** (Collaborative Home-Robot Dialogue) は、LLM搭載家庭用ロボットとの協調タスクにおける対話スタイルが、ユーザーとのラポールおよびタスク遂行に与える影響を検証するために開発されたデモアプリケーションです。GPT-4o-miniを搭載したロボットエージェントとチャット形式で対話を行いながら、家事タスク（テーブル準備や花を生けるなど）を共同で行うことができます。

本リポジトリには、実験で使用されたStreamlitアプリケーション、プロンプト設計、および実験関連資料が含まれています。

### システム構成
- **Frontend/Backend:** Python / Streamlit
- **LLM:** OpenAI GPT-4o-mini
- **Infrastructure:** Google Cloud Platform (Cloud Run)
- **Database:** Cloud Firestore (状態管理・ログ保存)

## 🔬 研究内容

本システムは、以下の研究の一環として開発・使用されました。
> 「LLM搭載家庭用ロボットの対話スタイルがラポールとタスク性能に与える影響」
> 吉田 馨, 山本 匠, 小橋 洋平, 杉浦 裕太

[研究内容とアプリ操作マニュアルはこちら](https://docs.google.com/presentation/d/170fsT62Pm_U1_FMcTsrCM27pVbMOy9_ZlhFZP5KOkxw/edit?usp=sharing)

現在、ソーシャルロボットを除く多くのロボットは「指示＋応答型」の効率重視のインタラクションスタイルを採用しており、最短時間でタスクを遂行することを目的としています。
しかし、このようなスタイルでは、ユーザが求める結果とは異なる出力を生じたり、ユーザ側に不要なストレスや違和感を引き起こしたりする恐れがあります。
今後、ロボットと人との関係がより親密で協調的になるにつれ、単なる効率だけでなく、「人が思う通りに動く」ような体験を重視したインタラクション設計が求められるようになると考えています。
本研究では、家庭内での協調作業において、どのような「コミュニケーションスタイル」がユーザーとの信頼構築やタスク効率に寄与するかを明らかにすることを目的としています。

## 🤖 プロンプト設計

本研究では、システムプロンプト内の指示を書き換えることでロボットの人格（対話スタイル）を制御しています。各スタイルの定義は以下の通りです。
※ 実際のプロンプトファイルは `prompts/` ディレクトリを参照してください。

## 📝 アンケート質問項目

本実験では、以下の指標を用いて評価を行いました。

### NASA-TLX（認知負荷）

* **精神的要求 (Mental Demand)**
  * あなたは，ロボットと会話をするにあたって，精神的要求（思考，意志決定，計算，記憶，観察，検索，等）がどれくらい要求されましたか？
* **身体的要求 (Physical Demand)**
  * あなたは，ロボットと会話をするにあたって，身体的要求（押す，引く，回す， 操作する等）がどれくらい要求されましたか？
* **時間的切迫感 (Temporal Demand)**
  * あなたは，ロボットと会話をするにあたって，時間的切迫感（作業や要素作業の頻度や速さ）をどの程度感じましたか？
* **作業達成度 (Performance)**
  * ロボットと会話をするにあたって，あなた自身が想定した作業（指示）は，どの程度ロボットによって達成されたと考えますか？
* **努力 (Effort)**
  * あなたはその作業達成率に到達するのに，どのくらい（精神的及び身体的に）努力しましたか？
* **不満 (Frustration)**
  * あなたは，ロボットと会話をするにあたってどのくらい不安，落胆，いらいら，ストレス，不快感を感じましたか？

### Trust Scale (信頼尺度)
以下の項目について，同意できる度合いを回答として得ました。

1. このロボットは能力が高いと信じる
2. 私はこのロボットを信頼している
3. このロボットの助言（アドバイス）は信頼できる
4. 私はこのロボットに頼れる
5. このロボットの動作（ふるまい）は一貫していると思う
6. このロボットの助言に従うとき，このロボットは最善を尽くしてくれると信頼している

### Godspeed Questionnaire Series（ロボットの印象）

#### Anthropomorphism (擬人化)
* Fake 偽物のような -- Natural 自然な
* Machinelike 機械的 -- Humanlike 人間的
* Unconscious 意識を持たない -- Conscious 意識を持っている
* Artificial 人工的 -- Lifelike 生物的
* Moving rigidly ぎこちない動き -- Moving elegantly 洗練された動き

#### Animacy (生物らしさ)
* Dead 死んでいる -- Alive 生きている
* Stagnant 活気のない -- Lively 生き生きとした
* Mechanical 機械的な -- Organic 有機的な
* Inert 不活発な -- Interactive 対話的な
* Apathetic 無関心な -- Responsive 反応のある

#### Likeability (好感度)
* Dislike 嫌い -- Like 好き
* Unfriendly 親しみにくい -- Friendly 親しみやすい
* Unkind 不親切な -- Kind 親切な
* Unpleasant 不愉快な -- Pleasant 愉快な
* Awful ひどい -- Nice 良い

#### Perceived Intelligence (知能の知覚)
* Incompetent 無能な -- Competent 有能な
* Ignorant 無知な -- Knowledgeable 物知りな
* Irresponsible 無責任な -- Responsible 責任のある
* Unintelligent 知的でない -- Intelligent 知的な
* Foolish 愚かな -- Sensible 賢明な

#### Perceived Safety (安全性の知覚)
* Anxious 不安な -- Relaxed 落ち着いた
* Agitated 動揺している -- Calm 冷静な
* Quiescent 平穏な -- Surprised 驚いた

## 🙌 謝辞

本調査には、**東京大学松尾・岩澤研究室 LLM コミュニティのプログラム LLMATCH** にご協力頂きました。
ここに深く感謝の意を表します。

---

<a name="english"></a>

## 📖 Overview
**CHORD** (Collaborative Home-Robot Dialogue) is a demo application developed to verify how dialogue styles in collaborative tasks with LLM-equipped home robots affect user rapport and task performance. Users can perform household chores (such as setting the table or arranging flowers) collaboratively while conversing in a chat format with a robot agent equipped with GPT-4o-mini.

This repository contains the Streamlit application used in the experiment, prompt designs, and materials related to the experiment.

### System Configuration
- **Frontend/Backend:** Python / Streamlit
- **LLM:** OpenAI GPT-4o-mini
- **Infrastructure:** Google Cloud Platform (Cloud Run)
- **Database:** Cloud Firestore (State management & Log storage)

## 🔬 Research Content

This system was developed and used as part of the following research:
> **"Impact of Dialogue Styles of LLM-Equipped Home Robots on Rapport and Task Performance"**
> Kaoru Yoshida, Takumi Yamamoto, Yohei Kobashi, Yuta Sugiura

[Click here for Research Details and App Operation Manual](https://docs.google.com/presentation/d/1xf68kw2iPy8MDEDAiTzxTcADPmQyeoh8rcNLgo7zWf8/edit?usp=sharing)

Currently, many robots (excluding social robots) adopt an efficiency-oriented "Instruction + Response" interaction style, aiming to complete tasks in the shortest possible time.
However, this style risks producing outputs different from what the user desires or causing unnecessary stress and discomfort for the user.
As the relationship between robots and humans becomes more intimate and collaborative in the future, we believe interaction design that emphasizes an experience where the robot "moves as the user intends"—rather than just pure efficiency—will become essential.
The purpose of this study is to clarify what kind of "communication style" contributes to building trust with the user and improving task efficiency in collaborative household work.

## 🤖 Prompt Design

In this study, we control the robot's persona (dialogue style) by rewriting instructions within the system prompt. The definitions of each style are as follows:
*Note: Please refer to the `prompts/` directory for the actual prompt files.*

## 📝 Survey Questions

In this experiment, evaluations were conducted using the following metrics.

### NASA-TLX (Cognitive Load)

* **Mental Demand**
  * How much mental and perceptual activity was required (e.g., thinking, deciding, calculating, remembering, looking, searching, etc.) while conversing with the robot?
* **Physical Demand**
  * How much physical activity was required (e.g., pushing, pulling, turning, controlling, activating, etc.) while conversing with the robot?
* **Temporal Demand**
  * How much time pressure did you feel due to the rate or pace at which the tasks or task elements occurred while conversing with the robot?
* **Performance**
  * How successful do you think you were in accomplishing the goals of the task set by yourself while conversing with the robot?
* **Effort**
  * How hard did you have to work (mentally and physically) to accomplish your level of performance?
* **Frustration**
  * How insecure, discouraged, irritated, stressed, and annoyed did you feel while conversing with the robot?

### Trust Scale
Participants answered the degree to which they agreed with the following items:

1. I believe this robot is capable.
2. I trust this robot.
3. This robot's advice is trustworthy.
4. I can rely on this robot.
5. I think this robot's behavior is consistent.
6. I trust that this robot will do its best when I follow its advice.

### Godspeed Questionnaire Series (Impression of the Robot)

#### Anthropomorphism
* Fake — Natural
* Machinelike — Humanlike
* Unconscious — Conscious
* Artificial — Lifelike
* Moving rigidly — Moving elegantly

#### Animacy
* Dead — Alive
* Stagnant — Lively
* Mechanical — Organic
* Inert — Interactive
* Apathetic — Responsive

#### Likeability
* Dislike — Like
* Unfriendly — Friendly
* Unkind — Kind
* Unpleasant — Pleasant
* Awful — Nice

#### Perceived Intelligence
* Incompetent — Competent
* Ignorant — Knowledgeable
* Irresponsible — Responsible
* Unintelligent — Intelligent
* Foolish — Sensible

#### Perceived Safety
* Anxious — Relaxed
* Agitated — Calm
* Quiescent — Surprised

## 🙌 Acknowledgements

This survey was conducted with the cooperation of **LLMATCH, a program by the Matsuo-Iwasawa Lab LLM Community at the University of Tokyo.**
We would like to express our deepest gratitude.
