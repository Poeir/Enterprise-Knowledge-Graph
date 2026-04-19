#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Cypher Query Builder for Enterprise Knowledge Graph
"""

from neo4j_connector import get_neo4j_connector
from rich.console import Console
from rich.table import Table

console = Console()

class CypherQueryBuilder:
    """
    Build and execute Cypher queries for knowledge graph analysis
    """
    
    def __init__(self, connector):
        """
        Initialize query builder
        
        Parameters:
        -----------
        connector : Neo4jConnector
            Neo4j connector instance
        """
        self.connector = connector
    
    def find_employees_by_skill(self, skill_name):
        """
        Find all employees with a specific skill
        
        Parameters:
        -----------
        skill_name : str
            Name of the skill
        
        Returns:
        --------
        list
            List of employees with the skill
        """
        query = """
        MATCH (e:employee)-[:HAS_SKILL]->(s:skill {skill_name: $skill_name})
        RETURN 
            e.emp_id as emp_id,
            e.name as name,
            e.department as department,
            COLLECT(s.skill_name) as skills
        """
        return self.connector.run_query(query, {'skill_name': skill_name})
    
    def find_skills_for_employee(self, emp_id):
        """
        Find all skills for a specific employee
        
        Parameters:
        -----------
        emp_id : str
            Employee ID
        
        Returns:
        --------
        list
            List of skills for the employee
        """
        query = """
        MATCH (e:employee {emp_id: $emp_id})-[:HAS_SKILL]->(s:skill)
        RETURN 
            e.emp_id as emp_id,
            e.name as name,
            e.department as department,
            COLLECT(s.skill_name) as skills,
            COUNT(s) as skill_count
        """
        return self.connector.run_query(query, {'emp_id': emp_id})
    
    def find_tickets_requiring_skill(self, skill_name):
        """
        Find all tickets that require a specific skill
        
        Parameters:
        -----------
        skill_name : str
            Name of the skill
        
        Returns:
        --------
        list
            List of tickets requiring the skill
        """
        query = """
        MATCH (t:ticket)-[:REQUIRES_SKILL]->(s:skill {skill_name: $skill_name})
        RETURN 
            t.ticket_id as ticket_id,
            t.customer_company as customer_company,
            t.issue_description as issue_description,
            COLLECT(s.skill_name) as required_skills
        """
        return self.connector.run_query(query, {'skill_name': skill_name})
    
    def find_employees_for_ticket(self, ticket_id):
        """
        Find employees who can handle a specific ticket
        
        Parameters:
        -----------
        ticket_id : str
            Ticket ID
        
        Returns:
        --------
        list
            List of employees who can handle the ticket
        """
        query = """
        MATCH (t:ticket {ticket_id: $ticket_id})-[:REQUIRES_SKILL]->(s:skill)
        MATCH (e:employee)-[:HAS_SKILL]->(s)
        WITH e, COUNT(DISTINCT s) as matching_skills
        OPTIONAL MATCH (t)-[:REQUIRES_SKILL]->(req_skill:skill)
        WITH e, matching_skills, COUNT(DISTINCT req_skill) as required_skills
        RETURN 
            e.emp_id as emp_id,
            e.name as name,
            e.department as department,
            matching_skills as matching_skills,
            required_skills as required_skills,
            CASE 
                WHEN matching_skills = required_skills THEN 'ทั้งหมด'
                WHEN matching_skills > 0 THEN 'บางส่วน'
                ELSE 'ไม่มี'
            END as coverage
        ORDER BY matching_skills DESC
        """
        return self.connector.run_query(query, {'ticket_id': ticket_id})
    
    def find_skill_hubs(self, min_employees=2):
        """
        Find skills that are held by multiple employees (hub skills)
        
        Parameters:
        -----------
        min_employees : int
            Minimum number of employees to be considered a hub
        
        Returns:
        --------
        list
            List of hub skills
        """
        query = """
        MATCH (e:employee)-[:HAS_SKILL]->(s:skill)
        WITH s, COUNT(DISTINCT e) as employee_count
        WHERE employee_count >= $min_employees
        RETURN 
            s.skill_id as skill_id,
            s.skill_name as skill_name,
            employee_count as num_employees
        ORDER BY employee_count DESC
        """
        return self.connector.run_query(query, {'min_employees': min_employees})
    
    def find_expert_employees(self, min_skills=3):
        """
        Find expert employees with many skills
        
        Parameters:
        -----------
        min_skills : int
            Minimum number of skills
        
        Returns:
        --------
        list
            List of expert employees
        """
        query = """
        MATCH (e:employee)-[:HAS_SKILL]->(s:skill)
        WITH e, COUNT(DISTINCT s) as skill_count
        WHERE skill_count >= $min_skills
        RETURN 
            e.emp_id as emp_id,
            e.name as name,
            e.department as department,
            skill_count as num_skills,
            COLLECT(s.skill_name) as skills
        ORDER BY skill_count DESC
        """
        return self.connector.run_query(query, {'min_skills': min_skills})
    
    def get_all_employees(self):
        """
        Get all employees with their skills and department
        
        Returns:
        --------
        list
            List of all employees
        """
        query = """
        MATCH (e:employee)
        OPTIONAL MATCH (e)-[:HAS_SKILL]->(s:skill)
        RETURN 
            e.emp_id as emp_id,
            e.name as name,
            e.department as department,
            COLLECT(s.skill_name) as skills,
            COUNT(s) as skill_count
        ORDER BY e.name
        """
        return self.connector.run_query(query)
    
    def get_all_skills(self):
        """
        Get all skills with employee and ticket counts
        
        Returns:
        --------
        list
            List of all skills
        """
        query = """
        MATCH (s:skill)
        OPTIONAL MATCH (e:employee)-[:HAS_SKILL]->(s)
        WITH s, COUNT(DISTINCT e) as emp_count
        OPTIONAL MATCH (t:ticket)-[:REQUIRES_SKILL]->(s)
        RETURN 
            s.skill_id as skill_id,
            s.skill_name as skill_name,
            emp_count as num_employees,
            COUNT(DISTINCT t) as num_tickets
        ORDER BY s.skill_name
        """
        return self.connector.run_query(query)
    
    def get_all_tickets(self):
        """
        Get all tickets with required skills
        
        Returns:
        --------
        list
            List of all tickets
        """
        query = """
        MATCH (t:ticket)
        OPTIONAL MATCH (t)-[:REQUIRES_SKILL]->(s:skill)
        RETURN 
            t.ticket_id as ticket_id,
            t.customer_company as customer_company,
            t.issue_description as issue_description,
            COLLECT(s.skill_name) as required_skills,
            COUNT(s) as skill_count
        ORDER BY t.ticket_id
        """
        return self.connector.run_query(query)

    def get_graph_visualization_data(self):
        """
        Get graph data for visualization (nodes and edges)
        
        Returns:
        --------
        dict
            Graph structure with nodes and relationships
        """
        # Get all nodes
        nodes_query = """
        MATCH (n)
        RETURN 
            DISTINCT id(n) as id,
            labels(n)[0] as type,
            CASE 
                WHEN 'employee' IN labels(n) THEN n.name
                WHEN 'skill' IN labels(n) THEN n.skill_name
                WHEN 'ticket' IN labels(n) THEN n.ticket_id
                ELSE n.name
            END as label,
            CASE
                WHEN 'employee' IN labels(n) THEN coalesce(n.emp_id, '')
                WHEN 'skill' IN labels(n) THEN coalesce(n.skill_id, '')
                WHEN 'ticket' IN labels(n) THEN coalesce(n.ticket_id, '')
                ELSE ''
            END as id_field
        """
        
        # Get all relationships
        edges_query = """
        MATCH (a)-[r]->(b)
        RETURN 
            id(a) as source,
            id(b) as target,
            type(r) as type
        """
        
        nodes_result = self.connector.run_query(nodes_query) or []
        edges_result = self.connector.run_query(edges_query) or []
        
        nodes = []
        edges = []
        
        for record in nodes_result:
            nodes.append({
                'id': str(record.get('id')),
                'type': record.get('type'),
                'label': record.get('label'),
                'id_field': record.get('id_field')
            })
        
        for record in edges_result:
            edges.append({
                'source': str(record.get('source')),
                'target': str(record.get('target')),
                'type': record.get('type')
            })
        
        return {'nodes': nodes, 'edges': edges}

    def get_graph_statistics(self):
        """
        Get overall statistics about the knowledge graph
        
        Returns:
        --------
        dict
            Graph statistics
        """
        query = """
        MATCH (e:employee) 
        WITH COUNT(e) as emp_count
        MATCH (s:skill) 
        WITH emp_count, COUNT(s) as skill_count
        MATCH (t:ticket) 
        WITH emp_count, skill_count, COUNT(t) as ticket_count
        MATCH ()-[r:HAS_SKILL]->() 
        WITH emp_count, skill_count, ticket_count, COUNT(r) as has_skill_count
        MATCH ()-[r:REQUIRES_SKILL]->() 
        RETURN 
            emp_count as employees,
            skill_count as skills,
            ticket_count as tickets,
            has_skill_count as has_skill_relationships,
            COUNT(r) as requires_skill_relationships
        """
        return self.connector.run_query(query)
    
    def display_results_table(self, results, title="ผลลัพธ์"):
        """Display results in a formatted table"""
        if not results:
            console.print(f"[yellow]ไม่มีผลลัพธ์สำหรับ {title}[/yellow]")
            return
        
        # Convert results to table format
        table = Table(title=title)
        record = results[0]
        
        for key in record.keys():
            table.add_column(key.replace('_', ' ').title(), style="cyan")
        
        for record in results:
            table.add_row(*[str(record.get(key, '')) for key in record.keys()])
        
        console.print(table)
    
    def get_employee_graph_insights(self, emp_id):
        """
        Get comprehensive graph insights for an employee
        
        Returns:
        --------
        dict
            Employee insights including bottleneck score, bridge score, risk level, etc.
        """
        query = """
        MATCH (e:employee {emp_id: $emp_id})
        
        // Get skills count and ticket coverage
        OPTIONAL MATCH (e)-[:HAS_SKILL]->(s:skill)
        WITH e, COUNT(DISTINCT s) as skill_count, COLLECT(DISTINCT s.skill_name) as skill_names
        
        // For each skill, check if sole expert
        OPTIONAL MATCH (e)-[:HAS_SKILL]->(s:skill)<-[:HAS_SKILL]-(other:employee)
        WHERE other.emp_id <> e.emp_id
        WITH e, skill_count, skill_names, COUNT(DISTINCT s) as other_emp_skills
        
        // Calculate sole expert count
        WITH e, skill_count, skill_names, 
             (skill_count - COALESCE(other_emp_skills, 0)) as sole_expert_count
        
        // Calculate tickets dependent
        OPTIONAL MATCH (e)-[:HAS_SKILL]->(s:skill)<-[:REQUIRES_SKILL]-(t:ticket)
        
        RETURN
            e.emp_id as emp_id,
            e.name as name,
            e.department as department,
            skill_count as num_skills,
            sole_expert_count as sole_expert_in_skills,
            COUNT(DISTINCT t) as tickets_dependent,
            ROUND(100.0 * sole_expert_count / CASE WHEN skill_count = 0 THEN 1 ELSE skill_count END, 1) as bottleneck_score,
            skill_names as skills_list
        """
        
        return self.connector.run_query(query, {'emp_id': emp_id})
    
    def get_department_context(self, department):
        """
        Get department context and other departments' info
        
        Returns:
        --------
        dict
            Department information
        """
        query = """
        MATCH (e:employee {department: $department})
        WITH COLLECT(DISTINCT e.name) as dept_members, COUNT(e) as dept_size
        
        MATCH (other:employee)
        WHERE other.department <> $department
        WITH dept_members, dept_size, COLLECT(DISTINCT other.department) as other_depts
        
        RETURN
            dept_members,
            dept_size,
            other_depts
        """
        
        return self.connector.run_query(query, {'department': department})
    
    def get_ticket_complexity_analysis(self, ticket_id):
        """
        Analyze ticket complexity and coverage
        
        Returns:
        --------
        dict
            Ticket complexity metrics
        """
        query = """
        MATCH (t:ticket {ticket_id: $ticket_id})
        OPTIONAL MATCH (t)-[:REQUIRES_SKILL]->(s:skill)
        WITH t, COUNT(DISTINCT s) as skill_count, COLLECT(DISTINCT s.skill_name) as required_skills
        
        // For each skill, count how many employees have it
        OPTIONAL MATCH (t)-[:REQUIRES_SKILL]->(s:skill)<-[:HAS_SKILL]-(e:employee)
        
        RETURN
            t.ticket_id as ticket_id,
            t.customer_company as company,
            skill_count as total_skills_needed,
            COUNT(DISTINCT e) as employees_with_any_skill,
            required_skills as skill_list
        """
        
        return self.connector.run_query(query, {'ticket_id': ticket_id})

    def display_results_table(self, results, title="ผลลัพธ์"):
        """
        Display query results in a formatted table
        
        Parameters:
        -----------
        results : list
            Query results from Neo4j
        title : str
            Table title
        """
        if not results:
            console.print("[yellow]⚠️  ไม่พบผลลัพธ์[/yellow]")
            return
        
        table = Table(title=title, show_header=True, header_style="bold cyan")
        
        # Get column names from first record
        first_record = results[0]
        for key in first_record.keys():
            table.add_column(key, style="green")
        
        # Add rows
        for record in results:
            row = []
            for key in first_record.keys():
                value = record[key]
                # Format lists
                if isinstance(value, list):
                    row.append(", ".join(map(str, value)))
                else:
                    row.append(str(value))
            table.add_row(*row)
        
        console.print(table)


def main():
    """
    Interactive query builder
    """
    connector = get_neo4j_connector()
    
    if not connector.connect():
        return
    
    builder = CypherQueryBuilder(connector)
    
    while True:
        console.print("\n" + "="*70)
        console.print("[bold cyan]🔍 Cypher Query Builder[/bold cyan]")
        console.print("="*70)
        console.print("""
[bold]เลือกคำสั่ง:[/bold]
1. หาพนักงานตามทักษะ
2. ดูทักษะของพนักงาน
3. หาทิกเก็ตที่ต้องการทักษะ
4. หาพนักงานที่สามารถจัดการทิกเก็ต
5. ค้นหา Skill Hubs
6. ค้นหา Expert Employees
7. ดูสถิติกราฟ
0. ออก
        """)
        
        choice = input("\n📝 เลือก (0-7): ").strip()
        
        if choice == '0':
            break
        elif choice == '1':
            skill = input("ป้อนชื่อทักษะ: ").strip()
            results = builder.find_employees_by_skill(skill)
            builder.display_results_table(results, f"พนักงานที่มีทักษะ: {skill}")
        elif choice == '2':
            emp_id = input("ป้อน Employee ID: ").strip()
            results = builder.find_skills_for_employee(emp_id)
            builder.display_results_table(results, f"ทักษะของ {emp_id}")
        elif choice == '3':
            skill = input("ป้อนชื่อทักษะ: ").strip()
            results = builder.find_tickets_requiring_skill(skill)
            builder.display_results_table(results, f"ทิกเก็ตที่ต้อง: {skill}")
        elif choice == '4':
            ticket_id = input("ป้อน Ticket ID: ").strip()
            results = builder.find_employees_for_ticket(ticket_id)
            builder.display_results_table(results, f"พนักงานสำหรับ {ticket_id}")
        elif choice == '5':
            results = builder.find_skill_hubs()
            builder.display_results_table(results, "Skill Hubs (ทักษะที่หลายคนมี)")
        elif choice == '6':
            results = builder.find_expert_employees()
            builder.display_results_table(results, "Expert Employees (มีทักษะหลายด้าน)")
        elif choice == '7':
            results = builder.get_graph_statistics()
            if results:
                builder.display_results_table(results, "สถิติ Knowledge Graph")
    
    connector.disconnect()


if __name__ == "__main__":
    main()
