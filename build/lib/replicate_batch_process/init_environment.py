#!/usr/bin/env python3
"""
Replicate 模型调用工具 - 环境初始化脚本

检查并设置必要的环境变量和API密钥
"""

import os
import sys
import getpass
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.absolute()
ENV_FILE = PROJECT_ROOT / '.env'

# 必需的环境变量
REQUIRED_ENV_VARS = {
    'REPLICATE_API_TOKEN': {
        'description': 'Replicate API Token',
        'help': '请访问 https://replicate.com/account/api-tokens 获取你的API token',
        'example': 'r8_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    }
}

def print_banner():
    """打印欢迎横幅"""
    print("=" * 60)
    print("🚀 Replicate 模型调用工具 - 环境初始化")
    print("=" * 60)
    print()

def check_env_file():
    """检查.env文件是否存在"""
    if ENV_FILE.exists():
        print(f"✅ 找到 .env 文件: {ENV_FILE}")
        return True
    else:
        print(f"⚠️  .env 文件不存在: {ENV_FILE}")
        return False

def load_existing_env():
    """加载现有的.env文件"""
    env_vars = {}
    
    if ENV_FILE.exists():
        try:
            with open(ENV_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        env_vars[key] = value
        except Exception as e:
            print(f"⚠️  读取 .env 文件时出错: {e}")
    
    return env_vars

def check_api_keys():
    """检查API密钥"""
    print("\n📋 检查API密钥状态:")
    print("-" * 40)
    
    # 加载现有环境变量
    existing_env = load_existing_env()
    
    # 同时检查系统环境变量和.env文件
    missing_keys = []
    
    for key, info in REQUIRED_ENV_VARS.items():
        # 检查系统环境变量
        sys_value = os.getenv(key)
        # 检查.env文件
        env_value = existing_env.get(key)
        
        if sys_value:
            print(f"✅ {key}: 在系统环境变量中找到")
        elif env_value:
            print(f"✅ {key}: 在.env文件中找到")
        else:
            print(f"❌ {key}: 未找到")
            missing_keys.append(key)
    
    return missing_keys, existing_env

def prompt_for_api_key(key, info):
    """提示用户输入API密钥"""
    print(f"\n🔑 请输入 {info['description']}:")
    print(f"   📖 说明: {info['help']}")
    print(f"   📝 格式示例: {info['example']}")
    print()
    
    # 使用getpass隐藏输入（对于敏感信息）
    if 'token' in key.lower() or 'key' in key.lower():
        value = getpass.getpass(f"请输入 {key}: ").strip()
    else:
        value = input(f"请输入 {key}: ").strip()
    
    if not value:
        print(f"⚠️  {key} 不能为空")
        return None
    
    return value

def validate_api_key(key, value):
    """简单验证API密钥格式"""
    if key == 'REPLICATE_API_TOKEN':
        if not value.startswith('r8_') or len(value) < 40:
            print(f"⚠️  警告: {key} 格式可能不正确")
            print("   Replicate API token 通常以 'r8_' 开头且长度较长")
            return False
    
    return True

def save_to_env_file(env_vars):
    """保存环境变量到.env文件"""
    print(f"\n💾 保存配置到 {ENV_FILE}")
    
    try:
        # 创建.env文件内容
        content = [
            "# Replicate 模型调用工具 - 环境变量配置",
            "# 此文件包含敏感信息，请勿提交到版本控制系统",
            "",
        ]
        
        for key, value in env_vars.items():
            if key in REQUIRED_ENV_VARS:
                content.append(f"# {REQUIRED_ENV_VARS[key]['description']}")
            content.append(f"{key}={value}")
            content.append("")
        
        # 写入文件
        with open(ENV_FILE, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content))
        
        print(f"✅ 配置已保存到 {ENV_FILE}")
        
        # 设置文件权限（仅所有者可读写）
        if os.name != 'nt':  # 非Windows系统
            os.chmod(ENV_FILE, 0o600)
            print("🔒 已设置.env文件权限为仅所有者可读写")
        
        return True
        
    except Exception as e:
        print(f"❌ 保存 .env 文件时出错: {e}")
        return False

def create_gitignore():
    """创建或更新.gitignore文件"""
    gitignore_path = PROJECT_ROOT / '.gitignore'
    
    # 要添加到.gitignore的内容
    ignore_patterns = [
        ".env",
        "*.env",
        "__pycache__/",
        "*.pyc",
        "*.pyo",
        "*.pyd",
        ".Python",
        "output/",
        "*.jpg",
        "*.png",
        "*.webp",
        "*.mp4",
        ".DS_Store",
        "Thumbs.db"
    ]
    
    existing_patterns = set()
    
    # 读取现有的.gitignore
    if gitignore_path.exists():
        try:
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                existing_patterns = {line.strip() for line in f if line.strip() and not line.startswith('#')}
        except Exception:
            pass
    
    # 检查需要添加的新规则
    new_patterns = []
    for pattern in ignore_patterns:
        if pattern not in existing_patterns:
            new_patterns.append(pattern)
    
    if new_patterns:
        try:
            with open(gitignore_path, 'a', encoding='utf-8') as f:
                if gitignore_path.stat().st_size > 0:
                    f.write('\n')
                f.write('# Replicate 模型调用工具\n')
                for pattern in new_patterns:
                    f.write(f'{pattern}\n')
            
            print(f"✅ 已更新 .gitignore 文件")
            print(f"   添加了 {len(new_patterns)} 个新的忽略规则")
            
        except Exception as e:
            print(f"⚠️  更新 .gitignore 时出错: {e}")

def test_api_connection():
    """测试API连接"""
    print("\n🔍 测试API连接...")
    
    try:
        import requests
        
        # 检查Replicate API
        replicate_token = os.getenv('REPLICATE_API_TOKEN')
        if replicate_token:
            headers = {'Authorization': f'Token {replicate_token}'}
            response = requests.get('https://api.replicate.com/v1/models', 
                                  headers=headers, timeout=10)
            
            if response.status_code == 200:
                print("✅ Replicate API 连接成功")
            elif response.status_code == 401:
                print("❌ Replicate API Token 无效")
                return False
            else:
                print(f"⚠️  Replicate API 响应异常: {response.status_code}")
        
        return True
        
    except ImportError:
        print("⚠️  未安装 requests 库，跳过连接测试")
        print("   可运行: pip install requests")
        return True
        
    except Exception as e:
        print(f"⚠️  测试API连接时出错: {e}")
        return True  # 不阻止继续

def create_output_directory():
    """创建输出目录"""
    output_dir = PROJECT_ROOT / 'output'
    output_dir.mkdir(exist_ok=True)
    print(f"✅ 创建输出目录: {output_dir}")

def print_next_steps():
    """打印后续步骤"""
    print("\n" + "=" * 60)
    print("🎉 环境初始化完成！")
    print("=" * 60)
    print("\n📋 后续步骤:")
    print("1. 运行示例: python example_usage.py")
    print("2. 或导入使用: from main import replicate_model_calling")
    print("3. 查看文档: README.md")
    print()
    print("💡 提示:")
    print("- 输出文件将保存在 output/ 目录中")
    print("- .env 文件已被添加到 .gitignore，不会被提交到版本控制")
    print("- 如需修改API密钥，可直接编辑 .env 文件")
    print()

def main():
    """主函数"""
    print_banner()
    
    # 检查.env文件
    env_exists = check_env_file()
    
    # 检查API密钥
    missing_keys, existing_env = check_api_keys()
    
    if not missing_keys:
        print("\n✅ 所有必需的API密钥都已配置")
        
        # 仍然执行其他初始化步骤
        create_gitignore()
        create_output_directory()
        
        if not env_exists and existing_env:
            # 如果.env文件不存在但环境变量在系统中，询问是否创建.env文件
            create_env = input("\n是否要创建 .env 文件以便本地使用？(y/n): ").strip().lower()
            if create_env in ['y', 'yes', '是']:
                # 从系统环境变量创建.env
                env_to_save = {}
                for key in REQUIRED_ENV_VARS:
                    value = os.getenv(key)
                    if value:
                        env_to_save[key] = value
                
                if env_to_save:
                    save_to_env_file(env_to_save)
        
        test_api_connection()
        print_next_steps()
        return True
    
    print(f"\n🔧 需要配置 {len(missing_keys)} 个API密钥")
    
    # 收集新的环境变量
    new_env_vars = existing_env.copy()
    
    for key in missing_keys:
        info = REQUIRED_ENV_VARS[key]
        
        while True:
            value = prompt_for_api_key(key, info)
            if value is None:
                continue
            
            # 验证API密钥
            if validate_api_key(key, value):
                new_env_vars[key] = value
                print(f"✅ {key} 已设置")
                break
            else:
                retry = input("是否重新输入？(y/n): ").strip().lower()
                if retry not in ['y', 'yes', '是']:
                    new_env_vars[key] = value  # 用户坚持使用这个值
                    print(f"⚠️  {key} 已设置（未经验证）")
                    break
    
    # 保存到.env文件
    if save_to_env_file(new_env_vars):
        # 重新加载环境变量
        for key, value in new_env_vars.items():
            os.environ[key] = value
        
        print("\n✅ 环境变量已加载到当前会话")
    
    # 执行其他初始化步骤
    create_gitignore()
    create_output_directory()
    test_api_connection()
    print_next_steps()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 用户取消，再见！")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 初始化过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)