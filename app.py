#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Flask Web Application for Enterprise Knowledge Graph
"""

from flask import Flask, render_template, request, jsonify
from neo4j_connector import get_neo4j_connector
from cypher_queries import CypherQueryBuilder
from graph_analyzer import GraphAnalyzer
import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, template_folder='templates', static_folder='static')

# Global connector
connector = None
query_builder = None
analyzer = None

def init_app():
    """Initialize app with database connection"""
    global connector, query_builder, analyzer
    connector = get_neo4j_connector()
    if connector.connect():
        query_builder = CypherQueryBuilder(connector)
        analyzer = GraphAnalyzer(connector)
        return True
    return False

@app.route('/')
def index():
    """Home page"""
    stats = None
    if query_builder:
        results = query_builder.get_graph_statistics()
        if results:
            stats = results[0]
    return render_template('index.html', stats=stats)

@app.route('/api/search-employee', methods=['POST'])
def search_employee():
    """Search employee by ID"""
    data = request.json
    emp_id = data.get('emp_id', '')
    
    if not emp_id:
        return jsonify({'error': 'Employee ID is required'}), 400
    
    results = query_builder.find_skills_for_employee(emp_id) or []
    
    if results:
        record = results[0]
        return jsonify({
            'emp_id': record.get('emp_id'),
            'name': record.get('name'),
            'department': record.get('department'),
            'skills': record.get('skills', []),
            'skill_count': record.get('skill_count')
        })
    else:
        return jsonify({'error': 'Employee not found'}), 404

@app.route('/api/search-skill', methods=['POST'])
def search_skill():
    """Search employees by skill"""
    data = request.json
    skill_name = data.get('skill_name', '')
    
    if not skill_name:
        return jsonify({'error': 'Skill name is required'}), 400
    
    results = query_builder.find_employees_by_skill(skill_name) or []
    
    employees = []
    for record in results:
        employees.append({
            'emp_id': record.get('emp_id'),
            'name': record.get('name'),
            'department': record.get('department'),
            'skills': record.get('skills', [])
        })
    
    return jsonify({'employees': employees})

@app.route('/api/search-ticket', methods=['POST'])
def search_ticket():
    """Search employees for ticket"""
    data = request.json
    ticket_id = data.get('ticket_id', '')
    
    if not ticket_id:
        return jsonify({'error': 'Ticket ID is required'}), 400
    
    results = query_builder.find_employees_for_ticket(ticket_id) or []
    
    employees = []
    for record in results:
        employees.append({
            'emp_id': record.get('emp_id'),
            'name': record.get('name'),
            'department': record.get('department'),
            'matching_skills': record.get('matching_skills'),
            'required_skills': record.get('required_skills'),
            'coverage': record.get('coverage')
        })
    
    return jsonify({'employees': employees})

@app.route('/api/analysis/bottlenecks')
def get_bottlenecks():
    """Get bottleneck skills"""
    results = analyzer.find_bottleneck_skills() or []
    
    bottlenecks = []
    for record in results:
        bottlenecks.append({
            'skill_id': record.get('skill_id'),
            'skill_name': record.get('skill_name'),
            'num_employees': record.get('num_employees'),
            'num_tickets': record.get('num_tickets'),
            'risk_score': record.get('risk_score')
        })
    
    return jsonify({'bottlenecks': bottlenecks})

@app.route('/api/analysis/critical')
def get_critical_bottlenecks():
    """Get critical bottleneck skills"""
    results = analyzer.find_critical_bottleneck_skills() or []
    
    critical = []
    for record in results:
        critical.append({
            'skill_name': record.get('skill_name'),
            'employee_name': record.get('sole_employee_name'),
            'employee_id': record.get('sole_employee_id'),
            'department': record.get('sole_employee_dept'),
            'tickets': record.get('num_critical_tickets')
        })
    
    return jsonify({'critical': critical})

@app.route('/api/analysis/bridges')
def get_bridges():
    """Get bridge employees"""
    results = analyzer.find_bridge_employees() or []
    
    bridges = []
    for record in results:
        bridges.append({
            'emp_id': record.get('emp_id'),
            'name': record.get('name'),
            'department': record.get('department'),
            'num_skills': record.get('num_skills'),
            'tickets_covered': record.get('tickets_covered'),
            'bridge_score': record.get('bridge_score')
        })
    
    return jsonify({'bridges': bridges})

@app.route('/api/analysis/high-demand')
def get_high_demand():
    """Get high demand skills"""
    results = analyzer.find_high_demand_skills() or []
    
    skills = []
    for record in results:
        skills.append({
            'skill_id': record.get('skill_id'),
            'skill_name': record.get('skill_name'),
            'num_tickets': record.get('num_tickets'),
            'num_employees': record.get('num_employees'),
            'availability': record.get('availability')
        })
    
    return jsonify({'skills': skills})

@app.route('/api/analysis/gaps')
def get_skill_gaps():
    """Get skill gaps"""
    results = analyzer.find_skill_gaps() or []
    
    gaps = []
    for record in results:
        gaps.append({
            'ticket_id': record.get('ticket_id'),
            'customer_company': record.get('customer_company'),
            'issue_description': record.get('issue_description'),
            'missing_skills': record.get('missing_skills', [])
        })
    
    return jsonify({'gaps': gaps})

@app.route('/api/analysis/departments')
def get_department_strengths():
    """Get department strengths"""
    results = analyzer.find_department_strengths() or []
    
    departments = []
    for record in results:
        top_skills = record.get('top_3_skills', [])
        skills = [{'skill': s.get('skill'), 'count': s.get('count')} for s in top_skills]
        departments.append({
            'department': record.get('department'),
            'top_skills': skills
        })
    
    return jsonify({'departments': departments})

@app.route('/dashboard')
def dashboard():
    """Analysis dashboard"""
    return render_template('dashboard.html')

@app.route('/query')
def query_page():
    """Query builder page"""
    return render_template('query.html')

@app.route('/list/employees')
def list_employees():
    """List all employees"""
    employees = []
    if query_builder:
        results = query_builder.get_all_employees() or []
        for record in results:
            employees.append({
                'emp_id': record.get('emp_id'),
                'name': record.get('name'),
                'department': record.get('department'),
                'skills': record.get('skills', []),
                'skill_count': record.get('skill_count', 0)
            })
    return render_template('list_employees.html', employees=employees)

@app.route('/list/skills')
def list_skills():
    """List all skills"""
    skills = []
    if query_builder:
        results = query_builder.get_all_skills() or []
        for record in results:
            skills.append({
                'skill_id': record.get('skill_id'),
                'skill_name': record.get('skill_name'),
                'num_employees': record.get('num_employees', 0),
                'num_tickets': record.get('num_tickets', 0)
            })
    return render_template('list_skills.html', skills=skills)

@app.route('/list/tickets')
def list_tickets():
    """List all tickets"""
    tickets = []
    if query_builder:
        results = query_builder.get_all_tickets() or []
        for record in results:
            tickets.append({
                'ticket_id': record.get('ticket_id'),
                'customer_company': record.get('customer_company'),
                'issue_description': record.get('issue_description'),
                'required_skills': record.get('required_skills', []),
                'skill_count': record.get('skill_count', 0)
            })
    return render_template('list_tickets.html', tickets=tickets)

def call_kku_genai(system_prompt, user_message):
    """
    Call KKU GenAI API for recommendations
    
    Parameters:
    -----------
    system_prompt : str
        System prompt for the AI
    user_message : str
        User message/question
    
    Returns:
    --------
    str
        AI response
    """
    try:
        api_key = os.getenv('KKU_GENAI_API_KEY', '')
        api_url = os.getenv('KKU_GENAI_API_URL', 'https://gen.ai.kku.ac.th/api/v1/chat/completions')
        
        if not api_key or api_key == 'your_kku_api_key_here':
            return "⚠️ KKU GenAI API key not configured. Please set KKU_GENAI_API_KEY in .env file"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        payload = {
            "model": "gemini-2.5-flash-lite",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "stream": False
        }
        
        response = requests.post(api_url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        return f"❌ AI Error: {str(e)}"

@app.route('/visualization')
def visualization():
    """Graph visualization page"""
    return render_template('visualization.html')

@app.route('/api/graph-data')
def get_graph_data():
    """Get graph data for visualization"""
    if query_builder:
        data = query_builder.get_graph_visualization_data()
        return jsonify(data)
    return jsonify({'nodes': [], 'edges': []})

@app.route('/api/tickets-list')
def get_tickets_list():
    """Get list of all tickets for selection"""
    tickets = []
    if query_builder:
        results = query_builder.get_all_tickets() or []
        for record in results:
            tickets.append({
                'ticket_id': record.get('ticket_id'),
                'customer_company': record.get('customer_company'),
                'issue_description': record.get('issue_description'),
                'skill_count': record.get('skill_count', 0)
            })
    return jsonify({'tickets': tickets})

@app.route('/recommendations')
def recommendations():
    """AI recommendations page"""
    return render_template('recommendations.html')

@app.route('/api/recommendations/employee-for-ticket', methods=['POST'])
def recommend_employee_for_ticket():
    """Get AI recommendation for best employee for a ticket"""
    data = request.json
    ticket_id = data.get('ticket_id', '')
    
    if not ticket_id:
        return jsonify({'error': 'Ticket ID required'}), 400
    
    if not query_builder:
        return jsonify({'error': 'Query builder not initialized'}), 500
    
    # Get ticket details
    ticket_query = f"""
    MATCH (t:ticket {{ticket_id: '{ticket_id}'}})
    OPTIONAL MATCH (t)-[:REQUIRES_SKILL]->(s:skill)
    RETURN t.customer_company as company, t.issue_description as description, 
           COLLECT(s.skill_name) as skills
    LIMIT 1
    """
    
    tickets = query_builder.connector.run_query(ticket_query) or []
    if not tickets:
        return jsonify({'error': 'Ticket not found'}), 404
    
    ticket_info = tickets[0]
    skills_needed = ', '.join(ticket_info.get('skills', []))
    
    # Get potential employees with basic info
    employees_query = f"""
    MATCH (e:employee)
    OPTIONAL MATCH (e)-[:HAS_SKILL]->(s:skill)
    RETURN e.name as name, e.emp_id as emp_id, e.department as dept,
           COLLECT(s.skill_name) as skills
    LIMIT 10
    """
    
    employees = query_builder.connector.run_query(employees_query) or []
    
    # Get graph insights for each employee
    employees_info = []
    graph_insights = []
    
    for emp in employees:
        emp_id = emp.get('emp_id')
        name = emp.get('name')
        dept = emp.get('dept')
        emp_skills = ', '.join(emp.get('skills', []))
        
        # Get employee insights
        insights_result = query_builder.get_employee_graph_insights(emp_id)
        if insights_result:
            insight = insights_result[0]
            bottleneck_score = insight.get('bottleneck_score', 0)
            sole_expert = insight.get('sole_expert_in_skills', 0)
            tickets_dependent = insight.get('tickets_dependent', 0)
            
            graph_insights.append(f"""
Employee: {name} ({emp_id})
- Department: {dept}
- Skills: {emp_skills}
- Bottleneck Score: {bottleneck_score}% (sole expert in {sole_expert} skills)
- Tickets Dependent on This Person: {tickets_dependent}
- Risk Level: {"🔴 CRITICAL" if bottleneck_score > 50 else "🟠 HIGH" if bottleneck_score > 25 else "🟡 MEDIUM" if bottleneck_score > 10 else "🟢 LOW"}
            """)
        
        employees_info.append(f"{name} ({dept}): {emp_skills}")
    
    employees_text = '\n'.join(employees_info)
    graph_context = ''.join(graph_insights)
    
    # Get department context
    if employees and employees[0].get('dept'):
        dept_context_result = query_builder.get_department_context(employees[0].get('dept'))
        if dept_context_result:
            dept_context = dept_context_result[0]
            dept_members = dept_context.get('department_members', [])
            other_depts = dept_context.get('neighboring_departments', [])
            dept_context_str = f"\nDepartment Context: {len(dept_members)} members in {employees[0].get('dept')}, can collaborate with: {', '.join(other_depts) if other_depts else 'None'}"
        else:
            dept_context_str = ""
    else:
        dept_context_str = ""
    
    # Get ticket complexity
    ticket_complexity_result = query_builder.get_ticket_complexity_analysis(ticket_id)
    if ticket_complexity_result:
        complexity = ticket_complexity_result[0]
        missing_skills = complexity.get('missing_skills_count', 0)
        skill_coverage = complexity.get('skill_coverage', [])
        complexity_str = f"\nTicket Complexity: {complexity.get('total_skills_needed', 0)} skills needed, {missing_skills} skills not covered by anyone"
    else:
        complexity_str = ""
    
    system_prompt = """You are an expert HR consultant analyzing team skills and project requirements using Knowledge Graph insights.
    Your recommendations must consider:
    1. Skill match quality (not just count)
    2. Bottleneck risk - don't overload critical people
    3. Organizational resilience - avoid single points of failure
    4. Career development opportunities
    5. Team dynamics and department collaboration
    
    Provide clear, data-driven recommendations balancing immediate project needs with organizational health."""
    
    user_message = f"""
=== TICKET ANALYSIS ===
Ticket: {ticket_id}
Company: {ticket_info.get('company')}
Description: {ticket_info.get('description')}
Required Skills: {skills_needed}
{complexity_str}

=== EMPLOYEE POOL WITH GRAPH INSIGHTS ===
{graph_context}

=== DEPARTMENT CONTEXT ===
{dept_context_str}

=== TASK ===
Based on the Graph Insights above (bottleneck scores, risk levels, ticket dependencies):
1. Recommend the BEST employee for this ticket
2. Explain why, considering both skill match AND organizational health
3. Highlight any risk factors (e.g., "WARNING: This person is already handling 12 critical tickets")
4. Suggest alternatives if the top choice poses risks
5. Recommend if outsourcing or team collaboration would be better

Provide response in Thai language. Format with clear sections.
    """
    
    recommendation = call_kku_genai(system_prompt, user_message)
    
    return jsonify({'recommendation': recommendation})

@app.route('/api/recommendations/team-for-ticket', methods=['POST'])
def recommend_team_for_ticket():
    """Get AI recommendation for best team composition for a ticket"""
    data = request.json
    ticket_id = data.get('ticket_id', '')
    
    if not ticket_id:
        return jsonify({'error': 'Ticket ID required'}), 400
    
    if not query_builder:
        return jsonify({'error': 'Query builder not initialized'}), 500
    
    # Get ticket details
    ticket_query = f"""
    MATCH (t:ticket {{ticket_id: '{ticket_id}'}})
    OPTIONAL MATCH (t)-[:REQUIRES_SKILL]->(s:skill)
    RETURN t.customer_company as company, t.issue_description as description, 
           COLLECT(s.skill_name) as skills
    LIMIT 1
    """
    
    tickets = query_builder.connector.run_query(ticket_query) or []
    if not tickets:
        return jsonify({'error': 'Ticket not found'}), 404
    
    ticket_info = tickets[0]
    skills_needed = ', '.join(ticket_info.get('skills', []))
    
    # Get all employees with skills
    employees_query = """
    MATCH (e:employee)
    OPTIONAL MATCH (e)-[:HAS_SKILL]->(s:skill)
    RETURN e.name as name, e.emp_id as emp_id, e.department as dept,
           COLLECT(s.skill_name) as skills
    """
    
    employees = query_builder.connector.run_query(employees_query) or []
    
    # Get graph insights for each employee
    graph_insights = []
    employees_info = []
    
    for emp in employees:
        emp_id = emp.get('emp_id')
        name = emp.get('name')
        dept = emp.get('dept')
        emp_skills = ', '.join(emp.get('skills', []))
        
        # Get employee insights
        insights_result = query_builder.get_employee_graph_insights(emp_id)
        if insights_result:
            insight = insights_result[0]
            bottleneck_score = insight.get('bottleneck_score', 0)
            sole_expert = insight.get('sole_expert_in_skills', 0)
            tickets_dependent = insight.get('tickets_dependent', 0)
            num_skills = insight.get('num_skills', 0)
            
            # Bridge score (inverse of bottleneck) - many skills = good bridge
            bridge_score = num_skills
            
            graph_insights.append(f"""
{name} ({emp_id}) - {dept}
  Skills: {emp_skills} ({num_skills} total)
  Bottleneck Risk: {bottleneck_score}% (sole expert in {sole_expert}/{num_skills} skills)
  Load: {tickets_dependent} tickets dependent
  Bridge Potential: {"⭐ EXCELLENT" if num_skills >= 4 else "⭐⭐ GOOD" if num_skills >= 2 else "⭐⭐⭐ LIMITED"}
  Risk Assessment: {"🔴 CRITICAL RESOURCE - DO NOT OVERLOAD" if bottleneck_score > 50 else "🟠 HIGH RISK" if bottleneck_score > 25 else "🟡 MANAGEABLE" if bottleneck_score > 10 else "🟢 GOOD AVAILABILITY"}
            """)
        
        employees_info.append(f"{name} ({dept}): {emp_skills}")
    
    employees_text = '\n'.join(employees_info)
    graph_context = ''.join(graph_insights)
    
    # Get ticket complexity
    ticket_complexity_result = query_builder.get_ticket_complexity_analysis(ticket_id)
    if ticket_complexity_result:
        complexity = ticket_complexity_result[0]
        missing_skills = complexity.get('missing_skills_count', 0)
        skill_coverage = complexity.get('skill_coverage', [])
        complexity_str = f"\nTicket Complexity: {complexity.get('total_skills_needed', 0)} skills needed, {missing_skills} skills not covered"
        
        coverage_details = "\nSkill Coverage Analysis:"
        for skill in skill_coverage:
            coverage_details += f"\n  - {skill.get('skill')}: {skill.get('available_employees', 0)} employee(s) available"
    else:
        complexity_str = ""
        coverage_details = ""
    
    system_prompt = """You are an expert HR consultant and team composition specialist with deep Knowledge Graph analysis capability.
    Your team recommendations must:
    1. Cover all required skills
    2. Balance skill diversity and complementary expertise
    3. AVOID creating new bottlenecks by overloading critical people
    4. Consider department diversity for better collaboration
    5. Optimize for team dynamics and knowledge sharing
    6. Minimize single points of failure
    
    Analyze bottleneck scores, load factors, and bridge potential carefully."""
    
    user_message = f"""
=== TICKET ANALYSIS ===
Ticket: {ticket_id}
Company: {ticket_info.get('company')}
Description: {ticket_info.get('description')}
Required Skills: {skills_needed}
{complexity_str}
{coverage_details}

=== EMPLOYEE POOL WITH GRAPH INSIGHTS ===
{graph_context}

=== TASK ===
Design an OPTIMAL TEAM (2-4 people) for this ticket considering:

1. **Skill Coverage**: Ensure all required skills are present
2. **Risk Mitigation**: Avoid people marked as "CRITICAL RESOURCE" unless absolutely necessary
3. **Team Balance**: Mix skills and bridge employees for knowledge transfer
4. **Department Diversity**: Include cross-functional collaboration when beneficial
5. **Load Distribution**: Don't concentrate high-risk people in one team

Please:
1. Recommend the ideal team composition
2. Explain the role of each member
3. List any risks and how to mitigate them
4. Suggest backup options if primary choices have constraints
5. Indicate if external hire/contractor is needed

Provide response in Thai language. Use clear structure with reasoning.
    """
    
    recommendation = call_kku_genai(system_prompt, user_message)
    
    return jsonify({'recommendation': recommendation})

@app.before_request
def before_request():
    """Initialize connection if not already done"""
    global connector, query_builder, analyzer
    if not connector or not connector.driver:
        init_app()

@app.teardown_appcontext
def teardown(exception):
    """Close connection only on app shutdown"""
    # Connection persists across requests, only close on shutdown
    pass

if __name__ == '__main__':
    if init_app():
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("❌ Failed to connect to Neo4j database")
