# 📊 Secure AI Copilot with Fine-Grained Authorization

## 📌 Overview

An internal AI-powered assistant (Copilot) for enterprise environments that interacts with business-critical data systems — CRM, HR, and Financial databases — while enforcing **granular, dynamic, and secure data access controls** at every stage.

## 📊 Data Schema

**Tables:**

- `users` (id, name, email, phone, role)
- `customers` (id, name, email, phone, budget, address, assigned_emp_id)
- `hr_data` (id, emp_id, designation, salary, benefits, department)
- `financial_data` (id, vendor_name, amount, txn_date, notes)

---

## 📌 Why This Project

- AI copilots are becoming integral to internal enterprise tools
- Traditional RBAC isn’t enough for AI-generated dynamic content
- We demonstrate **secure AI data operations** combining RBAC, ABAC, RAG filtering, and AI response enforcement — enterprise-ready and compliance-friendly

---
