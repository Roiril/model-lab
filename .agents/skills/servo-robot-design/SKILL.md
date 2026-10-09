---
name: servo-robot-design
description: model-lab で1サーボ駆動の小型かわいいロボット（および、サーボ/ホーン等の実物部品に嵌合する3Dプリント部品）を設計・印刷するときの設計原則・落とし穴・ワークフロー集。サーボマウント／ホーン結合／配線逃げ／目・耳アクセサリ／単位／boolean／検証／印刷分割／Blender手作業協調／サーボで蓋・扉を開ける箱を扱う。サーボを仕込むモデル、嵌合部品、頭が回る機構、ロボのアクセサリを作る時に必ず読む。
---

# 1サーボ・ロボット設計ガイド（Codex 用の入口）

本文の正本は **`.claude/skills/servo-robot-design/SKILL.md`**（Claude Code と共有）。先にそれを全部読む。
このファイルに中身を複製しない（2026-07-20 に複製した版が 3 か月古いまま残り、§0.5・§9.5 などが欠けていた）。

機構の設計・検証・刷る 3mf までの全体の手順は、共通スキル `printable-mechanism-design`
（`~/.agents/skills/printable-mechanism-design/`）にある。サーボで何かを動かす箱や機構を作るときは両方読む。

依頼の共通条件は `.agent/rules/model-request.md`、SG92R の寸法の正本は `models/sg92r-photo/`。
