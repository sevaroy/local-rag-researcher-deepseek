#!/usr/bin/env python3
"""
統一啟動腳本 - 同時運行 Streamlit 和 LINE Bot 服務
"""

import os
import sys
import subprocess
import signal
import time
from multiprocessing import Process

class ServiceManager:
    def __init__(self):
        self.processes = []
        
    def start_streamlit(self):
        """啟動 Streamlit 服務"""
        print("🌐 啟動 Streamlit Web 介面...")
        try:
            process = subprocess.Popen([
                sys.executable, "-m", "streamlit", "run", "app.py",
                "--server.port", "8501",
                "--server.address", "0.0.0.0"
            ])
            self.processes.append(('Streamlit', process))
            print(f"✅ Streamlit 已啟動 - PID: {process.pid}")
            print(f"📱 Web 介面: http://localhost:8501")
            return process
        except Exception as e:
            print(f"❌ Streamlit 啟動失敗: {e}")
            return None
    
    def start_linebot(self, use_simple=False):
        """啟動 LINE Bot 服務"""
        script = "simple_linebot.py" if use_simple else "main.py"
        print(f"🤖 啟動 LINE Bot 服務 ({script})...")
        
        try:
            if use_simple:
                process = subprocess.Popen([sys.executable, script])
            else:
                # 使用 uvicorn 啟動 FastAPI 應用程式
                process = subprocess.Popen([
                    sys.executable, "-m", "uvicorn", "main:app", 
                    "--host", "0.0.0.0", "--port", "8000", "--reload"
                ])
            self.processes.append(('LINE Bot', process))
            print(f"✅ LINE Bot 已啟動 - PID: {process.pid}")
            print(f"🔗 Webhook 端點: http://localhost:8000/webhook")
            return process
        except Exception as e:
            print(f"❌ LINE Bot 啟動失敗: {e}")
            return None
    
    def check_environment(self):
        """檢查環境配置"""
        print("🔍 檢查環境配置...")
        
        # 檢查必要文件
        required_files = ['app.py', 'main.py', 'simple_linebot.py', '.env']
        missing_files = [f for f in required_files if not os.path.exists(f)]
        
        if missing_files:
            print(f"⚠️  缺少文件: {', '.join(missing_files)}")
            if '.env' in missing_files:
                print("💡 提示: 請複製 .env.example 為 .env 並設定你的 API 金鑰")
        
        # 檢查端口是否被占用
        import socket
        def check_port(port, service):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            if result == 0:
                print(f"⚠️  端口 {port} ({service}) 已被占用")
                return False
            return True
        
        streamlit_ok = check_port(8501, "Streamlit")
        linebot_ok = check_port(8000, "LINE Bot")
        
        return len(missing_files) == 0 and streamlit_ok and linebot_ok
    
    def monitor_services(self):
        """監控服務狀態"""
        print("\n🔄 服務監控中... (按 Ctrl+C 停止所有服務)")
        try:
            while True:
                for name, process in self.processes:
                    if process.poll() is not None:
                        print(f"⚠️  {name} 服務意外停止 (退出碼: {process.returncode})")
                        self.processes.remove((name, process))
                
                time.sleep(5)  # 每5秒檢查一次
                
        except KeyboardInterrupt:
            print("\n🛑 收到停止信號，正在關閉服務...")
            self.stop_all_services()
    
    def stop_all_services(self):
        """停止所有服務"""
        for name, process in self.processes:
            try:
                print(f"🔴 停止 {name} 服務...")
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ {name} 已停止")
            except subprocess.TimeoutExpired:
                print(f"⚠️  強制終止 {name}")
                process.kill()
            except Exception as e:
                print(f"❌ 停止 {name} 時發生錯誤: {e}")
        
        self.processes.clear()
        print("🎉 所有服務已停止")

def main():
    print("🚀 RAG 研究助手 - 服務啟動器")
    print("=" * 50)
    
    manager = ServiceManager()
    
    # 檢查環境
    if not manager.check_environment():
        print("\n❌ 環境檢查失敗，請修復上述問題後重試")
        return
    
    print("\n✅ 環境檢查通過")
    
    # 詢問用戶選擇
    print("\n📋 服務選擇:")
    print("1. 啟動 Streamlit + 完整版 LINE Bot (預設)")
    print("2. 啟動 Streamlit + 簡化版 LINE Bot") 
    print("3. 僅啟動 Streamlit")
    print("4. 僅啟動 LINE Bot")
    print("5. 退出")
    
    try:
        choice = input("\n請選擇 (預設 1): ").strip()
        if not choice:
            choice = "1"  # 預設選擇
        
        if choice in ['1', '2']:
            # 同時啟動兩個服務
            manager.start_streamlit()
            time.sleep(2)  # 等待 Streamlit 啟動
            manager.start_linebot(use_simple=(choice == '2'))
            
        elif choice == '3':
            manager.start_streamlit()
            
        elif choice == '4':
            use_simple = input("使用簡化版 LINE Bot? (y/N): ").lower().startswith('y')
            manager.start_linebot(use_simple=use_simple)
            
        elif choice == '5':
            print("👋 退出程式")
            return
            
        else:
            print("❌ 無效選擇，使用預設選項 1")
            manager.start_streamlit()
            time.sleep(2)  # 等待 Streamlit 啟動
            manager.start_linebot(use_simple=False)
        
        if manager.processes:
            print(f"\n🎉 已啟動 {len(manager.processes)} 個服務")
            print("\n📊 服務狀態:")
            for name, process in manager.processes:
                print(f"  • {name}: PID {process.pid}")
            
            print("\n🔗 訪問連結:")
            if any(name == 'Streamlit' for name, _ in manager.processes):
                print("  • Streamlit Web 介面: http://localhost:8501")
            if any(name == 'LINE Bot' for name, _ in manager.processes):
                print("  • LINE Bot API: http://localhost:8000")
                print("  • LINE Bot Webhook: http://localhost:8000/webhook")
                print("  • API 文檔: http://localhost:8000/docs")
            
            # 開始監控
            manager.monitor_services()
    
    except KeyboardInterrupt:
        print("\n🛑 用戶取消操作")
    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
    finally:
        manager.stop_all_services()

if __name__ == "__main__":
    main()