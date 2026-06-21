import json
import time
import random
from pathlib import Path

def generate_sample_sessions(output_dir: str, num_sessions: int = 20):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    models = [
        "claude-3-5-sonnet-20241022",
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
    ]

    topics = [
        "Python 性能优化技巧",
        "React 组件设计模式",
        "数据库索引优化方案",
        "机器学习入门指南",
        "Docker 容器化部署",
        "算法与数据结构复习",
        "前端工程化实践",
        "微服务架构设计",
        "API 设计最佳实践",
        "代码质量与重构",
    ]

    now = time.time()

    for i in range(num_sessions):
        session_id = f"sample-session-{i+1}"
        topic = topics[i % len(topics)]
        model = random.choice(models)

        days_ago = random.randint(0, 30)
        hours_ago = random.randint(0, 23)
        created_at = now - (days_ago * 86400) - (hours_ago * 3600)
        updated_at = created_at + random.randint(60, 7200)

        num_messages = random.randint(4, 12)
        messages = []
        total_input_tokens = 0
        total_output_tokens = 0

        for j in range(num_messages):
            is_user = j % 2 == 0
            role = "user" if is_user else "assistant"

            if is_user:
                content = f"关于{topic}，我想了解更多相关知识。\n\n请问有什么好的学习资源或实践建议吗？"
                input_tokens = random.randint(100, 500)
                output_tokens = 0
            else:
                content = f"好的，关于{topic}，我来为您详细解答：\n\n1. 首先，理解核心概念非常重要\n2. 其次，多实践多练习才能真正掌握\n3. 最后，建议参考官方文档和优质教程\n\n希望这些建议对您有帮助！"
                input_tokens = 0
                output_tokens = random.randint(200, 2000)

            total_input_tokens += input_tokens
            total_output_tokens += output_tokens

            msg_created_at = created_at + (j * 120)

            messages.append({
                "id": f"{session_id}-msg-{j}",
                "role": role,
                "content": content,
                "model": model if not is_user else "",
                "created_at": msg_created_at,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "message_index": j,
            })

        session_data = {
            "id": session_id,
            "title": f"{topic} - 第{i+1}次对话",
            "created_at": created_at,
            "updated_at": updated_at,
            "model": model,
            "total_tokens": total_input_tokens + total_output_tokens,
            "input_tokens": total_input_tokens,
            "output_tokens": total_output_tokens,
            "message_count": len(messages),
            "messages": messages,
        }

        file_path = output_path / f"{session_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)

        print(f"Generated: {file_path.name}")

    print(f"\n共生成 {num_sessions} 个示例会话文件")
    print(f"输出目录: {output_path.resolve()}")


if __name__ == "__main__":
    import sys
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "data/sessions"
    num = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    generate_sample_sessions(output_dir, num)
