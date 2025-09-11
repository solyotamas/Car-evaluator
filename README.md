# **Car Price Predictor**

---

## **Introduction**
A deep learning project using **neural networks** to predict the prices of the cars available on the popular hungarian site Hasznaltautok.hu - aiming to find undervalued cars & good deals

## **Workflow**

**1. Data Gathering / Web Scraping**

Hasznaltautok.hu doesn't have an API or any easy way to download their data, so I wrote a scraper to get all the cars listings directly. 
I collected details like price, manufacturer, model, mileage, fuel type, etc. 

**2. Data Analysis**

Explored the scraped data to see different ranges of the features, possible errors the sellers might have mistyped, and feature correlation with price with plots & charts.


## **Project Structure**
- `analysis/` – analysis of important features and scalers with plots and charts for raw datasets
- `data/` – raw and clean datasets
- `modeling/` - neural network training & evaluation, model architecture
- `preprocessing/` – data cleaning, imputing, feature engineering and preprocessing functions
- `sql/` - SQL schemas
- `webscraper/` - scripts for collecting car data from Hasznaltautok.hu
- `workspace/` - experimental notebooks & temp files
- `evaluate_market_model` - seperate test environment for the latest model & dataset

    
## **Setup & Usage**


## **Future Improvements**

