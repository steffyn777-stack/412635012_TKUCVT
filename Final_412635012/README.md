 期末實作 — <412635012> <劉管亮>

## 1. 架構總覽
<Mermaid 圖 + 一段話說明>

## 2. Part A：底座與基準點
<ssh 證據 + 版本 + snapshot>
Host bastion
    HostName 192.168.56.104
    User steffyn

Host app
    HostName 192.168.56.105
    User steffyn
    ProxyJump bastion

## 3. Part B：Dockerfile 與快取
<Dockerfile + 兩次 build 對照>

### 為什麼聽 8080 不聽 80？
本版本容器會建立非 root 使用者 appuser，並透過 USER appuser 切換成非 root 身分執行。依照 Linux 權限模型，1024 以下的 port 屬於 privileged port，非 root 使用者不能直接綁定 80。因此本服務改聽 8080，避免額外給予 CAP_NET_BIND_SERVICE，符合最小權限原則。

## 4. Part C：Compose 與資料持久化
<compose.yaml 重點 + 三段對照>

三段對照

|階段	|	指令	|	SELECT * FROM exam 結果|
|砍容器重建|	docker compose down && docker compose up -d	|	資料仍存在|
|連 volume 一起砍|docker compose down -v && docker compose up -d|	資料消失|
|重寫|	再 INSERT 一次|資料重新出現|

### down vs down -v
docker compose down 只會刪除 container 與 network，不會刪除 named volume，因此 PostgreSQL 的資料仍保留在 db-data 中。

docker compose down -v 則會連同 Compose 管理的 named volume 一起刪除，因此資料庫資料會消失。

Named volume 的生命週期由 Docker 管理，但是否刪除取決於使用者執行的 Compose 指令；一般 down 不刪除 volume，down -v 才會刪除。

## 5. Part D：生產化加固
<權限驗證輸出 + cgroup 讀值對照表>
### yaml 的值怎麼對回 cgroup 檔案？
In compose.yaml, I wrote:

mem_limit: 256m
cpus: "0.5"
pids_limit: 200

The cgroup value memory.max shows 268435456 because 256 MiB = 256 × 1024 × 1024 = 268435456 bytes.

The cgroup value cpu.max shows 50000 100000. In cgroup v2, cpu.max uses the format "quota period". This means the container can use 50000 microseconds of CPU time in every 100000 microseconds period, which equals 50% CPU, the same as cpus: "0.5".

The cgroup value pids.max shows 200, which directly matches pids_limit: 200 in compose.yaml.


## 6. Part E：故障演練
### 故障 1：<F1–F4 擇一> F1
- 注入方式：docker compose stop db
- 故障前：app 與 db 均為 Up 且 healthy，執行 curl http://localhost:8080/healthz 回傳 200。
- 故障中：停止 db 後，app 容器仍然維持 Up 狀態，但因無法連線資料庫而導致 healthcheck 失敗。約 30 秒後，docker compose ps 顯示 app 狀態為 (unhealthy)，curl http://localhost:8080/healthz 回傳 HTTP 503。
- 回復後：docker compose start db
 等待資料庫恢復後，app healthcheck 再次成功，狀態恢復為 (healthy)，/healthz 回傳 200。
- 診斷推論：此故障顯示 unhealthy 不代表容器已死亡。App 容器仍在執行，但因為依賴的資料庫服務不可用，所以健康檢查失敗。

### 故障 2：<另一個> F2
- 注入方式：docker compose stop app
- 故障前：app 與 db 正常運作，執行 curl http://localhost:8080/ 可以取得學號與資料庫時間。
- 故障中：停止 app 容器後，Host 端已無服務監聽 8080 Port。執行 curl http://localhost:8080/ 出現 connection refused。
- 回復後：docker compose start app
等待容器啟動完成後，curl http://localhost:8080/ 再次取得正常回應。
- 診斷推論：此故障屬於容器層故障。因為 App Container 已停止，因此 TCP 連線無法建立，直接出現 connection refused。

### 三症狀分層表（必答）
| 症狀 | 最可能的層 | 第一條驗證命令 |
| ---- | ---------- | -------------- |
| timeout | 網路層（Network） | ping 192.168.56.105 |
| connection refused | 容器／服務層（Container / Service） | docker compose ps |
| HTTP 503 | 應用程式層（Application）  | curl http://localhost:8080/healthz |

## 7. 反思（200 字）
這學期從 VM 做到 production-ready 容器，「隔離」這個概念在 VM、namespace、
cgroup、權限階梯四個地方各出現一次——它們在防的東西一樣嗎？

This semester, I learned that isolation is used in different ways in VMs, namespaces, cgroups, and permissions. Even though they all provide protection, they do not protect the same thing.

A VM provides isolation by running a separate operating system. If one VM has a problem, it usually will not affect another VM. This makes VMs very secure but they use more resources.

Namespaces are used in containers. They make each container think it has its own processes, network, and files. This helps containers run independently even when sharing the same Linux kernel.

Cgroups are used to control resources. For example, they can limit how much CPU and memory a container can use. This prevents one container from using all system resources and affecting other services.

Permissions provide another layer of protection. Running applications as a non-root user and removing unnecessary privileges reduces security risks if the application is attacked.

In conclusion, these four types of isolation have different purposes. VMs isolate operating systems, namespaces isolate environments, cgroups isolate resources, and permissions isolate privileges. By working together, they make containerized applications more secure and stable.

## 8. Bonus（選做）
