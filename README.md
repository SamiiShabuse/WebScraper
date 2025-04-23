# 🕵️‍♂️ High School Teacher Web Scraper

This Python-based web scraper collects publicly available data about high school teachers near **Drexel University**. The goal is to extract and organize teacher names, emails, and subject information from local school websites, then export everything into an Excel sheet for easy use.

---

## 📌 Features

- 🌐 Searches Google for high schools near Drexel University using SerpAPI
- 🔍 Scans each school’s website for a staff directory
- 📥 Extracts:
  - Teacher names (guessed from email or parsed)
  - Email addresses
  - Subject taught (if available)
  - Source school website
- 📊 Outputs everything into a structured Excel file

---