#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Generate synthetic data for Enterprise Knowledge Graph project
"""

import json
from api_client import call_api

def generate_and_save_synthetic_data():
    """
    Generate synthetic data for knowledge graph and save to JSON file
    """
    # [ปรับปรุงที่ 1] อัปเกรด Prompt ให้สร้างความซับซ้อน (Hub & Bottleneck)
    user_message = """จงสร้างข้อมูลจำลอง (Synthetic Data) สำหรับทำโปรเจกต์ Enterprise Knowledge Graph โดยผลลัพธ์จะต้องอยู่ในรูปแบบ JSON ที่ถูกต้อง (Valid JSON) เท่านั้น ห้ามมีข้อความอธิบายใดๆ นอกเหนือจาก JSON block 

โครงสร้าง JSON ที่ต้องการ:
{
  "employees": [
    {
      "emp_id": "EMP001",
      "name": "ชื่อ-นามสกุล (ภาษาไทย)",
      "department": "ชื่อแผนก (เช่น IT, Sales, Support, DevOps)",
      "skills": ["ชื่อทักษะ"] 
    }
  ],
  "tickets": [
    {
      "ticket_id": "TKT001",
      "customer_company": "ชื่อบริษัทลูกค้า (ภาษาไทย)",
      "issue_description": "รายละเอียดปัญหาที่แจ้งเข้ามาให้สมจริง (ภาษาไทย)",
      "required_skills": ["ชื่อทักษะ"] 
    }
  ]
}

เงื่อนไขสำคัญที่ต้องทำตามอย่างเคร่งครัดเพื่อสร้างกราฟที่ซับซ้อน:
1. สร้างพนักงาน 15 คน และทิกเก็ต 30 รายการ
2. Hubs (เดอะแบก): พนักงาน 3 คนต้องเป็นระดับ Senior ที่มีทักษะเยอะมาก (4-5 ทักษะ)
3. Bottlenecks (คอขวด): ต้องมีทักษะหายาก (เช่น "Cloud Architecture" หรือ "Cybersecurity") ที่มีพนักงานทำได้แค่ 1 คน แต่มีทิกเก็ตระดับวิกฤตต้องการทักษะนี้ถึง 4-5 รายการ
4. Bridges (สะพาน): ต้องมีพนักงานที่เป็นจุดเชื่อมระหว่างแผนก เช่น อยู่แผนก IT แต่มีทักษะ "Negotiation" หรืออยู่แผนก Sales แต่มีทักษะ "Python"
5. คำศัพท์ใน "required_skills" ต้องสะกดตรงกับ "skills" ของพนักงาน 100%
6. ผลลัพธ์ต้องเป็น JSON ล้วนๆ เริ่มด้วย { และจบด้วย }
"""
    
    print("🚀 กำลังสร้างข้อมูลจำลอง Enterprise Knowledge Graph แบบซับซ้อน...")
    print("⏳ โปรดรอสักครู่ (อาจใช้เวลา 1-2 นาที)...\n")
    
    response = call_api(user_message, show_details=False)
    
    if response and response.get('choices') and len(response['choices']) > 0:
        content = response['choices'][0]['message']['content']
        
        # [ปรับปรุงที่ 2] ดักจับและทำความสะอาด Markdown Ticks ก่อน Parse
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:] # ตัด ```json ออก
        if content.startswith("```"):
            content = content[3:] # ตัด ``` ออก
        if content.endswith("```"):
            content = content[:-3] # ตัด ``` ด้านหลังออก
        content = content.strip() # ลบช่องว่างหัวท้ายอีกรอบ
        
        try:
            json_data = json.loads(content)
            
            output_file = "synthetic_knowledge_graph_data_2.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            
            employees_count = len(json_data.get('employees', []))
            tickets_count = len(json_data.get('tickets', []))
            
            print("\n" + "="*70)
            print("✅ สร้างข้อมูลสำเร็จ!")
            print("="*70)
            print(f"📊 \nข้อมูลที่สร้าง:")
            print(f"   • จำนวนพนักงาน: {employees_count} คน")
            print(f"   • จำนวนทิกเก็ต: {tickets_count} รายการ")
            print(f"\n💾 บันทึกลงไฟล์: {output_file}")
            print("="*70 + "\n")
            
            print("📋 ตัวอย่างพนักงาน (3 คนแรก):")
            for emp in json_data.get('employees', [])[:3]:
                print(f"   • {emp['emp_id']}: {emp['name']} ({emp['department']}) - ทักษะ: {', '.join(emp['skills'])}")
            
            print("\n📋 ตัวอย่างทิกเก็ต (3 รายการแรก):")
            for ticket in json_data.get('tickets', [])[:3]:
                print(f"   • {ticket['ticket_id']}: {ticket['customer_company']}")
                print(f"      - ปัญหา: {ticket['issue_description'][:50]}...")
                print(f"      - ทักษะที่ต้อง: {', '.join(ticket['required_skills'])}")
            
            print("\n✨ ข้อมูลพร้อมแล้ว! สามารถนำไปรันผ่านสคริปต์แปลงเป็น CSV ได้เลย!")
            
            return json_data
        
        except json.JSONDecodeError as e:
            print(f"❌ ERROR: JSON ไม่ถูกต้อง - {e}")
            print("\n📝 เนื้อหาที่เกิดปัญหา:")
            print(content[:500] + "\n...\n" + content[-500:]) # โชว์ทั้งหัวและท้ายเพื่อให้ Debug ง่าย
            return None
    else:
        print("❌ ข้อผิดพลาด: ไม่ได้รับการตอบกลับจาก API")
        return None

if __name__ == "__main__":
    generate_and_save_synthetic_data()