# Enterprise Knowledge Graph Project

ระบบ Enterprise Knowledge Graph สำหรับจัดการความรู้ทักษะของพนักงาน จับคู่คนกับงาน วิเคราะห์ความเสี่ยงด้านทรัพยากร และช่วยตัดสินใจด้วยข้อมูลเชิงกราฟร่วมกับ AI

## ภาพรวมโปรเจค

โปรเจคนี้ออกแบบมาเพื่อแก้ปัญหาที่พบบ่อยในองค์กร เช่น
- ไม่รู้ว่าใครมีทักษะอะไร
- งานสำคัญพึ่งพาคนเพียงไม่กี่คน (Single Point of Failure)
- จัดทีมให้เหมาะกับงานได้ยาก
- มองไม่เห็นภาพรวมช่องว่างทักษะ (Skill Gap) ของทั้งองค์กร

ระบบจะเก็บข้อมูลพนักงาน ทักษะ และทิกเก็ตงานในรูป Knowledge Graph (Neo4j) แล้วเปิดให้ค้นหา วิเคราะห์ และแนะนำการจัดสรรทรัพยากรผ่าน Web Application

## สิ่งที่ทำได้ในโปรเจคทั้งหมด

## 1) Data Pipeline (สร้างและเตรียมข้อมูล)

- สร้างข้อมูลจำลองแบบซับซ้อนด้วย AI
  - ไฟล์: generate_synthetic_data.py
  - สร้างพนักงาน/ทิกเก็ตที่มีลักษณะ Hub, Bottleneck, Bridge เพื่อนำไปวิเคราะห์เชิงโครงสร้าง

- แปลง JSON เป็น CSV สำหรับ Neo4j
  - ไฟล์: transform_json_to_csv.py
  - แปลงเป็น 5 ชุดข้อมูล: employee, skill, ticket, HAS_SKILL, REQUIRES_SKILL

- โหลด CSV เข้า Neo4j
  - ไฟล์: load_csv_to_neo4j.py
  - โหลด node และ relationship ครบทั้งกราฟ
  - มีตัวเลือกล้างข้อมูลเดิมก่อนโหลดใหม่

## 2) Query และการค้นหาเชิงปฏิบัติการ

- ค้นหาพนักงานด้วย Employee ID
- ค้นหาพนักงานจากชื่อทักษะ
- ค้นหาพนักงานที่เหมาะกับ Ticket พร้อมระดับความครอบคลุมทักษะ
- ดูรายการข้อมูลทั้งหมดของพนักงาน/ทักษะ/ทิกเก็ต

ใช้ผ่าน
- หน้าเว็บ query/list
- API ของ Flask
- Cypher Query Builder แบบ interactive ใน terminal

ไฟล์หลัก
- app.py
- cypher_queries.py

## 3) Graph Analytics เชิงลึก

ระบบวิเคราะห์โครงสร้างกราฟเพื่อหา insight สำคัญ

- Bottleneck Skills
  - ทักษะที่มีคนทำน้อยแต่งานต้องการมาก

- Critical Bottlenecks
  - ทักษะที่มีผู้เชี่ยวชาญเพียงคนเดียวแต่มีหลายงานที่ต้องพึ่งพา

- Bridge Employees
  - พนักงานที่เชื่อมหลายทักษะ/หลายบริบท ช่วยลดคอขวดของทีม

- High Demand Skills
  - ทักษะที่มีความต้องการสูงและสถานะความพร้อมของบุคลากร

- Skill Gaps
  - ทักษะที่ Ticket ต้องการแต่ยังไม่มีใครในองค์กรทำได้

- Department Strengths
  - ความเชี่ยวชาญเด่นของแต่ละแผนก (Top Skills)

ไฟล์หลัก
- graph_analyzer.py
- app.py

## 4) Interactive Graph Visualization

- แสดง Network ของ node และ edge ทั้งหมดแบบ interactive
- แยกสี node ตามประเภท employee/skill/ticket
- กดดูรายละเอียด node, จำนวน connection, fit view, reset layout

ไฟล์หลัก
- templates/visualization.html
- app.py (endpoint /api/graph-data)

## 5) AI Recommendations สำหรับการตัดสินใจ

มีหน้าแนะนำด้วย AI 2 โหมด
- Recommend Employee: แนะนำคนที่เหมาะที่สุดสำหรับ Ticket
- Recommend Team: แนะนำการจัดทีม 2-4 คนแบบสมดุล

AI จะอ้างอิงข้อมูลจากกราฟจริง เช่น
- ระดับ bottleneck risk
- จำนวนทักษะและภาระงานที่พึ่งพา
- ความซับซ้อนของ ticket
- บริบทแผนกและความร่วมมือข้ามทีม

ไฟล์หลัก
- app.py (endpoint /api/recommendations/*)
- templates/recommendations.html

## AI Data Flow (ส่งอะไรไปให้ LLM, มาจากไหน, และได้อะไรกลับมา)

เพื่อให้เห็นความโปร่งใสของระบบ AI ด้านล่างคือ flow จริงที่ใช้ในโค้ด

### A) AI Recommendations ใน Web App

จุดเริ่มต้น
- POST /api/recommendations/employee-for-ticket
- POST /api/recommendations/team-for-ticket

ข้อมูลที่นำไปประกอบ Prompt มาจากไหน
- จากผู้ใช้: `ticket_id` ที่ส่งมาใน request body
- จาก Neo4j (ผ่าน `query_builder.connector.run_query(...)`)
  - ข้อมูล ticket: company, description, required skills
  - ข้อมูลพนักงาน: emp_id, name, department, skills
- จาก Graph Insight methods
  - `get_employee_graph_insights(emp_id)`
    - bottleneck_score
    - sole_expert_in_skills
    - tickets_dependent
    - num_skills (ใช้ในโหมดแนะนำทีม)
  - `get_department_context(dept)`
    - สมาชิกในแผนก และแผนกที่เชื่อมโยง
  - `get_ticket_complexity_analysis(ticket_id)`
    - total_skills_needed
    - missing_skills_count
    - skill_coverage

ส่งอะไรไปให้ LLM
- เรียก `call_kku_genai(system_prompt, user_message)`
- API URL: `KKU_GENAI_API_URL` (default: `https://gen.ai.kku.ac.th/api/v1/chat/completions`)
- API Key: `KKU_GENAI_API_KEY`
- Payload ที่ส่ง

```json
{
  "model": "gemini-2.5-flash-lite",
  "messages": [
    {"role": "system", "content": "...แนวทางการวิเคราะห์..."},
    {"role": "user", "content": "...ข้อมูล ticket + employee graph insights + task..."}
  ],
  "stream": false
}
```

ได้ผลลัพธ์อะไรกลับมา
- ระบบรับ JSON response จาก KKU GenAI
- ดึงข้อความคำแนะนำจาก `result['choices'][0]['message']['content']`
- ส่งกลับหน้าเว็บในรูปแบบ

```json
{
  "recommendation": "...ข้อความแนะนำภาษาไทย..."
}
```

- หากเกิด error จะได้ข้อความในรูปแบบ `❌ AI Error: ...`

### B) AI สำหรับสร้าง Synthetic Data

จุดเริ่มต้น
- รัน `python generate_synthetic_data.py`

ส่งอะไรไปให้ LLM
- `generate_synthetic_data.py` สร้าง prompt ที่กำหนด schema JSON และ constraint ชัดเจน (จำนวนพนักงาน/ทิกเก็ต, hub, bottleneck, bridge)
- เรียก `call_api(user_message, show_details=False)` ใน `api_client.py`
- Payload ที่ส่งไป KKU GenAI

```json
{
  "model": "claude-sonnet-4.6",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "...prompt สร้าง synthetic graph data..."}
  ],
  "stream": false
}
```

- API Key ที่ใช้คือ `API_KEY` ในไฟล์ `.env`

ได้ผลลัพธ์อะไรกลับมา
- `call_api(...)` คืน response dict จาก API
- โค้ดดึง `choices[0].message.content` แล้ว clean markdown code fence (```json ... ```)
- parse ด้วย `json.loads(...)` ให้เป็น object
- บันทึกไฟล์เป็น `synthetic_knowledge_graph_data_2.json`
- ถ้า parse ไม่ได้ จะรายงาน `JSONDecodeError` พร้อมตัวอย่างเนื้อหาที่ตอบกลับเพื่อ debug

## 6) Web Dashboard ครบวงจร

หน้าเว็บที่มีในระบบ
- หน้าหลักสรุปสถิติกราฟ
- หน้าค้นหา (employee/skill/ticket)
- หน้า dashboard วิเคราะห์ความเสี่ยงและความต้องการทักษะ
- หน้า list สำหรับดูข้อมูลทั้งหมด
- หน้า visualization
- หน้า AI recommendations

ไฟล์หลัก
- templates/index.html
- templates/query.html
- templates/dashboard.html
- templates/list_employees.html
- templates/list_skills.html
- templates/list_tickets.html

## โมเดลข้อมูลในกราฟ

Node Types
- employee
- skill
- ticket

Relationships
- (employee)-[:HAS_SKILL]->(skill)
- (ticket)-[:REQUIRES_SKILL]->(skill)

แนวคิดนี้ทำให้วิเคราะห์ความสัมพันธ์แบบหลายชั้นได้ง่ายกว่าฐานข้อมูลแบบตารางทั่วไป

## โครงสร้างไฟล์สำคัญ

- app.py: Flask app และ API endpoints ทั้งหมด
- neo4j_connector.py: จัดการการเชื่อมต่อและรัน Cypher
- cypher_queries.py: query business logic สำหรับค้นหา/สรุปกราฟ
- graph_analyzer.py: วิเคราะห์ bottleneck/bridge/gap/high-demand
- load_csv_to_neo4j.py: โหลดข้อมูล CSV เข้าฐาน Neo4j
- transform_json_to_csv.py: แปลง JSON เป็น CSV สำหรับกราฟ
- generate_synthetic_data.py: สร้างข้อมูลจำลองด้วย AI
- api_client.py: utility เรียก KKU GenAI API
- templates/: หน้าเว็บทั้งหมด
- data/: ชุดข้อมูล CSV ที่พร้อมโหลด

## API Endpoints หลัก

Pages
- GET /
- GET /query
- GET /dashboard
- GET /list/employees
- GET /list/skills
- GET /list/tickets
- GET /visualization
- GET /recommendations

Search APIs
- POST /api/search-employee
- POST /api/search-skill
- POST /api/search-ticket

Analysis APIs
- GET /api/analysis/bottlenecks
- GET /api/analysis/critical
- GET /api/analysis/bridges
- GET /api/analysis/high-demand
- GET /api/analysis/gaps
- GET /api/analysis/departments

Graph/Recommendation APIs
- GET /api/graph-data
- GET /api/tickets-list
- POST /api/recommendations/employee-for-ticket
- POST /api/recommendations/team-for-ticket

## วิธีติดตั้งและเริ่มใช้งาน

## 1) เตรียมเครื่องมือ

- Python 3.10+
- Neo4j 4.x หรือ 5.x

## 2) ติดตั้ง dependencies

```bash
python -m venv .venv
.venv\Scripts\activate
pip install flask neo4j pandas requests python-dotenv rich
```

## 3) ตั้งค่าไฟล์ .env

สร้างไฟล์ .env ที่ root project

```env
# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# ใช้กับ api_client.py / generate_synthetic_data.py
API_KEY=your_kku_genai_api_key

# ใช้กับหน้า Recommendations ในเว็บ
KKU_GENAI_API_KEY=your_kku_genai_api_key
KKU_GENAI_API_URL=https://gen.ai.kku.ac.th/api/v1/chat/completions
```

## 4) เตรียมข้อมูล

ทางเลือก A: ใช้ข้อมูลตัวอย่างที่อยู่ในโฟลเดอร์ data ได้ทันที

ทางเลือก B: สร้างข้อมูลใหม่

```bash
python generate_synthetic_data.py
python transform_json_to_csv.py
```

หมายเหตุ
- transform_json_to_csv.py จะสร้างไฟล์ CSV ที่ root ของโปรเจค
- หากต้องการใช้ loader ค่า default ให้นำไฟล์ CSV ที่สร้างใหม่ไปไว้ในโฟลเดอร์ data

## 5) โหลดข้อมูลเข้า Neo4j

```bash
python load_csv_to_neo4j.py
```

## 6) รัน Web Application

```bash
python app.py
```

เปิดใช้งานที่
- http://localhost:5000

## 7) (ทางเลือก) รันโหมดวิเคราะห์ผ่าน terminal

```bash
python graph_analyzer.py
python cypher_queries.py
```

## ประโยชน์ของโปรเจค

## เชิงธุรกิจ

- ลดความเสี่ยงจากการพึ่งพาคนเก่งคนเดียว
- วางแผนจ้างงานและอัปสกิลจากข้อมูลจริง
- จัดสรรคนให้เหมาะกับงานได้เร็วขึ้น
- เพิ่มความต่อเนื่องของการส่งมอบงานให้ลูกค้า

## เชิงบริหารทีม

- เห็นภาพความเชี่ยวชาญของแต่ละแผนกอย่างเป็นระบบ
- ออกแบบทีมข้ามสายงานได้ดีขึ้น
- ใช้ bridge employee อย่างมีแผน ลดงานคอขวด

## เชิงเทคนิคและข้อมูล

- ใช้กราฟสำหรับวิเคราะห์ความสัมพันธ์ซับซ้อนได้ตรงจุด
- มีทั้ง API และ UI พร้อมใช้งานต่อยอด
- เชื่อม AI เข้ากับข้อมูลกราฟเพื่อสร้างคำแนะนำเชิงบริบท

## ตัวอย่างการนำไปใช้งาน

- ทีม PMO ใช้ดูว่าทิกเก็ตใหม่ควร assign ให้ใคร
- ทีม HR ใช้หา skill gap เพื่อวางแผนอบรมรายไตรมาส
- ทีมผู้บริหารใช้ dashboard ติดตามความเสี่ยงเชิงบุคลากร
- ทีม Technical Lead ใช้ visualization เพื่อวิเคราะห์ dependency ของทักษะ

## Troubleshooting แบบย่อ

- เชื่อม Neo4j ไม่ได้
  - ตรวจสอบ NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD ใน .env
  - ตรวจสอบว่า Neo4j service ทำงานอยู่จริง

- หน้า Recommendations ใช้งานไม่ได้
  - ตรวจสอบ KKU_GENAI_API_KEY ใน .env
  - ตรวจสอบว่า endpoint API ภายนอกเข้าถึงได้

- โหลด CSV ไม่เข้า
  - ตรวจสอบว่าไฟล์อยู่ในโฟลเดอร์ data และชื่อไฟล์ตรงตามที่ loader ใช้

## แนวทางพัฒนาต่อ

- เพิ่มระบบ authentication/authorization
- เพิ่มการจัดการระดับความชำนาญทักษะ (proficiency level)
- เพิ่มการวิเคราะห์เชิงเวลา เช่น trend ความต้องการทักษะรายเดือน
- เพิ่ม test suite และ CI pipeline สำหรับ production readiness

## License

Internal / Internship Project