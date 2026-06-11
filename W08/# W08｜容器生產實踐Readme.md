# W08｜容器生產實踐

## Healthcheck 故障測試
- 停 db 後幾秒被標 unhealthy：大約 20~30 秒
- 對應的 log 訊息：docker compose stop  db docker compose ps

## Log 失控估算
- noisy 容器 30s log 大小：2 MB
- 預估 24h 大小：2 MB × 2880 ≈ 5.6 GB
- 套 rotation 後穩定上限：10 MB × 5 = 50 MB

## 資源限制實驗

| 實驗 | 命令 | 觀察結果 | 對應 cgroup 檔 | 值 |
|---|---|---|---|---|
| App resource limit | docker stats --no-stream | app 使用 25.39MiB / 256MiB，限制成功套用 | memory.max | 268435456 |
| DB resource limit | docker stats --no-stream | db 使用 19.91MiB / 512MiB，限制成功套用 | memory.max | 536870912 |
| CPU limit | docker stats --no-stream | app CPU limit 為 0.5 CPU，db CPU limit 為 1.0 CPU | cpu.max | app 約 50000 100000；db 約 100000 100000 |

## 權限四階對照
| 階梯 | id | CapEff | NoNewPrivs | curl /healthz |
|---|---|---|---|---|
| 0 | uid=0(root) | 00000000a80425fb | 0 | 200 |
| 1 | uid=1000(appuser) | 0000000000000000 | 0 | 200 |
| 2 | uid=1000(appuser) | 0000000000000000 | 0 | 200 |
| 3 | uid=1000(appuser) | 0000000000000000 | 0 | 200 |
| 4 | uid=1000(appuser) | 0000000000000000 | 1 | 200 |

## 排錯紀錄

| 症狀 | 診斷 | 修正 | 驗證 |
|---|---|---|---|
| `The "DB_USER" variable is not set` | 缺少 `.env` 檔案，Docker Compose 無法讀取資料庫環境變數 | 建立 `.env`，加入 `DB_USER=postgres`、`DB_PASSWORD=postgres123`、`DB_NAME=appdb` | `docker compose up -d` 後 db 與 app 成功啟動並變成 healthy |
| `mapping key "volumes" already defined` | `compose.yaml` 裡重複貼上 `volumes:` 區塊 | 刪除重複的 YAML 區塊，只保留一個 `volumes:` | `docker compose config` 成功通過 |
| `mapping values are not allowed in this context` | `user: "1000:1000"` 縮排錯誤，多了一個空格 | 將 `user:` 對齊 `build:`、`ports:` 等 app service 內的欄位 | `docker compose up -d --build app` 成功執行 |
| `unable to prepare context: path "/home/steffyn/app" not found` | 在錯誤目錄 `~` 執行 docker compose，導致 Compose 找不到 `./app` | 切回 `cd ~/virt-container-labs/w08` 再執行指令 | app 成功 rebuild，`curl /healthz` 回傳 `OK - DB connected` |

## 設計決策
（你選的 mem_limit / cpus 數值理由是什麼？read_only 之後你補了哪些 tmpfs，為什麼？）
I configured the app container with `mem_limit: 256m` and `cpus: "0.5"` because this Flask application is very lightweight and only provides two endpoints: `/` and `/healthz`. According to `docker stats`, the app uses approximately 25.39 MiB out of the available 256 MiB, so this limit is sufficient while also preventing the application from consuming excessive host resources.

For the database container, I configured `mem_limit: 512m` and `cpus: "1.0"` because PostgreSQL requires additional resources for database connections, query processing, and internal caching. The limit provides enough headroom while still preventing uncontrolled resource usage.

I enabled `read_only: true` to make the container root filesystem immutable. This improves security by preventing applications or attackers from modifying system files, installed Python packages, or other parts of the container image at runtime.

Because a read-only filesystem can break applications that need temporary writable storage, I added the following tmpfs mounts:

```yaml
tmpfs:
  - /tmp:size=32M
  - /home/appuser/.cache:size=16M
