# CONTRIBUTING

---

## 前置準備

### 背景知識

網站開發:
docker > python > django

系統開發:
Docker, Jenkins, GitLab, Sonarqube

---

## 開始進行開發

1. 準備好資料庫與元件服務(docker)
2. `pip install -r requirements.txt`
3. 將 `flowlab` 下的 `local_settings.example` 複製成副檔名為 `.py` 的同名檔案，並配置好內容(參考 example)
4. `python manage.py runserver 0.0.0.0:8000`

## Git 貢獻提交規範
> 參考規範  
> [vue](https://github.com/vuejs/vue/blob/dev/.github/COMMIT_CONVENTION.md)  
> [Angular](https://github.com/conventional-changelog/conventional-changelog/tree/master/packages/conventional-changelog-angular)  
> [vben-admin-thin-next](https://github.com/anncwb/vben-admin-thin-next/blob/main/README.md)  

- `feat`: 增加新功能
- `fix`: 修復問題/BUG
- `style`: 程式碼風格相關，不影響運行結果
- `perf`: 優化/性能提升
- `refactor`: 重構
- `revert`: 撤銷修改
- `test`: 測試相關
- `docs`: 文件/註解
- `chore`: 依賴更新/修改設定檔等
- `ci`: 持續集成
- `wip`: 開發中

更多內容可以在 `docs` 資料夾下面找找看，如果沒有找到也歡迎開啟新的 issue，讓我們一起盡力改善！
