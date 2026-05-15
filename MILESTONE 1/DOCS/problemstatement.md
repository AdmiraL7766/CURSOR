# Problem Statement: AI-Powered Restaurant Recommendation System (Zomato Use Case)

Build an AI-powered restaurant recommendation service inspired by Zomato. The system should suggest restaurants intelligently by combining structured restaurant data with a Large Language Model (LLM), based on each user's preferences.

## Objective

Design and implement an application that:

- Accepts user preferences (location, budget, cuisine, rating, etc.).
- Uses a real-world restaurant dataset.
- Leverages an LLM to generate personalized, human-like recommendations.
- Presents results clearly in a useful, user-friendly format.

## System Workflow

### 1) Data Ingestion

- Load and preprocess the Zomato dataset from Hugging Face:  
  [https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation)
- Extract relevant attributes such as:
  - Restaurant name
  - Location
  - Cuisine
  - Cost
  - Rating

### 2) User Input

Collect user preferences, including:

- Location (for example, Delhi or Bangalore)
- Budget range (low, medium, high)
- Preferred cuisine (for example, Italian or Chinese)
- Minimum acceptable rating
- Additional constraints (for example, family-friendly, quick service)

### 3) Integration Layer

- Filter and prepare candidate restaurants based on user inputs.
- Pass structured candidate data into an LLM prompt.
- Design the prompt so the LLM can reason over options and rank them meaningfully.

### 4) Recommendation Engine

Use the LLM to:

- Rank restaurant options.
- Explain why each recommendation matches the user's needs.
- Optionally provide a concise summary of top choices.

### 5) Output Display

Present top recommendations in a clear format with:

- Restaurant name
- Cuisine
- Rating
- Estimated cost
- AI-generated explanation
