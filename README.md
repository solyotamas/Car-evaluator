# **Car Price Predictor**

---

##**Updates**
Updated weekly(ish) for new underpriced cars 

## **Introduction**
A deep learning project using regression **MLPS** to predict the prices of the cars which are available on the popular hungarian site Hasznaltautok.hu, trying to find underpriced ones


## **Project Structure**
- `analysis/` – analysis of important features and scalers with plots and charts for raw datasets
- `data/` – raw and clean datasets
- `modeling/` - neural network training & evaluation, model architecture
- `preprocessing/` – data cleaning, imputing, feature engineering and preprocessing functions
- `sql/` - SQL schemas
- `webscraper/` - scripts for collecting car data from Hasznaltautok.hu
- `workspace/` - experimental notebooks & temp files
- `evaluate_market_model` - seperate test environment for the latest model & dataset


## **Best Results**    

The best-performing model focuses on cars from 2010 onwards in the price range of 2M–50M HUF.
Achieving validation **MSE < 0.02**, validation MAPE ≈ 10.6% while maintaining between 10% - 11% MAPE on the test set.


## **Future Improvements**

- As noted in the notebooks, more frequent scraping of Hasznaltautok.hu is needed to gather sufficient, realistic car data. (The site lists around 500-1k new cars daily)
- Once enough data is collected, the model can be trained on inactive listings only and be used to predict prices for all active listings, catching potantial bargains instantly. 


## **Workflow**

**1. Data Gathering / Web Scraping**

Hasznaltautok.hu doesn't have an API or any easy way to download their data, so I wrote a scraper to get all the cars listings directly. 
I collected details like price, manufacturer, model, mileage, fuel type, etc. 

**2. Data Analysis**

- Explored the scraped data to understand the ranges of different features
- Spot possible errors or typos made by sellers
- Studied how each feature correlates with price using plots, keeping only those features which defined the value of the cars the closest

**3. Data Cleaning & Imputing & Preprocessing**

- Cleaned unreasonable or incorrect entries in the dataset
- Imputed missing values where appropriate to avoid losing useful data, also flagged where neccessary
- Standardized numerical features and target
- Prepared categorical features for future embeddings so they could be used in the neural network

**4. Modeling**

- Built neural networks (MLPs) for regression and experimented with different architectures
- Trained models with early stopping and learning rate scheduling to optimize performance
- Experimented with training models on specific price ranges while still covering majority of the market

**5. Evaluation**

- Evaluated model performance with metrics such as MSE, RMSE, MAE, MAPE 
- Visualized results with plots to better understand model behavior and where it fails exactly.
- Refined the model based on evaluation feedback
