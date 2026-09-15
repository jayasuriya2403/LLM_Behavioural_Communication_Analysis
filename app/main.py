from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from app.api.routes import router
from app.core.config import settings
from app.db.database import init_db


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Evidence-grounded behavioural and communication analysis of interview transcripts.",
)


@app.on_event("startup")
def startup():
    Path("data").mkdir(exist_ok=True)
    init_db()


app.include_router(router)


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!doctype html>
    <html>
    <head>
      <meta charset="utf-8">
      <title>Vellei Interview Assessment</title>
      <style>
        body{font-family:Arial,sans-serif;max-width:1000px;margin:40px auto;padding:0 20px}
        textarea{width:100%;min-height:330px;padding:12px;font-size:14px}
        button{padding:12px 18px;margin-top:12px;cursor:pointer}
        pre{background:#f5f5f5;padding:15px;overflow:auto}
        .links{margin:20px 0}
      </style>
    </head>
    <body>
      <h1>Vellei AI Interview Assessment</h1>
      <p>Paste a transcript and generate evidence-grounded candidate and recruiter reports.</p>
      <textarea id="transcript">Interviewer: Tell me about a challenging project you worked on.
Candidate: In my previous company, I worked on an e-commerce project. We had a performance problem. My task was to identify the bottleneck. I reviewed the logs, discussed it with the team, and implemented caching. The result was a faster response time and fewer complaints.

Interviewer: Tell me about a conflict with a colleague.
Candidate: We had a disagreement about priorities. I first listened to the concern, then compared the requirements and explained my reasoning. We agreed on a smaller first release and delivered it together.</textarea>
      <br>
      <button onclick="run()">Analyze Interview</button>
      <div id="status"></div>
      <pre id="output"></pre>
      <div id="links" class="links"></div>
      <script>
        async function run(){
          const status=document.getElementById('status');
          status.textContent='Analyzing...';
          document.getElementById('links').innerHTML='';
          const res=await fetch('/api/v1/analyze',{
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body:JSON.stringify({transcript:document.getElementById('transcript').value})
          });
          const data=await res.json();
          document.getElementById('output').textContent=JSON.stringify(data,null,2);
          if(data.analysis_id){
            document.getElementById('links').innerHTML =
              `<a target="_blank" href="/api/v1/analyses/${data.analysis_id}/candidate-report">Candidate Report</a>
               &nbsp; | &nbsp;
               <a target="_blank" href="/api/v1/analyses/${data.analysis_id}/recruiter-report">Recruiter Report</a>`;
          }
          status.textContent=res.ok?'Complete':'Error';
        }
      </script>
    </body>
    </html>
    """


@app.get("/health")
def health():
    return {"status": "ok", "service": settings.app_name}
