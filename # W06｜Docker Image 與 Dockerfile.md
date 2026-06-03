**# W06｜Docker Image 與 Dockerfile**



**## 映像組成**

**- Layers 是什麼：Docker image is built from multiple layers, each instruction in a Dockerfile (RUN, COPY, etc.) creates a layer.**



**- Config 是什麼：Config contains runtime settings such as CMD, ENTRYPOINT, ENV, and WORKDIR. It defines how the container starts.**



**- Manifest 是什麼：Manifest is metadata that describes the image, including layers and config. Docker uses it to pull and assemble images.**



**## python:3.12-slim inspect 摘錄**

**- Config.Cmd：\["python3"]**

**- Config.Env：\[**

**"PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",**

**"LANG=C.UTF-8",**

**"GPG\_KEY=7169605F62C751356D054A26A821E680E5FA6305",**

**"PYTHON\_VERSION=3.12.13",**

**"PYTHON\_SHA256=c08bc65a81971c1dd5783182826503369466c7e67374d1646519adf05207b684"**

**]**

**- Config.WorkingDir：/**

**- RootFS.Layers 數量：4**



**## Layer 快取實驗**

**| 情境 | build 時間 |**

**|---|---|**

**| v1 首次 build | 13.606s |**

**| v1 改 app.py 後 rebuild |  \~cached (faster) |**

**| v2 首次 build | 57.560s |**

**| v2 改 app.py 後 rebuild |v2 is slower initially but faster on rebuild due to caching |**



**觀察（用自己的話寫）：為什麼 v2 的 rebuild 這麼快？**



**## CMD vs ENTRYPOINT 實驗**

**| 寫法 | `docker run <img>` 輸出 | `docker run <img> extra1 extra2` 輸出 |**

**|---|---|---|**

**| CMD shell form | Arguments received: 0 show\_args.py | Error: "hello" not found |**

**| CMD exec form | Arguments received: 0 show\_args.py | Error: "hello" not found |**

**| ENTRYPOINT + CMD | Arguments received: 0 show\_args.py | Arguments received: 0 show\_args.py / 1 hello / 2 world |**



**結論（用自己的話寫）：CMD SHELL form excetues through a shell and fail to handle arguments correctly.**

&#x09;	    **CMD EXEC form passes argument correctly but is still replaced depending on the usage.**

&#x09;	    **Entry Point ensure the command always run adn append to the arguments, and making it the best for fixing an applications.**



**## Multi-stage 大小對照**

**| Image | SIZE |**

**|---|---|**

**| python:3.12（builder base） | 179MB |**

**| python:3.12-slim（runtime base） | 179MB |**

**| myapp:v2（單階段） |  199MB |**

**| myapp:multi（多階段） |  199MB |**



**解釋（用自己的話寫）：builder stage 的 layer 去哪了？**



**Multi-stage builds reduce image size by removing build dependencies. In this case, size reduction is not significant because Python runtime and dependencies already dominate image size.**



**## .dockerignore 故障注入**

**| 項目 | 故障前 | 故障中 | 回復後 |**

**|---|---|---|---|**

**| du -sh . | 52K | 52K | 52K |**

**| build context | 129B | 129B | 129B |**

**| build time | \~44s | \~44s | \~44s |**



**## 排錯紀錄**

**- \*\*症狀\*\*: Dockerfile not found / image not found**

**- \*\*診斷\*\*: Incorrect working directory**

**- \*\*修正\*\*: Navigate to correct project folder**

**- \*\*驗證\*\*: Docker build and run succeeded**



**## 設計決策**

**（說明本週至少 1 個技術選擇與取捨，例如：為什麼 runtime 選 `python:3.12-slim` 而不是 `alpine`？）**

**I chose `python:3.12-slim` instead of alpine because:**



**- Better compatibility with Python packages**

**- Fewer compilation issues**

**- Good balance between size and stability**





**## Minimum Command Chain**



**```bash**

**cd \~/virt-container-labs/w06**



**docker build -f Dockerfile.v1 -t myapp:v1 .**

**docker build -f Dockerfile.v2 -t myapp:v2 .**

**docker build -f Dockerfile.multi -t myapp:multi .**



**docker run myapp:v1**

**docker run cmd-shell**

**docker run entrypoint**



