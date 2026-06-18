# auto_checkin.py (Enhanced Version with Smart Token Management and Deduplication)
import os
import requests
import json
import base64
from datetime import datetime, timedelta
from get_token import get_wjkc_token
from update_github_secret import update_github_repo_secret

# --- API Endpoints ---
CHECKIN_URL = "https://wj-kc.com/api/user/sign_use"
USER_INFO_URL = "https://wj-kc.com/api/user/userinfo"

# --- Smart Token Management ---`
def check_token_needs_update():
    """检查token是否需要更新（15天周期）"""
    last_update = os.getenv('TOKEN_LAST_UPDATE')
    if not last_update:
        print("未找到TOKEN_LAST_UPDATE，需要更新token")
        return True

    try:
        last_update_date = datetime.fromisoformat(last_update)
        days_since_update = (datetime.now() - last_update_date).days
        print(f"距离上次token更新已过去 {days_since_update} 天")
        return days_since_update >= 15
    except ValueError:
        print("TOKEN_LAST_UPDATE格式无效，需要更新token")
        return True

def should_send_notification():
    """检查今日是否需要发送通知（去重机制）"""
    last_notification = os.getenv('LAST_NOTIFICATION_DATE')
    today = datetime.now().strftime('%Y-%m-%d')

    if last_notification == today:
        print(f"今日({today})已发送过通知，跳过")
        return False

    print(f"今日({today})尚未发送通知，将发送")
    return True

def set_github_output(name, value):
    """设置GitHub Actions输出变量"""
    github_output = os.getenv('GITHUB_OUTPUT')
    if github_output:
        with open(github_output, 'a', encoding='utf-8') as f:
            f.write(f"{name}={value}\n")
    print(f"设置输出变量: {name}={value}")

# --- 主函数 (处理单个Token) ---
def run_checkin_for_token(token_name, wjkc_token):
    print(f"--- 正在处理账户: {token_name} ---")
    session = requests.Session()
    session.cookies.update({"token": wjkc_token.strip()}) # 使用 .strip() 清除可能存在的空格
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'})
    
    try:
        # Step 1: Check-in
        checkin_response = session.post(CHECKIN_URL, json={"data": "e30="})
        checkin_response.raise_for_status()
        checkin_result = json.loads(base64.b64decode(checkin_response.json().get('data')))
        
        message = checkin_result.get('msg', 'N/A')
        if message == "SUCCESS":
            reward_mb = checkin_result.get('data', {}).get('addTraffic', 0) / (1024*1024)
            status_text = f"✅ 签到成功！获得 {reward_mb:.2f}MB"
            status_emoji = "✅"
        else:
            status_text = f"🟡 无需签到 (已签到)"
            status_emoji = "🟡"
        print(f"  > 签到状态: {status_text}")

        # Step 2: Get User Info
        userinfo_response = session.post(USER_INFO_URL, json={"data": "e30="})
        userinfo_result = json.loads(base64.b64decode(userinfo_response.json().get('data')))
        if userinfo_result.get('msg') != 'SUCCESS': raise ValueError("Token无效或已过期，无法查询信息。")

        email = userinfo_result.get('data', {}).get('email', token_name)
        traffic_gb = userinfo_result.get('data', {}).get('traffic', 0) / (1024*1024*1024)

        # 返回格式化的结果，包含更多信息
        return {
            'email': email,
            'status': status_text,
            'status_emoji': status_emoji,
            'traffic_gb': traffic_gb,
            'reward_mb': reward_mb if message == "SUCCESS" else 0,
            'success': True
        }

    except Exception as e:
        print(f"  > 发生错误: {e}")
        return {
            'email': token_name,
            'status': f"❌ 任务失败: {str(e)}",
            'status_emoji': "❌",
            'traffic_gb': 0,
            'reward_mb': 0,
            'success': False,
            'error': str(e)
        }

# --- 脚本入口 ---
def load_tokens_from_env():
    tokens_str = os.getenv('WJKC_TOKENS')
    if tokens_str:
        # 过滤掉因为额外逗号等产生的空字符串
        return {f"Token_{i+1}": token.strip() for i, token in enumerate(tokens_str.split(',')) if token.strip()}
    return {}

def main():
    print("=== WJKC 自动签到系统 v2.0 启动 ===")
    execution_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')

    github_repo = os.getenv('GITHUB_REPOSITORY')
    github_token = os.getenv('GH_TOKEN')

    # 检查是否需要发送通知（去重机制）
    should_notify = should_send_notification()
    set_github_output('should_notify', 'true' if should_notify else 'false')
    set_github_output('execution_time', execution_time)

    # 智能Token管理：检查是否需要更新token
    need_token_update = check_token_needs_update()
    accounts_to_update = {}

    if need_token_update:
        print("🔄 Token需要更新，尝试通过登录获取新token...")
        credentials_str = os.getenv('WJKC_CREDENTIALS')

        if credentials_str and github_repo and github_token:
            try:
                credentials = json.loads(credentials_str)
                print(f"找到 {len(credentials)} 个账户凭据")

                for i, cred in enumerate(credentials):
                    account_name = cred.get('name', f"Account_{i+1}")
                    username = cred.get('username')
                    password = cred.get('password')

                    if username and password:
                        new_token = get_wjkc_token(account_name, username, password)
                        if new_token:
                            accounts_to_update[account_name] = new_token
                            print(f"✅ 成功获取账户 '{account_name}' 的新token")
                        else:
                            print(f"❌ 未能获取账户 '{account_name}' 的新token")
                    else:
                        print(f"⚠️ 账户 '{account_name}' 缺少凭据，跳过")

                if accounts_to_update:
                    # 更新WJKC_TOKENS
                    updated_tokens_str = ",".join(accounts_to_update.values())
                    update_success = update_github_repo_secret(
                        github_repo, "WJKC_TOKENS", updated_tokens_str, github_token
                    )

                    if update_success:
                        # 更新token更新时间
                        current_time = datetime.now().isoformat()
                        update_github_repo_secret(
                            github_repo, "TOKEN_LAST_UPDATE", current_time, github_token
                        )
                        print("✅ Token和更新时间已成功更新到GitHub Secrets")
                    else:
                        print("❌ Token更新失败")

            except json.JSONDecodeError:
                print("❌ WJKC_CREDENTIALS 格式错误")
            except Exception as e:
                print(f"❌ 处理凭据时发生错误: {e}")
        else:
            print("⚠️ 缺少必要的环境变量，跳过token更新")
    else:
        print("✅ Token仍在有效期内，无需更新")

    # 加载现有的token并执行签到
    all_tokens = load_tokens_from_env()

    # 如果有新获取的token，优先使用
    for name, new_token in accounts_to_update.items():
        all_tokens[name] = new_token

    if not all_tokens:
        error_msg = "❌ 未找到任何可用的token"
        print(error_msg)
        set_github_output('result', error_msg)
        return

    print(f"🚀 开始为 {len(all_tokens)} 个账户执行签到任务...")
    results = []
    success_count = 0
    total_reward = 0

    for name, token in all_tokens.items():
        print(f"\n--- 处理账户: {name} ---")
        result = run_checkin_for_token(name, token)
        results.append(result)

        if result['success']:
            success_count += 1
            total_reward += result['reward_mb']

    # 格式化通知消息
    notification_lines = []
    notification_lines.append(f"📊 **签到统计**: {success_count}/{len(all_tokens)} 成功")
    notification_lines.append(f"🎁 **总奖励**: {total_reward:.2f}MB")
    notification_lines.append("")

    for result in results:
        notification_lines.append(f"{result['status_emoji']} **{result['email']}**")
        notification_lines.append(f"   状态: {result['status']}")
        notification_lines.append(f"   流量: {result['traffic_gb']:.2f}GB")
        if result['reward_mb'] > 0:
            notification_lines.append(f"   奖励: +{result['reward_mb']:.2f}MB")
        notification_lines.append("")

    notification_message = "\n".join(notification_lines)
    set_github_output('result', notification_message)

    # 更新通知日期（如果需要发送通知）
    if should_notify and github_repo and github_token:
        today = datetime.now().strftime('%Y-%m-%d')
        update_github_repo_secret(github_repo, "LAST_NOTIFICATION_DATE", today, github_token)
        print(f"✅ 已更新通知日期: {today}")

    print("\n=== 所有任务已完成 ===")

if __name__ == "__main__":
    main()
