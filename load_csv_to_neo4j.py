#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Load CSV data into Neo4j database
"""

import pandas as pd
from rich.console import Console
from rich.progress import track
from neo4j_connector import get_neo4j_connector

console = Console()

class CSVLoader:
    """
    Load CSV files into Neo4j database
    """
    
    def __init__(self, connector):
        """
        Initialize CSV Loader
        
        Parameters:
        -----------
        connector : Neo4jConnector
            Neo4j connector instance
        """
        self.connector = connector
    
    def load_employees(self, csv_file="data/nodes_employee.csv"):
        """
        Load employees from CSV
        
        Parameters:
        -----------
        csv_file : str
            Path to employee CSV file
        """
        console.print(f"[cyan]📝 กำลังโหลด Employees จาก {csv_file}...[/cyan]")
        
        try:
            df = pd.read_csv(csv_file, encoding='utf-8')
            
            for _, row in track(df.iterrows(), total=len(df), description="โหลด Employees"):
                query = """
                CREATE (e:employee {
                    emp_id: $emp_id,
                    name: $name,
                    department: $department
                })
                """
                self.connector.run_query(query, {
                    'emp_id': str(row['emp_id']),
                    'name': str(row['name']),
                    'department': str(row['department'])
                })
            
            console.print(f"[green]✅ โหลด {len(df)} พนักงานสำเร็จ[/green]")
            return True
        except Exception as e:
            console.print(f"[red]❌ ข้อผิดพลาดในการโหลด Employees: {e}[/red]")
            return False
    
    def load_skills(self, csv_file="data/nodes_skill.csv"):
        """
        Load skills from CSV
        
        Parameters:
        -----------
        csv_file : str
            Path to skill CSV file
        """
        console.print(f"[cyan]📝 กำลังโหลด Skills จาก {csv_file}...[/cyan]")
        
        try:
            df = pd.read_csv(csv_file, encoding='utf-8')
            
            for _, row in track(df.iterrows(), total=len(df), description="โหลด Skills"):
                # Support both old format (skill_name only) and new format (skill_id + skill_name)
                skill_id = str(row['skill_id']) if 'skill_id' in row else f"SKILL{row.name + 1:03d}"
                skill_name = str(row['skill_name']) if 'skill_name' in row else str(row.iloc[0])
                
                query = """
                CREATE (s:skill {
                    skill_id: $skill_id,
                    skill_name: $skill_name
                })
                """
                self.connector.run_query(query, {
                    'skill_id': skill_id,
                    'skill_name': skill_name
                })
            
            console.print(f"[green]✅ โหลด {len(df)} ทักษะสำเร็จ[/green]")
            return True
        except Exception as e:
            console.print(f"[red]❌ ข้อผิดพลาดในการโหลด Skills: {e}[/red]")
            return False
    
    def load_tickets(self, csv_file="data/nodes_ticket.csv"):
        """
        Load tickets from CSV
        
        Parameters:
        -----------
        csv_file : str
            Path to ticket CSV file
        """
        console.print(f"[cyan]📝 กำลังโหลด Tickets จาก {csv_file}...[/cyan]")
        
        try:
            df = pd.read_csv(csv_file, encoding='utf-8')
            
            for _, row in track(df.iterrows(), total=len(df), description="โหลด Tickets"):
                query = """
                CREATE (t:ticket {
                    ticket_id: $ticket_id,
                    customer_company: $customer_company,
                    issue_description: $issue_description
                })
                """
                self.connector.run_query(query, {
                    'ticket_id': str(row['ticket_id']),
                    'customer_company': str(row['customer_company']),
                    'issue_description': str(row['issue_description'])
                })
            
            console.print(f"[green]✅ โหลด {len(df)} ทิกเก็ตสำเร็จ[/green]")
            return True
        except Exception as e:
            console.print(f"[red]❌ ข้อผิดพลาดในการโหลด Tickets: {e}[/red]")
            return False
    
    def load_has_skill_edges(self, csv_file="data/edges_has_skill.csv"):
        """
        Load HAS_SKILL relationships
        
        Parameters:
        -----------
        csv_file : str
            Path to HAS_SKILL edges CSV file
        """
        console.print(f"[cyan]📝 กำลังโหลด HAS_SKILL relationships จาก {csv_file}...[/cyan]")
        
        try:
            df = pd.read_csv(csv_file, encoding='utf-8')
            
            for _, row in track(df.iterrows(), total=len(df), description="โหลด HAS_SKILL"):
                query = """
                MATCH (e:employee {emp_id: $emp_id})
                MATCH (s:skill {skill_name: $skill_name})
                CREATE (e)-[r:HAS_SKILL]->(s)
                """
                self.connector.run_query(query, {
                    'emp_id': str(row['source_id']),
                    'skill_name': str(row['target_id'])
                })
            
            console.print(f"[green]✅ สร้าง {len(df)} HAS_SKILL relationships สำเร็จ[/green]")
            return True
        except Exception as e:
            console.print(f"[red]❌ ข้อผิดพลาดในการสร้าง HAS_SKILL: {e}[/red]")
            return False
    
    def load_requires_skill_edges(self, csv_file="data/edges_requires_skill.csv"):
        """
        Load REQUIRES_SKILL relationships
        
        Parameters:
        -----------
        csv_file : str
            Path to REQUIRES_SKILL edges CSV file
        """
        console.print(f"[cyan]📝 กำลังโหลด REQUIRES_SKILL relationships จาก {csv_file}...[/cyan]")
        
        try:
            df = pd.read_csv(csv_file, encoding='utf-8')
            
            for _, row in track(df.iterrows(), total=len(df), description="โหลด REQUIRES_SKILL"):
                query = """
                MATCH (t:ticket {ticket_id: $ticket_id})
                MATCH (s:skill {skill_name: $skill_name})
                CREATE (t)-[r:REQUIRES_SKILL]->(s)
                """
                self.connector.run_query(query, {
                    'ticket_id': str(row['source_id']),
                    'skill_name': str(row['target_id'])
                })
            
            console.print(f"[green]✅ สร้าง {len(df)} REQUIRES_SKILL relationships สำเร็จ[/green]")
            return True
        except Exception as e:
            console.print(f"[red]❌ ข้อผิดพลาดในการสร้าง REQUIRES_SKILL: {e}[/red]")
            return False
    
    def load_all(self):
        """
        Load all data into Neo4j
        """
        console.print("\n" + "="*70)
        console.print("[bold cyan]🚀 เริ่มโหลดข้อมูลเข้า Neo4j[/bold cyan]")
        console.print("="*70 + "\n")
        
        # Load nodes
        if not self.load_employees():
            return False
        if not self.load_skills():
            return False
        if not self.load_tickets():
            return False
        
        # Load edges
        if not self.load_has_skill_edges():
            return False
        if not self.load_requires_skill_edges():
            return False
        
        console.print("\n" + "="*70)
        console.print("[bold green]✅ โหลดข้อมูลทั้งหมดสำเร็จ![/bold green]")
        console.print("="*70 + "\n")
        return True


def main():
    """
    Main function to load CSV data
    """
    connector = get_neo4j_connector()
    
    if not connector.connect():
        return
    
    # Optionally clear database first
    console.print("\n[yellow]⚠️  ต้องการลบข้อมูลเดิมก่อนโหลดใหม่ไหม (y/n)? [/yellow]")
    choice = input().strip().lower()
    if choice == 'y':
        connector.clear_database()
    
    # Load data
    loader = CSVLoader(connector)
    loader.load_all()
    
    connector.disconnect()


if __name__ == "__main__":
    main()
