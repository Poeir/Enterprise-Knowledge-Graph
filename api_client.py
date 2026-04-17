import requests
import json
import os
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

console = Console()

# Load environment variables from .env file
load_dotenv()
# Configuration
API_KEY = os.getenv("API_KEY")  # Get API key from environment variables
API_URL = "https://gen.ai.kku.ac.th/api/v1/chat/completions"

# Headers
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

# Default system message
SYSTEM_MESSAGE = "You are a helpful assistant."

def format_thai_response(result, show_details=True):
    """
    Format API response beautifully in Thai language with markdown rendering
    
    Parameters:
    -----------
    result : dict
        API response dictionary
    show_details : bool, default=True
        If True, show full response (model info, tokens, quota)
        If False, show only AI message content
    """
    if show_details:
        console.print("\n" + "="*70)
        console.print("[bold cyan]📋 ผลลัพธ์จาก API KKU[/bold cyan]")
        console.print("="*70)
        
        # Model Information
        console.print(f"\n[bold green]🤖 ข้อมูลรุ่นโมเดล:[/bold green]")
        console.print(f"   • ชื่อโมเดล: {result.get('model', 'N/A')}")
        console.print(f"   • ผู้ให้บริการ: {result.get('provider', 'N/A')}")
        console.print(f"   • ID สำเร็จสูตร: {result.get('id', 'N/A')[:20]}...")
    
    # Message Content
    if result.get('choices') and len(result['choices']) > 0:
        message = result['choices'][0].get('message', {})
        content = message.get('content', 'ไม่พบเนื้อหา')
        
        if show_details:
            # Display content as markdown with full details
            console.print(f"\n[bold blue]💬 คำตอบ:[/bold blue]")
            console.print(f"   [dim]บทบาท: {message.get('role', 'N/A')}[/dim]")
            console.print("")
            
            # Render markdown content in a nice panel
            md = Markdown(content)
            console.print(Panel(md, title="📝 เนื้อหา", border_style="blue", expand=False))
        else:
            # Display only the content (markdown format)
            md = Markdown(content)
            console.print(md)
    
    if show_details:
        # Token Usage
        usage = result.get('usage', {})
        console.print(f"\n[bold yellow]📊 การใช้งาน Token:[/bold yellow]")
        console.print(f"   • Token ที่ป้อน: {usage.get('prompt_tokens', 0)}")
        console.print(f"   • Token ที่สร้าง: {usage.get('completion_tokens', 0)}")
        console.print(f"   • Token ทั้งหมด: {usage.get('total_tokens', 0)}")
        
        # Quota Information
        quota = result.get('model_quota', {})
        if quota:
            console.print(f"\n[bold magenta]📈 ข้อมูลโควต้า:[/bold magenta]")
            console.print(f"   • โควต้ารายวัน: {quota.get('daily_quota_tokens', 0):,} Tokens")
            console.print(f"   • ใช้งานแล้ว: {quota.get('daily_usage_tokens', 0):,} Tokens")
            console.print(f"   • เหลืออยู่: {quota.get('daily_remaining_tokens', 0):,} Tokens")
        
        console.print("\n" + "="*70 + "\n")

def call_api(user_message, show_details=True):
    """
    Call the KKU AI API with custom user message
    
    Parameters:
    -----------
    user_message : str
        Message to send to the API
    show_details : bool, default=True
        If True, show full response (model info, tokens, quota)
        If False, show only AI message content
    
    Returns:
    --------
    dict or None
        API response dictionary or None if error occurs
    """
    # Build payload with user message
    payload = {
        "model": "claude-sonnet-4.6",
        "messages": [
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": user_message}
        ],
        "stream": False
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        result = response.json()
        # Display formatted Thai response with show_details parameter
        format_thai_response(result, show_details=show_details)
        
        return result
    
    except requests.exceptions.RequestException as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        return None
