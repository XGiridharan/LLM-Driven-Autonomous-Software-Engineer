from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI(title="🧠 Demo Blog - LLM Autonomous Engineer")

@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🧠 LLM Autonomous Software Engineer Demo</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .header { text-align: center; color: #667eea; }
            .demo-box { background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }
            .feature { margin: 10px 0; }
            .success { color: #28a745; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🧠 LLM Autonomous Software Engineer</h1>
            <h2>Working Demo Application</h2>
        </div>
        
        <div class="demo-box">
            <h3>🎉 Successfully Built!</h3>
            <p>Your AI-powered development system has created this working application.</p>
        </div>
        
        <div class="demo-box">
            <h3>🚀 What Your AI Can Build:</h3>
            <div class="feature">✅ FastAPI backend applications</div>
            <div class="feature">✅ Database models and migrations</div>
            <div class="feature">✅ User authentication systems</div>
            <div class="feature">✅ RESTful API endpoints</div>
            <div class="feature">✅ Beautiful web interfaces</div>
            <div class="feature">✅ Complete CRUD operations</div>
            <div class="feature">✅ Security and validation</div>
        </div>
        
        <div class="demo-box">
            <h3>🔧 Technical Capabilities:</h3>
            <div class="feature">• FastAPI framework</div>
            <div class="feature">• SQLAlchemy ORM</div>
            <div class="feature">• JWT authentication</div>
            <div class="feature">• Pydantic validation</div>
            <div class="feature">• Modern HTML/CSS/JS</div>
            <div class="feature">• Database management</div>
        </div>
        
        <div class="demo-box">
            <h3>🎯 Your Dashboard:</h3>
            <p>Access your LLM Autonomous Software Engineer dashboard at:</p>
            <p><strong>http://localhost:9000</strong></p>
            <p>There you can build any application you want!</p>
        </div>
    </body>
    </html>
    