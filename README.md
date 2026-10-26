<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:FF6B6B,35:FFA94D,70:4DABF7,100:845EF7&height=200&section=header&text=FinanceAI&fontSize=44&fontColor=ffffff&fontAlignY=36&animation=fadeIn&desc=AI-Powered%20Personal%20Finance%20Manager&descSize=16&descAlignY=58" width="100%"/>

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=22&pause=1000&color=845EF7&center=true&vCenter=true&width=700&lines=Track+accounts%2C+transactions+%26+budgets;Set+goals+and+watch+your+progress;Get+smart+insights+on+your+spending;Chat+with+a+Groq-powered+finance+assistant" alt="Typing SVG"/>

<br/>

<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
<img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django"/>
<img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL"/>
<img src="https://img.shields.io/badge/Groq-F55036?style=for-the-badge&logoColor=white" alt="Groq"/>
<img src="https://img.shields.io/badge/Chart.js-FF6384?style=for-the-badge&logo=chartdotjs&logoColor=white" alt="Chart.js"/>
<img src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white" alt="HTML5"/>
<img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white" alt="CSS3"/>
<img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" alt="JavaScript"/>

<br/>

<img src="https://img.shields.io/badge/Status-Active-20C997?style=for-the-badge" alt="Status"/>
<img src="https://img.shields.io/github/stars/Annepuuday111/AI-Personal-Finance-Manager?style=for-the-badge&color=845EF7" alt="Stars"/>
<img src="https://img.shields.io/github/last-commit/Annepuuday111/AI-Personal-Finance-Manager?style=for-the-badge&color=4DABF7" alt="Last Commit"/>
<img src="https://img.shields.io/github/repo-size/Annepuuday111/AI-Personal-Finance-Manager?style=for-the-badge&color=FF6B6B" alt="Repo Size"/>

<br/><br/>

[About](#-about) • [Features](#-features) • [Tech Stack](#️-tech-stack) • [Project Structure](#-project-structure) • [Getting Started](#-getting-started) • [Roadmap](#️-roadmap) • [Author](#-author)

</div>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%">

## 📖 About

**FinanceAI** is a Django web application for managing personal finances in one place. Users sign up with email (verified by a one-time password) or via Google / Facebook, then track bank accounts, income and expenses, category budgets and savings goals. A built-in insights engine analyses spending and budget health, and a chat assistant powered by **Groq** (`llama-3.1-8b-instant`) answers personal-finance questions.

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%">

## ✨ Features

| | Feature |
| :---: | :--- |
| 🔐 | **Authentication** with `django-allauth` – email login plus Google and Facebook OAuth |
| 🛡️ | **Email OTP verification** – 6-digit codes on signup and login, with expiry and a resend option |
| 🏦 | **Bank accounts** – checking, savings, credit card, investment and cash accounts with balances |
| 💸 | **Transactions** – income / expense / transfer entries with categories, notes, tags, receipts and recurring flags |
| 🗂️ | **Custom categories** – income and expense categories with icon, colour and optional budget limit |
| 📅 | **Budgets** – weekly / monthly / yearly budgets with configurable alert thresholds |
| 🎯 | **Financial goals** – target amount, deadline and progress updates |
| 📊 | **Dashboard & analytics** – income vs. expense trends and category breakdowns with Chart.js |
| 🧠 | **Insights engine** – spending patterns, saving opportunities, budget health, expense predictions and recommendations |
| 📰 | **Finance news insights** – Google News RSS headlines turned into insights (`fetch_google_news` command) |
| 🔔 | **Notifications** – transaction, budget, goal, low-balance and milestone alerts with read / read-all |
| 💬 | **AI chat assistant** – personalised finance Q&A via the Groq API |

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%">

## 🛠️ Tech Stack

<div align="center">

<img src="https://skillicons.dev/icons?i=python,django,postgres,html,css,js&theme=light" alt="Tech icons"/>

</div>

| Layer | Technology |
| :--- | :--- |
| **Backend** | ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) ![Django](https://img.shields.io/badge/Django%204.2-092E20?style=for-the-badge&logo=django&logoColor=white) |
| **Database** | ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white) (`psycopg2-binary`) |
| **Auth** | ![allauth](https://img.shields.io/badge/django--allauth-092E20?style=for-the-badge&logo=django&logoColor=white) ![Google](https://img.shields.io/badge/Google%20OAuth-4285F4?style=for-the-badge&logo=google&logoColor=white) ![Facebook](https://img.shields.io/badge/Facebook%20OAuth-0866FF?style=for-the-badge&logo=facebook&logoColor=white) |
| **AI Chat** | ![Groq](https://img.shields.io/badge/Groq%20·%20Llama%203.1-F55036?style=for-the-badge&logoColor=white) |
| **Frontend** | ![Django Templates](https://img.shields.io/badge/Django%20Templates-092E20?style=for-the-badge&logo=django&logoColor=white) ![Chart.js](https://img.shields.io/badge/Chart.js-FF6384?style=for-the-badge&logo=chartdotjs&logoColor=white) ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black) |
| **Utilities** | `python-decouple`, `python-dotenv`, `feedparser`, `requests`, `Pillow` |

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%">

## 📂 Project Structure

```text
AI-Personal-Finance-Manager/
├── accounts/                     # Core finance app
│   ├── management/commands/
│   │   └── fetch_google_news.py  # Creates news-based insights for all users
│   ├── migrations/
│   ├── templatetags/
│   ├── ai_service.py             # Insights engine (AIFinanceAnalyzer)
│   ├── notification_service.py   # Alerts & notifications
│   ├── signals.py                # Profile / welcome hooks on user creation
│   ├── forms.py
│   ├── models.py                 # Profile, Category, BankAccount, Transaction, Budget,
│   │                             # FinancialGoal, AIInsight, Notification, EmailOTP ...
│   ├── urls.py
│   └── views.py                  # Dashboard, CRUD views, OTP login/signup
├── chat/                         # Groq-powered chat assistant
│   ├── urls.py
│   └── views.py
├── financeai/                    # Project settings & root URLs
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── templates/
│   ├── account/                  # Landing, login, signup, OTP pages
│   ├── accounts/                 # Dashboard, transactions, budgets, goals, analytics ...
│   └── chat/
├── manage.py
└── requirements.txt
```

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%">

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL running locally (or reachable via the `DB_*` settings)
- A [Groq API key](https://console.groq.com/) for the chat assistant
- A Gmail / SMTP account with an app password for OTP emails

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Annepuuday111/AI-Personal-Finance-Manager.git
   cd AI-Personal-Finance-Manager
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate      # macOS / Linux
   # venv\Scripts\activate       # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create the database**
   ```bash
   createdb financeai_db
   ```

5. **Create a `.env` file** in the project root (next to `manage.py`)
   ```env
   DEBUG=True

   DB_NAME=financeai_db
   DB_USER=postgres
   DB_PASSWORD=your_db_password
   DB_HOST=localhost
   DB_PORT=5432

   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_HOST_USER=your_email@gmail.com
   EMAIL_HOST_PASSWORD=your_app_password
   DEFAULT_FROM_EMAIL=FinanceAI <your_email@gmail.com>

   GROQ_API_KEY=your_groq_api_key
   ```

6. **Run migrations and create an admin user**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

7. **(Optional) Enable Google / Facebook login** – in the Django admin (`/admin/`), set the *Site* domain and add a *Social application* for each provider with your OAuth client ID and secret.

8. **Start the server**
   ```bash
   python manage.py runserver
   ```
   Open http://127.0.0.1:8000

9. **(Optional) Pull finance news into insights**
   ```bash
   python manage.py fetch_google_news --max 8
   ```

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%">

## 🗺️ Roadmap

- [x] OTP-verified email signup & login
- [x] Accounts, transactions, budgets, goals & analytics
- [x] Groq-powered chat assistant
- [ ] Live market-data integration for stock and interest-rate insights
- [ ] Load all secrets from environment variables
- [ ] REST API for a mobile client

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%">

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push the branch: `git push origin feature/your-feature`
5. Open a Pull Request

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%">

## 👨‍💻 Author

<div align="center">

### Annepu Uday Kumar

<a href="https://github.com/Annepuuday111"><img src="https://img.shields.io/badge/GitHub-Annepuuday111-845EF7?style=for-the-badge&logo=github&logoColor=white" alt="GitHub"/></a>
<a href="https://annepuudaykumar.netlify.app"><img src="https://img.shields.io/badge/Portfolio-Visit-FF6B6B?style=for-the-badge&logo=netlify&logoColor=white" alt="Portfolio"/></a>

</div>

<br/>

<div align="center">⭐ If you like this project, give it a star!</div>

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:845EF7,35:4DABF7,70:FFA94D,100:FF6B6B&height=120&section=footer" width="100%"/>
