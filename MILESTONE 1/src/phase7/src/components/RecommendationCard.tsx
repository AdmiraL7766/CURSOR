import React from "react";
import { Star, MapPin, Award } from "lucide-react";

/**
 * Matches the Phase 5 RecommendationCard schema exactly:
 * rank, restaurant_id, title, cuisine, rating, estimated_cost_for_two, explanation, tags
 */
interface RecommendationData {
  rank: number;
  restaurant_id: string;
  title: string;
  cuisine: string;
  rating: number;
  estimated_cost_for_two: number;
  explanation: string;
  tags: string[];
}

// Curated food images to cycle through (Unsplash provides stable URLs)
const FOOD_IMAGES = [
  "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=600&q=80",
  "https://images.unsplash.com/photo-1552566626-52f8b828add9?w=600&q=80",
  "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=600&q=80",
  "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=600&q=80",
  "https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=600&q=80",
  "https://images.unsplash.com/photo-1540189549336-e6e99c3679fe?w=600&q=80",
];

const TAG_COLORS: Record<string, string> = {
  "top-rated": "bg-green-100 text-green-700",
  "high-rated": "bg-emerald-50 text-emerald-600",
  "budget-friendly": "bg-blue-50 text-blue-600",
  "premium": "bg-purple-50 text-purple-600",
  "fallback-ranked": "bg-gray-100 text-gray-500",
};

export default function RecommendationCard({
  restaurant,
}: {
  restaurant: RecommendationData;
}) {
  const getRatingColor = (rating: number) => {
    if (rating >= 4.0) return "bg-[#24963F]";
    if (rating >= 3.0) return "bg-[#DB7C38]";
    return "bg-[#E23744]";
  };

  const imageUrl = FOOD_IMAGES[(restaurant.rank - 1) % FOOD_IMAGES.length];

  return (
    <div className="card group">
      {/* Image */}
      <div className="relative h-48 bg-gray-100 overflow-hidden">
        <img
          src={imageUrl}
          alt={restaurant.title}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          loading="lazy"
        />

        {/* Rank badge */}
        <div className="absolute top-3 left-3 bg-black/60 backdrop-blur-sm text-white text-xs font-bold px-2 py-1 rounded-md flex items-center gap-1">
          <Award className="h-3 w-3" />#{restaurant.rank}
        </div>

        {/* Cuisine tag */}
        <div className="absolute bottom-3 left-3 bg-white/90 backdrop-blur px-2.5 py-1 rounded-md text-[10px] font-bold uppercase tracking-widest text-gray-700">
          {restaurant.cuisine}
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        {/* Title + Rating */}
        <div className="flex justify-between items-start mb-2">
          <h3 className="font-bold text-lg leading-tight line-clamp-1 pr-2">
            {restaurant.title}
          </h3>
          <div
            className={`${getRatingColor(restaurant.rating)} text-white px-2 py-0.5 rounded flex items-center gap-1 text-sm font-bold shadow-sm shrink-0`}
          >
            {restaurant.rating.toFixed(1)}
            <Star className="h-3 w-3 fill-white stroke-white" />
          </div>
        </div>

        {/* Cuisine + Cost */}
        <div className="flex justify-between text-sm text-gray-500 mb-3 font-medium">
          <span className="truncate flex-1 pr-2">{restaurant.cuisine}</span>
          <span className="whitespace-nowrap">
            ₹{restaurant.estimated_cost_for_two.toLocaleString("en-IN")} for two
          </span>
        </div>

        {/* Tags */}
        {restaurant.tags.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mb-3">
            {restaurant.tags.map((tag) => (
              <span
                key={tag}
                className={`tag-pill ${TAG_COLORS[tag] ?? "bg-gray-100 text-gray-500"}`}
              >
                {tag.replace("-", " ")}
              </span>
            ))}
          </div>
        )}

        {/* AI explanation */}
        <div className="bg-red-50/60 p-3 rounded-xl border border-red-100">
          <p className="text-xs text-gray-700 leading-relaxed">
            <span className="font-bold text-[#E23744] mr-1">Why this?</span>
            {restaurant.explanation}
          </p>
        </div>
      </div>
    </div>
  );
}
