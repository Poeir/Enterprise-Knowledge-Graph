# 🏢 Enterprise Knowledge Graph System

ระบบการจัดการกราฟความรู้องค์กร (Enterprise Knowledge Graph) ที่ช่วยในการวิเคราะห์และจัดสรรพนักงานตามทักษะที่มี

## ✨ ฟีเจอร์หลัก

- **🔍 ค้นหาพนักงาน** - ค้นหาพนักงานตามหมายเลข ID หรือทักษะ
- **📊 วิเคราะห์กราฟ** - ค้นหา Bottleneck Skills, Bridge Employees, Skill Gaps
- **🎯 จัดสรรทรัพยากร** - หา Employee ที่เหมาะสมสำหรับทิกเก็ต
- **📈 สถิติกำลังงาน** - ดูข้อมูลทักษะ ภาค และพนักงาน
- **🌐 Web Interface** - หน้าเว็บสวยงามและใช้งานง่าย

## 📦 ส่วนประกอบ

```
project/
├── api_client.py              # เชื่อมต่อกับ KKU AI API
├── generate_synthetic_data.py # สร้างข้อมูลจำลอง
├── transform_json_to_csv.py   # แปลง JSON เป็น CSV
├── neo4j_connector.py         # เชื่อมต่อ Neo4j Database
├── load_csv_to_neo4j.py       # โหลด CSV เข้า Neo4j
├── cypher_queries.py          # Query Builder สำหรับ Neo4j
├── graph_analyzer.py          # วิเคราะห์ Knowledge Graph
├── app.py                     # Flask Web Application
├── data/                      # ข้อมูล CSV
│   ├── nodes_employee.csv
│   ├── nodes_skill.csv
│   ├── nodes_ticket.csv
│   ├── edges_has_skill.csv
│   └── edges_requires_skill.csv
├── templates/                 # HTML Templates
│   ├── index.html
│   ├── query.html
│   └── dashboard.html
└── static/                    # Static files (CSS, JS)
```

## 🚀 ขั้นตอนการใช้งาน

### 1. ติดตั้ง Dependencies

```bash
# สร้าง virtual environment
python -m venv .venv
.venv\Scripts\activate

# ติดตั้ง packages
pip install neo4j flask requests python-dotenv rich pandas
```

### 2. ตั้งค่า Neo4j Database

```bash
# ติดตั้ง Neo4j (ใช้ Neo4j Desktop หรือ Docker)
# Docker example:
docker run -d \
  -p 7474:7474 \
  -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest
```

### 3. ตั้งค่า Environment Variables

สร้างไฟล์ `.env` ในโปรเจกต์:

```env
# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# API Configuration (ถ้าใช้)
API_KEY=your_api_key_here
```

### 4. สร้างข้อมูลจำลอง (ถ้ายังไม่มี)

```bash
# สร้างข้อมูล JSON จาก AI API
python generate_synthetic_data.py

# แปลง JSON เป็น CSV
python transform_json_to_csv.py
```

### 5. โหลดข้อมูลเข้า Neo4j

```bash
# โหลด CSV files เข้า Neo4j
python load_csv_to_neo4j.py
```

### 6. เรียกใช้ Web Application

```bash
# เริ่มเซิร์ฟเวอร์
python app.py

# เปิดบ้านเว็บ
# http://localhost:5000
```

## 📖 การใช้งาน

### หน้าหลัก
- แสดงสถิติกราฟทั่วไป (พนักงาน, ทักษะ, ทิกเก็ต)
- ลิงก์ไปยังหน้าค้นหาและวิเคราะห์

### ค้นหา (Search)
- **ค้นหาพนักงาน** - ใส่ Employee ID เช่น `EMP001`
- **ค้นหาตามทักษะ** - ใส่ชื่อทักษะ เช่น `Python`
- **หาพนักงานสำหรับทิกเก็ต** - ใส่ Ticket ID เช่น `TKT001`

### วิเคราะห์ (Dashboard)
1. **Critical Bottlenecks** 🚨 - ทักษะที่มีคนเดียว และต้องเยอะ
2. **Bottleneck Skills** ⚠️ - ทักษะที่เสี่ยง (คนน้อย ต้องเยอะ)
3. **Bridge Employees** 🌉 - พนักงานที่เชื่อมต่อระหว่างกลุ่ม
4. **High Demand Skills** 📈 - ทักษะที่มีความต้องการสูง
5. **Skill Gaps** ❌ - ทักษะที่ไม่มีใครมี แต่ต้องการ
6. **Department Strengths** 🏢 - ความเชี่ยวชาญของแต่ละแผนก

## 📊 ตัวอย่างการ Query

### Cypher Query Builder

```bash
# เรียกใช้ interactive query builder
python cypher_queries.py
```

ตัวอย่าง Query:
```cypher
# หา employees ที่มีทักษะ Python
MATCH (e:employee)-[:HAS_SKILL]->(s:skill {skill_name: 'Python'})
RETURN e.name, e.department

# หา bottleneck skills
MATCH (e:employee)-[:HAS_SKILL]->(s:skill)
WITH s, COUNT(DISTINCT e) as emp_count
WHERE emp_count <= 1
RETURN s.skill_name, emp_count
```

### Graph Analyzer

```bash
# เรียกใช้ analysis
python graph_analyzer.py
```

## 🔧 Configuration

### Neo4j Connection
ปรับได้ใน `.env`:
```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
```

### Flask Server
ปรับได้ใน `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

## 📝 API Endpoints

- `GET /` - หน้าหลัก
- `GET /query` - หน้าค้นหา
- `GET /dashboard` - หน้าวิเคราะห์
- `POST /api/search-employee` - ค้นหาพนักงาน
- `POST /api/search-skill` - ค้นหาตามทักษะ
- `POST /api/search-ticket` - ค้นหาพนักงานสำหรับทิกเก็ต
- `GET /api/analysis/bottlenecks` - Bottleneck Skills
- `GET /api/analysis/critical` - Critical Bottlenecks
- `GET /api/analysis/bridges` - Bridge Employees
- `GET /api/analysis/high-demand` - High Demand Skills
- `GET /api/analysis/gaps` - Skill Gaps
- `GET /api/analysis/departments` - Department Strengths

## 🛠️ Troubleshooting

### ปัญหา: ไม่สามารถเชื่อมต่อ Neo4j
```bash
# ตรวจสอบว่า Neo4j running
docker ps

# ตรวจสอบ connection settings
# ใน .env ให้ตรงกับการตั้งค่า Neo4j
```

### ปัญหา: CSV ไม่โหลดเข้า
```bash
# ตรวจสอบว่า CSV files อยู่ในโฟลเดอร์ data/
# ลองลบข้อมูลเดิมแล้วโหลดใหม่
python load_csv_to_neo4j.py
```

### ปัญหา: Flask server ไม่เริ่ม
```bash
# ตรวจสอบ port 5000 ว่างหรือไม่
netstat -an | findstr :5000

# ใช้ port อื่นถ้า 5000 ใช้ไป
python app.py  # แล้วเปลี่ยน port ใน app.py
```

## 📚 หมายเหตุ

- ระบบสมมติว่าข้อมูล CSV มีโครงสร้างถูกต้อง
- จำนวน nodes ใหญ่อาจต้องเวลาในการโหลด
- ต้องใช้ Neo4j version 4.0 ขึ้นไป

## 📄 License

Internal Project

## 👨‍💼 Support

สำหรับคำถามหรือปัญหา ติดต่อ Project Owner

---

**🎉 ระบบพร้อมใช้งาน!**
