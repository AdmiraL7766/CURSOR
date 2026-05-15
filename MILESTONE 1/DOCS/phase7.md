# Phase 7: Frontend Web Application

## Overview
Phase 7 provides a responsive, Zomato-styled web interface using **Next.js 14 (App Router)** and **Tailwind CSS**. Users enter their dining preferences and receive AI-powered restaurant recommendations from the Phase 6 backend.

## Objectives
- Modern, responsive UI matching the Zomato design language (signature red `#E23744`, card-based layout, dark footer).
- Full preference capture: location, cuisine, budget tier, and minimum rating.
- Live connection to the Phase 6 FastAPI backend (`POST /api/v1/recommendations`).
- Loading skeletons, error handling, and AI summary display.

## Project Structure

```
src/phase7/
├── next.config.mjs          # Next.js configuration (image domains)
├── postcss.config.js         # PostCSS + Tailwind pipeline
├── tailwind.config.ts        # Tailwind content paths & theme
├── tsconfig.json             # TypeScript compiler options
├── package.json              # Dependencies & scripts
└── src/
    ├── app/
    │   ├── globals.css       # Design tokens, component classes, skeleton animation
    │   ├── layout.tsx        # Root layout with Header + Footer
    │   └── page.tsx          # Home page: hero, form, results grid
    └── components/
        ├── Header.tsx        # Sticky nav with mobile hamburger menu
        ├── Footer.tsx        # Dark 4-column Zomato-style footer
        ├── PreferenceForm.tsx # Location, cuisine, budget, rating inputs
        └── RecommendationCard.tsx  # Restaurant card with rating badge, tags, AI explanation
```

## API Integration
The frontend sends a `POST` request to the backend with this payload (matching `RecommendationRequest` from Phase 6):

```json
{
  "location": "Bellandur",
  "cuisine": "North Indian",
  "budget": "medium",
  "min_rating": "3.5",
  "top_n": 5
}
```

The response follows the `FinalResponsePayload` schema from Phase 5:

```json
{
  "status": "success",
  "message": "Recommendations generated successfully.",
  "summary": "Top 5 North Indian options in Bellandur…",
  "preferences": { ... },
  "recommendations": [
    {
      "rank": 1,
      "restaurant_id": "123",
      "title": "Restaurant Name",
      "cuisine": "North Indian",
      "rating": 4.2,
      "estimated_cost_for_two": 800.0,
      "explanation": "Great match because…",
      "tags": ["high-rated", "budget-friendly"]
    }
  ],
  "metadata": { ... }
}
```

## Environment Configuration
Set the backend URL via environment variable (defaults to `http://localhost:8000`):

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## How to Run

```bash
cd src/phase7
npm install
npm run dev
```

The frontend runs on `http://localhost:3000`. Ensure the Phase 6 backend is running on port 8000.

## Design Decisions
- **Zomato Red (#E23744)** for all CTAs and brand accents.
- **Rating badges** use Zomato's color scheme: green (4.0+), amber (3.0+), red (<3.0).
- **Skeleton loaders** provide visual feedback during API calls.
- **AI Summary block** surfaces the LLM-generated overview before individual cards.
- **Tag pills** (top-rated, budget-friendly, premium, fallback-ranked) come directly from the Phase 5 formatter.
