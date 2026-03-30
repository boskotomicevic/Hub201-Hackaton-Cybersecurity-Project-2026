For testing you can use:

```shell
npx web-ext run -t chromium
```
this will run a clean chromium browser with your extension uploaded


Some important elements you can target on gmail:

```javascript
const senderElement = row.querySelector('.zF, [email]');
const senderEmail = senderElement?.getAttribute('email') || "";
const subject = row.querySelector('.bog')?.innerText || "";
const domain = senderEmail.split('@')[1] || "";
const dateContainer = row.querySelector('.xW span[title]');
const fullTimestamp = dateContainer?.getAttribute('title') || ""; // "сре, 18. феб 2026. 11:58"
const shortDate = dateContainer?.innerText || ""; // "18. феб"
```


[Processed Mails]
[{
    
"mail_ID":"senderEmail+fullTimestamp",
"score":0
        
}]

Verified mail

{
    "domain":"discord.com",
    "score":10
}

## 🚀 Running the Backend

### 1️⃣ Install dependencies

```bash
pip install -r requirements.txt

### 2️⃣ Run FastAPI server
uvicorn app.main:app --reload

### Build Image
docker build -t intday-backend .

### Run Container
docker run -p 8000:8000 intday-backend

### Run Fullstack
docker-compose up --build
