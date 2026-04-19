#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Neo4j Connection Manager for Enterprise Knowledge Graph
"""

from neo4j import GraphDatabase
from rich.console import Console
import os
from dotenv import load_dotenv

console = Console()

# Load environment variables
load_dotenv()

class Neo4jConnector:
    """
    Manages connection to Neo4j database
    """
    
    def __init__(self, uri=None, username=None, password=None):
        """
        Initialize Neo4j connection
        
        Parameters:
        -----------
        uri : str
            Neo4j connection URI (default from .env)
        username : str
            Neo4j username (default from .env)
        password : str
            Neo4j password (default from .env)
        """
        self.uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.username = username or os.getenv("NEO4J_USER", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD", "password")
        self.driver = None
        self.session = None
    
    def connect(self):
        """
        Establish connection to Neo4j
        
        Returns:
        --------
        bool
            True if connection successful, False otherwise
        """
        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.username, self.password),
                encrypted=False
            )
            # Verify connection
            self.driver.verify_connectivity()
            console.print("[green]✅ เชื่อมต่อ Neo4j สำเร็จ[/green]")
            return True
        except Exception as e:
            console.print(f"[red]❌ เชื่อมต่อ Neo4j ล้มเหลว: {e}[/red]")
            return False
    
    def disconnect(self):
        """
        Close connection to Neo4j
        """
        if self.driver:
            self.driver.close()
            console.print("[yellow]🔌 ปิดการเชื่อมต่อ Neo4j[/yellow]")
    
    def run_query(self, query, parameters=None):
        """
        Run Cypher query
        
        Parameters:
        -----------
        query : str
            Cypher query string
        parameters : dict
            Query parameters
        
        Returns:
        --------
        list
            Query results
        """
        if not self.driver:
            console.print("[red]❌ ยังไม่ได้เชื่อมต่อ Neo4j[/red]")
            return []
        
        try:
            with self.driver.session() as session:
                result = session.run(query, parameters or {})
                records = list(result)
                return records
        except Exception as e:
            console.print(f"[red]❌ เกิดข้อผิดพลาดในการรัน query: {e}[/red]")
            return []
    
    def clear_database(self):
        """
        Clear all data from database (for testing)
        """
        try:
            self.run_query("MATCH (n) DETACH DELETE n")
            console.print("[yellow]⚠️  ลบข้อมูลทั้งหมดจากฐานข้อมูล[/yellow]")
            return True
        except Exception as e:
            console.print(f"[red]❌ ไม่สามารถลบข้อมูล: {e}[/red]")
            return False


def get_neo4j_connector():
    """
    Get Neo4j connector instance
    
    Returns:
    --------
    Neo4jConnector
        Neo4j connector instance
    """
    return Neo4jConnector()


if __name__ == "__main__":
    # Test connection
    connector = get_neo4j_connector()
    if connector.connect():
        console.print("[cyan]🔍 ทดสอบการค้นหา nodes ทั้งหมด...[/cyan]")
        results = connector.run_query("MATCH (n) RETURN COUNT(n) as count")
        if results:
            for record in results:
                console.print(f"[green]จำนวน nodes ทั้งหมด: {record['count']}[/green]")
        connector.disconnect()
