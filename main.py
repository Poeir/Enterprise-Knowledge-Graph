#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Main script to interact with KKU AI API
"""

from api_client import call_api

def main():
    """
    Main function to handle user input and call API
    """
    print("\n" + "="*70)
    print("💬 ส่ง Message ไปยัง API KKU")
    print("="*70)
    
    user_message = input("\n📝 กรุณาพิมพ์ข้อความของคุณ: ")

    
    if user_message.strip():
        print(f"\n⏳ กำลังส่งข้อความ: '{user_message}'\n")
        result = call_api(user_message, show_details=False)
        return result
    else:
        print("\n❌ ข้อผิดพลาด: ไม่สามารถส่ง message ได้เนื่องจากข้อความว่างเปล่า")
        return None

if __name__ == "__main__":
    main()
