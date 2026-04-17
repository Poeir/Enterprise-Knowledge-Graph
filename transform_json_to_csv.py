#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Transform JSON data into CSV files for Neo4j import
"""

import json
import pandas as pd
from rich.console import Console

console = Console()

def transform_json_to_csv(input_file="synthetic_knowledge_graph_data_2.json"):
    """
    Transform JSON data into separate CSV files for nodes and edges
    
    Parameters:
    -----------
    input_file : str
        Path to the input JSON file
    """
    console.print("[yellow]⏳ กำลังอ่านข้อมูลและสกัด Nodes / Edges...[/yellow]")
    
    # 1. โหลดข้อมูลดิบ
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        console.print(f"[bold red]❌ ไม่พบไฟล์ {input_file} กรุณาตรวจสอบให้แน่ใจว่าไฟล์อยู่ในโฟลเดอร์[/bold red]")
        return
    except json.JSONDecodeError as e:
        console.print(f"[bold red]❌ ไฟล์ JSON ไม่ถูกต้อง: {e}[/bold red]")
        return

    # 2. เตรียม Lists สำหรับจัดเก็บข้อมูลแยกตามประเภท
    employees = []
    tickets = []
    skills_set = set()  # ใช้ Set เพื่อป้องกันชื่อ Skill ซ้ำกัน
    has_skill_edges = []
    requires_skill_edges = []

    # 3. ลูปสกัดข้อมูลพนักงาน (Employees) และความสัมพันธ์ (HAS_SKILL)
    console.print("[cyan]📋 กำลังประมวลผลข้อมูลพนักงาน...[/cyan]")
    for emp in data.get('employees', []):
        emp_id = emp['emp_id']
        employees.append({
            'emp_id': emp_id, 
            'name': emp['name'], 
            'department': emp['department']
        })
        
        for skill in emp.get('skills', []):
            skills_set.add(skill)  # เก็บลงตะกร้า Skill กลาง
            has_skill_edges.append({
                'source_id': emp_id, 
                'target_id': skill, 
                'type': 'HAS_SKILL'
            })

    # 4. ลูปสกัดข้อมูลทิกเก็ต (Tickets) และความสัมพันธ์ (REQUIRES_SKILL)
    console.print("[cyan]🎫 กำลังประมวลผลข้อมูลทิกเก็ต...[/cyan]")
    for tkt in data.get('tickets', []):
        ticket_id = tkt['ticket_id']
        tickets.append({
            'ticket_id': ticket_id, 
            'customer_company': tkt['customer_company'], 
            'issue_description': tkt['issue_description']
        })
        
        for skill in tkt.get('required_skills', []):
            skills_set.add(skill)  # เก็บลงตะกร้า Skill กลาง
            requires_skill_edges.append({
                'source_id': ticket_id, 
                'target_id': skill, 
                'type': 'REQUIRES_SKILL'
            })

    # 5. ใช้ Pandas แปลงเป็น DataFrame และบันทึกเป็น CSV
    console.print("[cyan]💾 กำลังบันทึก CSV files...[/cyan]")
    
    # Nodes
    pd.DataFrame(employees).to_csv('nodes_employee.csv', index=False, encoding='utf-8-sig')
    console.print("   ✓ nodes_employee.csv")
    
    pd.DataFrame(tickets).to_csv('nodes_ticket.csv', index=False, encoding='utf-8-sig')
    console.print("   ✓ nodes_ticket.csv")
    
    pd.DataFrame([{'skill_id': s} for s in sorted(skills_set)]).to_csv('nodes_skill.csv', index=False, encoding='utf-8-sig')
    console.print("   ✓ nodes_skill.csv")
    
    # Edges
    pd.DataFrame(has_skill_edges).to_csv('edges_has_skill.csv', index=False, encoding='utf-8-sig')
    console.print("   ✓ edges_has_skill.csv")
    
    pd.DataFrame(requires_skill_edges).to_csv('edges_requires_skill.csv', index=False, encoding='utf-8-sig')
    console.print("   ✓ edges_requires_skill.csv")

    # 6. แสดงสรุปผลการแปลง
    console.print("\n[bold green]✅ การแปลงข้อมูลเสร็จสมบูรณ์![/bold green]")
    console.print("\n[bold cyan]📊 สรุปข้อมูล:[/bold cyan]")
    console.print(f"   • พนักงาน (Employees): {len(employees)} คน")
    console.print(f"   • ทิกเก็ต (Tickets): {len(tickets)} รายการ")
    console.print(f"   • ทักษะ (Skills): {len(skills_set)} ประเภท")
    console.print(f"   • ความสัมพันธ์ HAS_SKILL: {len(has_skill_edges)} รายการ")
    console.print(f"   • ความสัมพันธ์ REQUIRES_SKILL: {len(requires_skill_edges)} รายการ")
    console.print("\n[bold yellow]📁 ไฟล์ที่สร้าง:[/bold yellow]")
    console.print("   1. nodes_employee.csv     - ข้อมูลพนักงาน")
    console.print("   2. nodes_ticket.csv       - ข้อมูลทิกเก็ต")
    console.print("   3. nodes_skill.csv        - ข้อมูลทักษะ")
    console.print("   4. edges_has_skill.csv    - ความสัมพันธ์ พนักงาน-ทักษะ")
    console.print("   5. edges_requires_skill.csv - ความสัมพันธ์ ทิกเก็ต-ทักษะ")
    console.print("\n[bold green]🚀 เตรียมพร้อมนำเข้า Neo4j ต่อไป![/bold green]\n")

if __name__ == "__main__":
    transform_json_to_csv()
