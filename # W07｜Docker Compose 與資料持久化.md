# W07｜Docker Compose 與資料持久化

## 拓樸圖
（mermaid 或 ASCII，標出 app、db、default network、db-data volume）

## 從 docker run 到 compose.yaml
In the past, using docker run required many manual steps:

Create app container
Create database container
Set up network manually
Set up volume manually
Make sure app and database can connect properly

With Docker Compose:
One compose.yaml file can start the entire system at once.

The biggest improvement is I don’t need to type multiple docker run commands anymore.

## 三種掛載對照
| 掛載類型 | 路徑（host） | 容器砍重起資料還在嗎 | 重啟容器資料狀態 | 適合情境 |
|---|---|---|---|---|
| named volume | /var/lib/docker/volumes/ | yes |persistent  | Databases, production data |
| bind mount | /home/user/project  | yes | live sync | Development , code editing |
| tmpfs | memory (ram) | no  | Lost | Cache, temporary data |

## healthcheck 前後對照
| 寫法 | curl /healthz t=1s | t=3s | t=5s | t=10s |
|---|---|---|---|---|
| 只 depends_on | fail | fail | unstable or fail | ok  |
| service_healthy | waiting  | waiting | starting  | stabe ok  |

觀察（自己的話）：

## 排錯紀錄
- 症狀：/healthz returned database connection error or the db container exited unexpectedly.
- 診斷：The .env file was missing or not created, so database environment variables (DB_USER, DB_PASSWORD, DB_NAME) were empty.
- 修正：Created the .env file using cp .env.example .env to provide required environment variables.
- 驗證：Ran curl http://localhost:8080/healthz and received OK - DB connected.

## 設計決策
（為什麼 db 用 named volume 而不是 bind mount？為什麼不能在生產用 tmpfs 存資料庫？）
Because database data should be managed safely by Docker. Named volumes are more stable, less likely to be accidentally modified or deleted, and better suited for production databases.

Because tmpfs stores data in memory (RAM). If the container or system restarts, all data is lost. Databases require persistent storage, so tmpfs is only suitable for temporary or cache data, not production use.

cd ~/virt-container-labs/w07

cp .env.example .env

docker compose up -d

sleep 10

curl http://localhost:8080/healthz
