## run_job.sh
```sh
#!/usr/bin/env bash
# run_job.sh  <jar路径>  [可选参数...]
set -euo pipefail

JAR="$1"
shift          # 其余参数作为作业参数

# 1) 发送作业到集群，并把 JOB_ID 提出来
JOB_JSON=$(./bin/flink run -d "$@" "$JAR" 2>&1 | tee /tmp/run_job.log)

# 2) 抓取 JobID（正则匹配）
JOB_ID=$(echo "$JOB_JSON" | grep -oP '(?<=Job has been submitted with JobID )\K[A-Fa-f0-9]+')

echo "JobID = $JOB_ID"
echo "$JOB_ID" > job_id.tmp          # 保存到文件

```

## cancel_job.sh
```sh
#!/usr/bin/env bash
# cancel_job.sh
set -euo pipefail

JOB_ID_FILE="job_id.tmp"

if [[ ! -f "$JOB_ID_FILE" ]]; then
    echo "❌ 文件 $JOB_ID_FILE 不存在，请先运行 run_job.sh"
    exit 1
fi

JOB_ID=$(cat "$JOB_ID_FILE")
echo "取消任务: $JOB_ID"

if bin/flink cancel "$JOB_ID"; then
    rm -f "$JOB_ID_FILE"
    echo "已删除 $JOB_ID_FILE"
else
    echo "取消失败，文件保留以便人工处理"
fi

```

## 执行
```sh
sh -v run_job.sh examples/flink-demo.jar -c com.flink.job.ToDoris

sh cancel_job.sh
```