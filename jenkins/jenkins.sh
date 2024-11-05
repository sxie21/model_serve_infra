# 运行 Apache Benchmark
RESULT=$(ab -n 1000 -c 10 -H "Authorization: Bearer <your_token>" -p data.json http://localhost:8000/predictions/model1)

# 提取 QPS 和 P90 时间（假设我们用正则提取相关值）
QPS=$(echo "$RESULT" | grep "Requests per second" | awk '{print $4}')
P90=$(echo "$RESULT" | grep "Time per request" | awk '{print $4}')

# 设置性能目标
TARGET_QPS=100
TARGET_P90=200

# 检查是否满足目标
if [ $(echo "$QPS < $TARGET_QPS" | bc) -eq 1 ]; then
  echo "QPS is below the target: $QPS"
  exit 1
fi

if [ $(echo "$P90 > $TARGET_P90" | bc) -eq 1 ]; then
  echo "P90 is above the target: $P90"
  exit 1
fi

echo "Performance test passed"
