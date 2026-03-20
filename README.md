# FG Sprite Composer（立绘合成器）

一个用于窗社和类似视觉小说引擎立绘合成的小工具。

A simple tool for composing character sprites (FG) for visual novel engines (especially Madosoft-like engines).

ビジュアルノベル（特にまどそふと系エンジン）向けの立ち絵合成ツールです。

---

## ✨ 功能 / Features / 機能

- 批量合成身体 + 表情图片  
- 支持预览单组立绘  
- 自动读取 PNG 中的位置信息（pos,x,y,...）  
- 支持导出单张或批量导出  



- Batch composition of body + expression images  
- Live preview for selected pair  
- Automatically reads position metadata from PNG (pos,x,y,...)  
- Export single preview or batch export  



- 体＋表情画像の一括合成  
- 選択した組み合わせのプレビュー表示  
- PNG 内の位置情報（pos,x,y,...）を自動取得  
- 単体・一括エクスポート対応  

---

## 📦 使用方法 / Usage / 使い方

👉 请在 Release 页面下载 `.exe` 文件并直接运行  
👉 Download the `.exe` from Releases and run it directly  
👉 Release から `.exe` をダウンロードして実行してください  

基本流程：

1. 添加身体图片（Body）  
2. 添加表情图片（Expression）  
3. 选择输出路径  
4. 点击合成或导出  


Basic steps:

1. Add body images  
2. Add expression images  
3. Select output folder  
4. Start composition or export  


基本手順：

1. 体画像を追加  
2. 表情画像を追加  
3. 出力フォルダを選択  
4. 合成またはエクスポートを実行  

---

## 🧠 原理说明 / How it works / 仕組み

通过分析游戏内的 Lua 脚本，提取出立绘合成所使用的位置规则。  
只要 PNG 图片中包含对应的位置信息（pos,x,y,...），即可自动对齐并完成合成。

The tool is based on analyzing Lua scripts from the game, which define how character sprites are composed.  
As long as the PNG images contain position metadata (pos,x,y,...), the tool can automatically align and compose them.

ゲーム内の Lua スクリプトを解析し、立ち絵合成の位置情報ルールを再現しています。  
PNG に含まれる位置情報（pos,x,y,...）を利用して、自動的に合成を行います。

---

## 🎮 已测试游戏 / Tested Games / 動作確認済みタイトル

目前已在以下游戏中测试可用：

- 《常轨脱离creative》  
  Hamidashi Creative  
  ハミダシクリエイティブ  


- 《天选庶民的真命之选》  
  Select Oblige  
  セレクトオブリージュ

---

## ⚠️ 注意事项 / Notes / 注意事項

- 仅支持 PNG 图片  
- 依赖图片中内嵌的位置信息  
- 若图片没有 pos 信息，默认按 (0,0) 处理  



- Only PNG images are supported  
- Requires embedded position metadata  
- Images without position data will default to (0,0)  



- PNG のみ対応  
- 位置情報が埋め込まれている必要があります  
- 位置情報がない場合は (0,0) として処理されます  

---

## 📄 License

MIT License
