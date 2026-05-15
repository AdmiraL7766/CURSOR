# Zomato-Style Next.js UI Generation Prompt

This document contains a comprehensive prompt designed for use with **Google Stitch** or other AI-driven UI generation tools. It specifies the technical stack, design language, and core features required to build a frontend identical to the Zomato web application.

---

## The Prompt

### Core Instruction
> "Act as a Senior Frontend Engineer and UI/UX Designer. Create a high-fidelity, responsive food delivery web application using **Next.js (App Router)** and **Tailwind CSS**. The design language must strictly follow the **Zomato 'Sushi' Design System**."

### Technical Stack
- **Framework:** Next.js 14+ (App Router, TypeScript).
- **Styling:** Tailwind CSS (for modern, utility-first design).
- **Components:** Headless UI or Radix UI for accessibility.
- **Icons:** Lucide React or FontAwesome.
- **Animations:** Framer Motion for smooth transitions (hover effects, page loads).

### Visual Identity (Zomato Style)
- **Primary Color:** Zomato Red (`#E23744`). Use this for CTAs, active states, and brand highlights.
- **Neutral Palette:**
  - Background: White (`#FFFFFF`) or subtle Off-white (`#F8F8F8`).
  - Text: Dark Charcoal (`#2D2D2D`) for headers, Muted Gray (`#696969`) for subtext.
  - Borders: Light Gray (`#E8E8E8`).
- **Typography:** Use a clean, geometric sans-serif like **Metropolis**, **Inter**, or **Roboto**. Maintain a strong visual hierarchy with bold headers and legible body text.
- **Layout:**
  - **Cards:** White cards with subtle box-shadows (`shadow-sm` or `shadow-md`) and slightly rounded corners (`rounded-lg`).
  - **Grid:** Responsive grid for restaurant listings (1 col mobile, 3-4 cols desktop).
  - **Visuals:** Use high-quality, vibrant food imagery as the primary focus.

### Core Components to Implement
1.  **Global Header:**
    - Sticky navigation bar.
    - Location picker (with pin icon).
    - Search bar: Large, white background, shadow, placeholder "Search for restaurant, cuisine or a dish".
    - Login/Signup buttons.
2.  **Navigation Tabs:**
    - Distinctive tabs for "Dining Out", "Delivery", and "Nightlife".
    - Active tab should have a circular colored background (light red for delivery, etc.) or a bold underline with the brand color.
3.  **Home Page (Hero Section):**
    - High-resolution food background.
    - Large Zomato logo and search interface overlay.
4.  **Collections Section:**
    - "Collections" header with a subtext like "Explore curated lists of top restaurants, cafes, pubs, and bars in [City]".
    - Visual cards with image overlays and title/place count.
5.  **Localities Section:**
    - Grid of white boxes representing different areas, showing locality name and "places" count.
6.  **Restaurant Cards:**
    - Top image with rounded corners.
    - **Rating Badge:** Right-aligned, colored block (Green `#24963F` for 4+, Yellow `#FFBA00` for 3+, Red `#E23744` for <3).
    - Price for two, delivery time, and distance subtext.
    - "Offers" label if applicable (blue text/icon).
7.  **Footer:**
    - Large multi-column footer with "About Zomato", "Zomaverse", "For Restaurants", and "Learn More".
    - Social icons and "Get the app" badges.

### Interaction & UX
- Implement **Hover States**: Cards should slightly scale or have a deeper shadow on hover.
- **Skeleton Loaders**: Design matching skeleton states for the restaurant grid.
- **Sticky Navigation**: The header should remain fixed on scroll for desktop.

---

## How to Use This Prompt
1.  **Copy** the content under the "The Prompt" section.
2.  **Paste** it into your AI generation tool (e.g., Google Stitch, v0.dev, or Claude Artifacts).
3.  **Refine** by asking for specific pages like "Now build the Restaurant Detail page with the menu items list."
