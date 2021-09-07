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

---

## Django Coding Style

[Coding style](https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/coding-style/)

---

## django-app 結構規範

1. FBV or CBV
原則上使用FBV加速開發，但當符合下列條件時應使用CBV
    1. url 可以對應兩種以上的 http method, 且兩種方法的程式碼差異達 30% 以上時
    2. 想要繼承現有的通用 views class 時

使用 CBV 時, 應該把整個 view class 移動到單一檔案中  
並且如果存在 1 個以上的 views 檔案就應該將所有檔案放到 views 資料夾中

---

## core/static 規範

- 單個 `css`, `images` 或 `js` 的檔案直接放置於 `core/static/core/` 下
- 若該類別存在 1 個以上的檔案就應該將所有檔案放到 "該類別" 的資料夾中

例如：目前 `core/static/core` 下有 `flowlab-logo.png` 與 `devops.png` 兩份檔案  
則將這兩份檔案統一放置於 `core/static/core/images/` 下

---

## view.py 規範

1. 傳遞 `context` 參數時, 需要明確指名變數, 禁用 `locals()` 傳遞所有變數

---

## URL 字串格式

除了由 Django 指定格式的欄位以外
默認 URL 表示方法由順序在後的字串提供分隔符(/)
即，如果有一個 URL: `https://gitlab.example.com/api/v4/projects`
則在組織時應該拆分為如右格式: `https://gitlab.example.com` + `/api/v4` + `/projects`

---

## Git 貢獻提交規範
> 參考規範  
> [vue](https://github.com/vuejs/vue/blob/dev/.github/COMMIT_CONVENTION.md)  
> [Angular](https://github.com/conventional-changelog/conventional-changelog/tree/master/packages/conventional-changelog-angular)  
> [vben-admin-thin-next](https://github.com/anncwb/vben-admin-thin-next/blob/main/README.md)  
> [Git Commit Message 這樣寫會更好，替專案引入規範與範例](https://wadehuanglearning.blogspot.com/2019/05/commit-commit-commit-why-what-commit.html)

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
