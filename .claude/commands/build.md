モデル「$ARGUMENTS」をビルドしてビューワーに反映してください。

## 手順

1. `models/$ARGUMENTS/model.py` が存在するか確認する
   - なければ「モデルが見つかりません。/new-model $ARGUMENTS で作成できます」と伝える

2. ビューワーサーバーが起動しているか確認する
   ```
   curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/
   ```
   - 200 以外なら `node server.js` をバックグラウンドで起動する

3. Blenderでビルドを実行する
   ```
   ./run.sh models/$ARGUMENTS/model.py
   ```

4. 結果を報告する
   - 成功: `exports/$ARGUMENTS.stl` が生成されたことを伝える
   - 失敗: エラー内容を読んで原因を特定・修正してリトライする

5. ユーザーに伝える
   - http://localhost:3000 でモデルが確認できること
   - `params.py` から読み取れる外形寸法（W × D × H mm）
   - 設計上の注意点があれば補足する
