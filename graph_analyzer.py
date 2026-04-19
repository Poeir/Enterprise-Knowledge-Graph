#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Analysis module for Enterprise Knowledge Graph
Identifies bottlenecks, hubs, bridges, and critical skills
"""

from neo4j_connector import get_neo4j_connector
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

class GraphAnalyzer:
    """
    Analyze knowledge graph for bottlenecks, hubs, and bridges
    """
    
    def __init__(self, connector):
        """
        Initialize analyzer
        
        Parameters:
        -----------
        connector : Neo4jConnector
            Neo4j connector instance
        """
        self.connector = connector
    
    def find_bottleneck_skills(self):
        """
        Find bottleneck skills - skills held by very few employees but needed by many tickets
        
        Returns:
        --------
        list
            List of bottleneck skills
        """
        query = """
        MATCH (s:skill)
        OPTIONAL MATCH (e:employee)-[:HAS_SKILL]->(s)
        WITH s, COUNT(DISTINCT e) as employee_count
        OPTIONAL MATCH (t:ticket)-[:REQUIRES_SKILL]->(s)
        WITH s, employee_count, COUNT(DISTINCT t) as ticket_count
        WHERE employee_count <= 1 AND ticket_count > 0
        RETURN 
            s.skill_id as skill_id,
            s.skill_name as skill_name,
            employee_count as num_employees,
            ticket_count as num_tickets,
            ROUND(TOFLOAT(ticket_count) / TOFLOAT(employee_count + 1) * 100, 2) as risk_score
        ORDER BY risk_score DESC
        """
        return self.connector.run_query(query)
    
    def find_critical_bottleneck_skills(self):
        """
        Find critical bottleneck skills - only 1 employee and multiple tickets need them
        
        Returns:
        --------
        list
            List of critical skills
        """
        query = """
        MATCH (e:employee)-[:HAS_SKILL]->(s:skill)
        WITH s, COUNT(DISTINCT e) as employee_count
        WHERE employee_count = 1
        MATCH (t:ticket)-[:REQUIRES_SKILL]->(s)
        WITH s, employee_count, COUNT(DISTINCT t) as ticket_count
        WHERE ticket_count >= 1
        MATCH (e:employee)-[:HAS_SKILL]->(s)
        RETURN 
            s.skill_id as skill_id,
            s.skill_name as skill_name,
            e.emp_id as sole_employee_id,
            e.name as sole_employee_name,
            e.department as sole_employee_dept,
            ticket_count as num_critical_tickets
        ORDER BY ticket_count DESC
        """
        return self.connector.run_query(query)
    
    def find_bridge_employees(self):
        """
        Find bridge employees - employees who connect different departments or skill domains
        
        Returns:
        --------
        list
            List of bridge employees
        """
        query = """
        MATCH (e:employee)-[:HAS_SKILL]->(s:skill)
        WITH e, COUNT(DISTINCT s) as skill_count
        MATCH (e)-[:HAS_SKILL]->(s1:skill)
        MATCH (t1:ticket)-[:REQUIRES_SKILL]->(s1)
        WITH e, skill_count, COUNT(DISTINCT t1) as coverage_tickets
        WHERE coverage_tickets > 2
        RETURN 
            e.emp_id as emp_id,
            e.name as name,
            e.department as department,
            skill_count as num_skills,
            coverage_tickets as tickets_covered,
            ROUND(TOFLOAT(coverage_tickets) / (TOFLOAT(skill_count) + 1) * 100, 2) as bridge_score
        ORDER BY bridge_score DESC
        """
        return self.connector.run_query(query)
    
    def find_underutilized_skills(self):
        """
        Find underutilized skills - held by employees but not needed by any tickets
        
        Returns:
        --------
        list
            List of underutilized skills
        """
        query = """
        MATCH (s:skill)
        OPTIONAL MATCH (e:employee)-[:HAS_SKILL]->(s)
        WITH s, COUNT(DISTINCT e) as employee_count
        OPTIONAL MATCH (t:ticket)-[:REQUIRES_SKILL]->(s)
        WITH s, employee_count, COUNT(DISTINCT t) as ticket_count
        WHERE ticket_count = 0 AND employee_count > 0
        RETURN 
            s.skill_id as skill_id,
            s.skill_name as skill_name,
            employee_count as num_employees,
            ticket_count as num_tickets
        ORDER BY employee_count DESC
        """
        return self.connector.run_query(query)
    
    def find_high_demand_skills(self):
        """
        Find high-demand skills - needed by many tickets
        
        Returns:
        --------
        list
            List of high-demand skills
        """
        query = """
        MATCH (s:skill)
        OPTIONAL MATCH (t:ticket)-[:REQUIRES_SKILL]->(s)
        WITH s, COUNT(DISTINCT t) as ticket_count
        OPTIONAL MATCH (e:employee)-[:HAS_SKILL]->(s)
        WITH s, ticket_count, COUNT(DISTINCT e) as employee_count
        WHERE ticket_count > 0
        RETURN 
            s.skill_id as skill_id,
            s.skill_name as skill_name,
            ticket_count as num_tickets,
            employee_count as num_employees,
            CASE 
                WHEN employee_count = 0 THEN 'ขาดบุคลากร'
                WHEN employee_count < 3 THEN 'มีน้อย'
                ELSE 'เพียงพอ'
            END as availability
        ORDER BY ticket_count DESC
        """
        return self.connector.run_query(query)
    
    def find_skill_gaps(self):
        """
        Find skill gaps - tickets that need skills no employee has
        
        Returns:
        --------
        list
            List of skill gaps
        """
        query = """
        MATCH (t:ticket)-[:REQUIRES_SKILL]->(s:skill)
        WITH t, s, COLLECT(DISTINCT e.emp_id) as employee_ids
        FROM (MATCH (e:employee)-[:HAS_SKILL]->(s) RETURN e.emp_id)
        WHERE size(employee_ids) = 0
        RETURN 
            t.ticket_id as ticket_id,
            t.customer_company as customer_company,
            t.issue_description as issue_description,
            COLLECT(s.skill_name) as missing_skills
        """
        # Alternative query that works with all Neo4j versions
        query = """
        MATCH (t:ticket)-[:REQUIRES_SKILL]->(s:skill)
        WITH DISTINCT t, s
        OPTIONAL MATCH (e:employee)-[:HAS_SKILL]->(s)
        WITH t, s, COUNT(e) as emp_count
        WHERE emp_count = 0
        RETURN 
            t.ticket_id as ticket_id,
            t.customer_company as customer_company,
            t.issue_description as issue_description,
            COLLECT(DISTINCT s.skill_name) as missing_skills
        """
        return self.connector.run_query(query)
    
    def find_department_strengths(self):
        """
        Find which skills each department specializes in
        
        Returns:
        --------
        list
            Department specializations
        """
        query = """
        MATCH (e:employee)-[:HAS_SKILL]->(s:skill)
        WITH e.department as department, s.skill_name as skill_name, COUNT(*) as count
        ORDER BY department, count DESC
        WITH department, COLLECT({skill: skill_name, count: count}) as skills
        RETURN 
            department,
            skills[0..3] as top_3_skills
        ORDER BY department
        """
        return self.connector.run_query(query)
    
    def generate_analysis_report(self):
        """
        Generate comprehensive analysis report
        """
        console.print("\n" + "="*70)
        console.print("[bold cyan]📊 Enterprise Knowledge Graph Analysis Report[/bold cyan]")
        console.print("="*70 + "\n")
        
        # 1. Bottleneck Skills
        console.print("[bold yellow]🚨 Bottleneck Skills (ทักษะที่เสี่ยง)[/bold yellow]")
        bottlenecks = self.find_bottleneck_skills()
        if bottlenecks:
            table = Table(show_header=True, header_style="bold red")
            table.add_column("Skill ID")
            table.add_column("Skill Name")
            table.add_column("Employees")
            table.add_column("Tickets Need")
            table.add_column("Risk Score", style="red")
            
            for record in bottlenecks[:5]:
                table.add_row(
                    str(record['skill_id']),
                    str(record['skill_name']),
                    str(record['num_employees']),
                    str(record['num_tickets']),
                    str(record['risk_score'])
                )
            console.print(table)
        else:
            console.print("[green]✅ ไม่มี Bottleneck Skills[/green]")
        
        # 2. Critical Bottleneck Skills
        console.print("\n[bold red]⚠️  Critical Bottleneck Skills (วิกฤต)[/bold red]")
        critical = self.find_critical_bottleneck_skills()
        if critical:
            table = Table(show_header=True, header_style="bold red")
            table.add_column("Skill Name")
            table.add_column("Sole Employee")
            table.add_column("Department")
            table.add_column("Critical Tickets")
            
            for record in critical:
                table.add_row(
                    str(record['skill_name']),
                    f"{record['sole_employee_name']} ({record['sole_employee_id']})",
                    str(record['sole_employee_dept']),
                    str(record['num_critical_tickets'])
                )
            console.print(table)
        else:
            console.print("[green]✅ ไม่มี Critical Bottleneck[/green]")
        
        # 3. Bridge Employees
        console.print("\n[bold blue]🌉 Bridge Employees (คนเชื่อมต่อ)[/bold blue]")
        bridges = self.find_bridge_employees()
        if bridges:
            table = Table(show_header=True, header_style="bold blue")
            table.add_column("Name")
            table.add_column("Department")
            table.add_column("Skills")
            table.add_column("Coverage")
            
            for record in bridges[:5]:
                table.add_row(
                    str(record['name']),
                    str(record['department']),
                    str(record['num_skills']),
                    str(record['tickets_covered'])
                )
            console.print(table)
        else:
            console.print("[yellow]⚠️  ไม่มี Bridge Employees[/yellow]")
        
        # 4. High Demand Skills
        console.print("\n[bold green]📈 High Demand Skills[/bold green]")
        high_demand = self.find_high_demand_skills()
        if high_demand:
            table = Table(show_header=True, header_style="bold green")
            table.add_column("Skill Name")
            table.add_column("Tickets")
            table.add_column("Employees")
            table.add_column("Availability")
            
            for record in high_demand[:5]:
                table.add_row(
                    str(record['skill_name']),
                    str(record['num_tickets']),
                    str(record['num_employees']),
                    str(record['availability'])
                )
            console.print(table)
        
        # 5. Skill Gaps
        console.print("\n[bold red]❌ Skill Gaps (ทักษะที่ขาดบุคลากร)[/bold red]")
        gaps = self.find_skill_gaps()
        if gaps:
            console.print(f"พบ {len(gaps)} ทิกเก็ตที่มีทักษะที่ไม่มีใครมี\n")
            for record in gaps[:3]:
                console.print(f"[yellow]📋 {record['ticket_id']}: {record['customer_company']}[/yellow]")
                console.print(f"   ทักษะที่ขาด: {', '.join(record['missing_skills'])}")
        else:
            console.print("[green]✅ ไม่มี Skill Gaps[/green]")
        
        # 6. Department Strengths
        console.print("\n[bold cyan]🏢 Department Strengths[/bold cyan]")
        dept_strengths = self.find_department_strengths()
        if dept_strengths:
            table = Table(show_header=True, header_style="bold cyan")
            table.add_column("Department")
            table.add_column("Top 3 Skills")
            
            for record in dept_strengths:
                skills_str = "\n".join([f"{s['skill']} ({s['count']})" for s in record['top_3_skills']])
                table.add_row(str(record['department']), skills_str)
            console.print(table)
        
        console.print("\n" + "="*70)


def main():
    """
    Main function for analysis
    """
    connector = get_neo4j_connector()
    
    if not connector.connect():
        return
    
    analyzer = GraphAnalyzer(connector)
    analyzer.generate_analysis_report()
    
    connector.disconnect()


if __name__ == "__main__":
    main()
