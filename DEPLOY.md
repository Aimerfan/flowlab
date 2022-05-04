# DEPLOY

---

## Pyhon 手動編譯安裝

**請確認 Python 版本有在 3.8.10 以上**

- 如果 Python 版本不滿足，安裝請參考[文章](https://blog.csdn.net/xietansheng/article/details/84791703)
- 編譯時需要的依賴[參考](https://devguide.python.org/setup/#linux)

---

## 啟動並設定 DevOps 自動化工具

1. git clone flowlab GitHub
    - clone 專案, 並切換到需要部屬的分支上
2. 修改設定檔
    - 將 `./env.example` 複製並更名為 `.env`, 修改內容
    - 將 `./flowlab/secrets.example` 複製並更名為 `secrets.py`, 修改內容
3. 輸入 `./tools/init.sh` 以修改虛擬記憶體大小
4. 啟動部分服務 (資料庫, gitlab, jenkins)
    - 執行 `docker-compose up -d db gitlab jenkins`
5. 使用 pgAdmin 建立一個名為 sonar 的 database
6. 啟動 sonarqube 服務
    - 執行 `docker-compose up -d sonarqube`

### 設定 jenkins

1. 開啟 jenkins 網頁
2. 進入 jenkins 容器 `docker-compose exec jenkins bash`
3. 輸入 `cat /var/jenkins_home/secrets/initialAdminPassword`
   取得字串後, 填入網頁中, 以解鎖 Jenkins
4. 點選左邊的 Install suggested plugins, 安裝建議的插件
5. 根據 `.env` 建立 Admin 帳號
6. 下載 plugins
    - 管理 Jenkins > 管理外掛程式 >
    - 查詢並安裝以下套件:
      - JUnit Plugin (原則上預設會有)
      - GitLab
      - GitLab API
      - JaCoCo
      - Docker Plugin
7. 設定專案型矩陣授權策略, 以便學生只能檢視自己的專案工作 (作業)
    - 管理 Jenkins > 設定全域安全性 > 授權 > 專案型矩陣授權策略
    - 已驗證使用者 (Auth. Users) 僅勾選 整體: Read
    - 建立專案時, 所套用的 xml 檔案, 會將學生設定成 作業: Read, 讓學生能夠查看自己的作業
8. 建立節點
    - 管理 Jenkins > 管理節點 > Configure Clouds
    - 依據以下說明進行填寫 (以下未說明到 的表示不更動預設值)
      - Name: `docker`
      - 點開 Docker Cloud details...
        - Docker Host URL: `unix://var/run/docker.sock`
        - 勾選 `Enabled`
        - Container Cap: `2`
      - 點開 Docker Agent templates...
        - Labels: `inbound`
        - 勾選 `Enabled`
        - Name: `inbound`
        - Docker Image: `jenkins/inbound-agent:4.9-1`
9. 建立 API token
    - (右上角) Admin 帳號 > 設定 > API token > Add new Token
    - 複製 token 到 `.env` 的 `JENKINS_API_TOKEN`
10. 建立 global credentials (for gitlab and sonarqube)
    - 管理 Jenkins > manage credentials > Stores scoped to Jenkins 的 (global) > Add Credentials
    - 建立 GitLab API token, ID 為 `gitlab_token`, API token 為 gitlab 的 access token (待設定完 gitlab)
    - 建立 Secret text, ID 為 `sonarqube_token`, Secret 為 sonarqube 的 access token (待設定完 sonarqube)

### 設定 gitlab

1. 開啟 gitlab 網頁
2. 建立 Personal Access Tokens
   - (右上角) 頭貼 > Edit profile > (左邊) Access Token
   - Token name 不限制
   - Select scopes 全勾選
   - 點選 Create personal access token
3. 複製 token 到 `.env` 的 `GITLAB_ROOT_PRIVATE_TOKEN`
4. 至 jenkins 新增 Credentials (Kind 為 GitLab API token)

### 設定 sonarqube

1. 開啟 sonarqube 網頁 (預設帳密皆為 `admin`)
2. 根據 `.env` 的內容修改密碼
3. 新增 Tokens
   - (右上角) 頭貼 > My Account > Security > Generate Token
   - Token name 不限制
   - 點選 Generate
4. 複製 token 到 `.env` 的 `SONARQUBE_SHARED_TOKEN`
5. 至 jenkins 新增 Credentials (Kind 為 Secret text)

**由於修改 `.env`, 因此需要重新啟動 docker: `docker-compose restart`**

---

## 安裝需求套件、建立資料表與管理員

1. 建立虛擬環境 (若已有虛擬環境, 請跳過這步驟) `python3 -venv <venv>`
2. 進入虛擬環境 `. <venv>/bin/activate`
3. 安裝 python 所需套件 `pip install -r requirements.txt`
4. 建立資料表 `python3 manage.py migrate`
5. 收集靜態資源 `python3 manage.py collectstatic --clear`
   - `--clear` 會先刪除在重新收集, 確保最新
   - 若遇到 `permission denied`, 執行 `chmod -R 777 logs/
6. 建立一個管理員帳號
   - `python3 manage.py createsuperuser`
   - 依序輸入 username, email, password

---

## 設定 gunicorn 為系統服務 (daemon)

由於我們是在虛擬環境中安裝 gunicorn, 因此**以下操作請全程在虛擬環境中執行**

1. 建立 `gunicorn.socket`
    - `sudo vim /etc/systemd/system/gunicorn.socket`
      ```
      [Unit]
      Description=gunicorn socket
   
      [Socket]
      ListenStream=/run/gunicorn.sock
      # Our service won't need permissions for the socket, since it
      # inherits the file descriptor by socket activation
      # only the nginx daemon will need access to the socket
      SocketUser=www-data
      # Optionally restrict the socket permissions even more.
      # SocketMode=600
   
      [Install]
      WantedBy=sockets.target
      ```
2. 確認 gunicorn 路徑: `which gunicorn`, 記住等下有用
3. 建立 `gunicorn.service`
    - `sudo vim /etc/systemd/system/gunicorn.service`
    - `<project_root>` 輸入 Django 專案的路徑
    - `<gunicorn_path` 輸入 gunicorn 的路徑, 使用 `which gunicorn` 獲得
      ```
      [Unit]
      Description=gunicorn daemon
      Requires=gunicorn.socket
      After=network.target
   
      [Service]
      User=www-data
      Group=www-data
      WorkingDirectory=<project_root>
      ExecStart=<gunicorn_path> \
                --access-logfile - \
                --workers 3 \
                --bind unix:/run/gunicorn.sock \
                <project_name>.wsgi:application
    
      [Install]
      WantedBy=multi-user.target
      ```
4. 啟動 gunicorn.sock
   ```
   sudo systemctl start gunicorn.socket
   sudo systemctl enable gunicorn.socket
   ```
   或者
   `sudo systemctl enable --now gunicorn.socket`
5. 設定允許 gunicorn 操作日誌目錄與檔案
   `sudo chomod -R 777 logs`
6. 確認 gunicorn.sock 有正常運作
    - `sudo systemctl status gunicorn.socket`
    - 如果結果不是綠色 (正常運作)，使用以下指令檢查
      - `sudo journalctl -u gunicorn.socket`
7. 測試 gunicorn
    - `curl --unix-socket /run/gunicorn.sock localhost`
    - 如果結果不是綠色 (正常運作)，使用以下指令檢查
      - `sudo journalctl -u gunicorn`
      - 問題排除後要重新啟動 gunicorn
        ```
        sudo systemctl daemon-reload    # 重新讀取設定，有變更設定(gunicorn.sock, gunicorn.service)必須要下
        sudo systemctl restart gunicorn # 重新啟動
        ```

至此，gunicorn 應該可以正常運作，但是監聽位置是使用本機套接字，還沒有辦法從外部連入，因次接下來要設定 nginx 來轉發外部的 requests

---

## 安裝 nginx 提供靜態資源

1. 安裝 nginx
    - `sudo apt update`
    - `sudo apt install nginx`
2. 設定 nginx 轉發
    - 建立網站設定檔
      - `sudo vim /etc/nginx/sites-available/<project_name>.conf`
        ```
        server {
            listen 8000;                           # 網站 port number，看需求變更
            server_name <domain_name> <server_ip>; # 網域名及ip，以空格隔開。
   
            location /static/ {
                root <static_root_path>;           # static 根目錄的位置(不包含 static 本身)
            }
   
            location / {
                include proxy_params;
                proxy_pass http://unix:/run/gunicorn.sock;
            }
        }
        ```
      - **`static_root_path` 路徑下不要包含 static 目錄本身**
    - 啟動網站
      ```
      sudo ln -s /etc/nginx/sites-available/<project_name>.conf /etc/nginx/sites-enabled
      sudo nginx -t   # 測試設定檔是否正確，如果正常這邊都只有綠字，黃字紅字都有問題
      sudo systemctl restart nginx
      ```
    - 設定防火牆
      - `sudo ufw allow 8000`
    - 成功! 可以連到 `http://domain_name:8000` 去看看了

---

## FlowLab 基本設定

1. 使用管理員帳號在後台... (`http://domain_name:8000/admin`)
   1. 建立一個使用者, 並設定為 teacher
   2. 建立 學期
   3. 建立 課程
2. **手動** 替該使用者 (teacher) 建立一個 gitlab, jenkins, sonarqube 帳號
   - gitlab: menu > admin > new user
   - jenkins: 管理 Jenkins > 管理使用者 > 建立使用者
   - sonarqube: (右上角) 頭貼 > Security > users > create user
3. 讓老師能夠檢視所有人的專案
   - 管理 Jenkins > 設定全域安全性 > 授權 > 專案型矩陣授權策略
   - Add user... > 填寫老師的 username, 並勾選 整體: Read; 作業: Read;
4. 使用 teacher 帳號在前端...
   1. 建立學生帳號
      - 進入課程 > 新增學生
   2. 建立專案並匯出成模板 (for 課程需求)
      - 若遇到 `permission denied: '~/flowlab/uploads'` 這類問題時
        - 建立一個 uploads 資料夾, 並修改權限, 重啟伺服器
          ```
          mkdir uploads
          chmod -R 777 uploads
          sudo systemctl restart gunicorn
          ```
   3. 在課程裡新增實驗, 評量題目等等...

---

## 其他
- 僅修改程式碼, 須更新網頁伺服器
  - 重新啟動 gunicorn `sudo systemctl restart gunicorn`
- 修改到靜態資源 (.png, .js ...), 須更新網頁伺服器
  - 進入虛擬環境 `. <venv>/bin/activate`
  - 收集靜態資源 `python3 manage.py collectstatic --clear`
  - 重新啟動 nginx `sudo systemctl restart nginx`
- 網頁有誤 (ex: 500...)
  - 查看 gunicorn logs `sudo journalctl -eu gunicorn`
