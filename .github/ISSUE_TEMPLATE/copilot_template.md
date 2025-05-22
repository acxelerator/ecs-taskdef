---
name: リクエスト
about: このプロジェクトに「機能」を追加する
title: "[FEATURE]"
labels: enhancement
assignees: 'copilot'
---


## 問題の説明
<!-- 問題の明確かつ簡潔な説明。例: 私はいつも [...]のときに困っています -->

## 提案する解決策
<!-- 実現したいことの明確かつ簡潔な説明 -->

# 確認事項

修正後に以下の内容を確認してください

## コード整形

修正後に以下の2つのコマンドが通ることを確認してください

- `$ ruff check`
- `$ ruff format --check .`

## テスト

修正後にテストが通ることを確認してください

- `$ rye run python -m pytest --cov=ecs_taskdef`
