# 💰 FinanceAI: The Smart Way to Manage Your Money

<p align="center">
  <img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django" />
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white" alt="OpenAI" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License" />
</p>

---

## 🚀 Overview

**FinanceAI** is a state-of-the-art personal finance management platform designed to help users take full control of their financial life. By combining modern banking integrations with advanced AI insights, we transform complex financial data into actionable wisdom.

---

## ⚡ The Problem

Managing personal finances is often a chaotic and overwhelming task for many. Traditional methods suffer from:

*   **Fragmented Data**: Transactions spread across multiple bank accounts and wallets.
*   **Manual Entry Fatigue**: Spending hours logging every coffee or bill payment.
*   **Lack of Insights**: Raw numbers don't tell you *why* you're overspending or *how* to save better.
*   **Security Fears**: Concerns about data privacy and insecure authentication.
*   **Complexity**: Most tools are designed for accountants, not everyday people.

## 💡 The Solution

**FinanceAI** bridges the gap between raw data and financial freedom. Our solution provides:

*   **Centralized Hub**: View all your accounts, budgets, and goals in one unified dashboard.
*   **AI-Powered Insights**: Get personalized advice on spending patterns and saving strategies.
*   **Automated Tracking**: Effortless categorization of transactions using intelligent algorithms.
*   **Military-Grade Security**: Secure OAuth login (Google & Facebook) and 2FA/OTP verification.
*   **Goal-Oriented Planning**: Set and track financial milestones with real-time progress updates.

---

## 🛠️ The Tech Stack

| Category | Tools & Technologies |
| :--- | :--- |
| **Backend** | ![Django](https://img.shields.io/badge/Django-092E20?style=flat-square&logo=django&logoColor=white) ![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white) |
| **Frontend** | ![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white) ![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=flat-square&logo=css3&logoColor=white) ![JS](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black) |
| **AI/ML** | ![NLP](https://img.shields.io/badge/AI-Insight-8A2BE2) OpenAI API (Internal Integration) |
| **Database** | ![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white) (Dev) / PostgreSQL (Prod) |
| **Security** | ![allauth](https://img.shields.io/badge/OAuth-Google%20%26%20Facebook-blue) OTP/Email Verification |

---

## ✨ Key Features

- 🔐 **Secure Authentication**: Traditional login, Google OAuth, and Facebook integration.
- 🛡️ **Two-Step Verification**: Email-based OTP for enhanced security during signup and login.
- 📊 **Dynamic Dashboard**: Real-time visualization of your net worth, expenses, and budget status.
- 🧠 **AI Insights**: Generate personalized financial reports and tips based on your spending.
- 🎯 **Financial Goals**: Set targets for savings, vacations, or major purchases.
- 📅 **Budget Management**: Create monthly budgets and receive alerts when you're close to limits.
- 📱 **Fully Responsive**: Access your finances from any device—desktop, tablet, or mobile.

---

## 🔧 Installation & Setup

### 1. Prerequisites
Ensure you have Python 3.10+ installed on your system.

### 2. Clone and Prepare
```bash
# Clone the repository
git clone https://github.com/Annepuuday111/ai_powered_personal_finance_management.git
cd ai_powered_personal_finance_management

# Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configuration
Create a `.env` file in the root directory:
```env
SECRET_KEY=your_secret_key
DEBUG=True
GOOGLE_CLIENT_ID=your_id
GOOGLE_CLIENT_SECRET=your_secret
# ... other OAuth keys
```

### 5. Initialize Database
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

---

## 📖 How to Use

1.  **Launch the App**: Run `python manage.py runserver` and navigate to `http://127.0.0.1:8000`.
2.  **Sign Up/Login**:
    *   **Registration**: Create an account and verify your email via the instant **OTP (One-Time Password)** sent to your inbox.
    *   **Login**: Enter your credentials. For your security, a 6-digit verification code will be required to complete the sign-in.
    *   **OAuth**: Use Google or Facebook for lightning-fast, secure 1-click access.
3.  **Link Accounts**: Head to the **Bank Accounts** section to add your initial balances.
4.  **Set Budgets**: Use the **Budgets** tab to define category-wise monthly limits.
5.  **Track Transactions**: Log your income and expenses. The system automatically updates your net worth and budget progress.
6.  **Get AI Insights**: Visit the **AI Insights** page to receive personalized, AI-driven financial strategies.

---

## 🔒 Security Highlights

We prioritize your data security with a multi-layered defense system:
- **Two-Factor Authentication (2FA)**: Mandatory OTP verification for both login and signup.
- **Session Protection**: Intelligent session management to prevent unauthorized access.
- **Fail-Safe OTP**: Integrated "Resend OTP" functionality to ensure you're never locked out.
- **Encryption**: All sensitive data and passwords are cryptographically hashed and secured.

---

## 🤝 Contributing

We welcome contributions! Please feel free to submit a Pull Request.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

---

<p align="center">
  Made with ❤️ by the FinanceAI Team
</p>
