"use client";

import React, { useState } from "react";
import PreferenceForm from "@/components/PreferenceForm";
import RecommendationCard from "@/components/RecommendationCard";
import { Loader2, UtensilsCrossed, AlertCircle, Sparkles } from "lucide-react";

/** Matches the FinalResponsePayload from Phase 5 */
interface ApiResponse {
  status: string;
  message: string;
  preferences: Record<string, string>;
  summary: string;
  recommendations: Array<{
    rank: number;
    restaurant_id: string;
    title: string;
    cuisine: string;
    rating: number;
    estimated_cost_for_two: number;
    explanation: string;
    tags: string[];
  }>;
  metadata: Record<string, unknown>;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function Home() {
  const [response, setResponse] = useState<ApiResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchRecommendations = async (preferences: {
    location: string;
    cuisine: string;
    budget: string;
    min_rating: string;
    top_n: number;
    additional_preferences: string[];
  }) => {
    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const res = await fetch(`${API_BASE}/api/v1/recommendations`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(preferences),
      });

      if (!res.ok) {
        const detail = await res.json().catch(() => null);
        throw new Error(
          detail?.detail ?? `Server responded with ${res.status}`
        );
      }

      const data: ApiResponse = await res.json();
      setResponse(data);
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "An unexpected error occurred.";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const recommendations = response?.recommendations ?? [];

  return (
    <main className="min-h-screen">
      {/* ─── Hero Section ─── */}
      <section className="relative h-[380px] md:h-[420px] flex flex-col items-center justify-center text-white overflow-hidden">
        <img
          src="https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=1600&q=80"
          className="absolute inset-0 w-full h-full object-cover brightness-[0.35]"
          alt="Delicious food spread"
          loading="eager"
        />
        <div className="relative z-10 text-center px-4 max-w-3xl">
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-black mb-4 leading-tight">
            Discover the best food & drinks
          </h1>
          <p className="text-lg md:text-xl font-light text-gray-200">
            Personalized AI recommendations based on your mood and budget
          </p>
        </div>
      </section>

      {/* ─── Content ─── */}
      <div className="max-w-7xl mx-auto px-4 pb-20">
        <PreferenceForm onSubmit={fetchRecommendations} loading={loading} />

        {/* Error state */}
        {error && (
          <div className="mt-10 p-4 bg-red-50 border border-red-200 rounded-xl text-[#E23744] text-center font-medium flex items-center justify-center gap-2">
            <AlertCircle className="h-5 w-5 shrink-0" />
            {error}
          </div>
        )}

        {/* Loading state with skeletons */}
        {loading && (
          <div className="mt-16">
            <div className="flex items-center gap-3 mb-8">
              <Loader2 className="h-6 w-6 animate-spin text-[#E23744]" />
              <p className="text-lg font-medium text-gray-500">
                Curating your perfect picks…
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
                  <div className="skeleton h-48 rounded-none" />
                  <div className="p-4 space-y-3">
                    <div className="skeleton h-5 w-3/4" />
                    <div className="skeleton h-4 w-1/2" />
                    <div className="skeleton h-16 w-full" />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Results */}
        {!loading && response && (
          <div className="mt-16">
            {/* Summary */}
            {response.summary && (
              <div className="mb-8 p-4 bg-gradient-to-r from-red-50 to-orange-50 rounded-xl border border-red-100 flex items-start gap-3">
                <Sparkles className="h-5 w-5 text-[#E23744] shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm font-semibold text-gray-800 mb-0.5">
                    AI Summary
                  </p>
                  <p className="text-sm text-gray-600">{response.summary}</p>
                </div>
              </div>
            )}

            {recommendations.length > 0 ? (
              <>
                <h2 className="text-2xl md:text-3xl font-bold mb-8 text-gray-800">
                  Top Recommendations for you
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                  {recommendations.map((restaurant) => (
                    <RecommendationCard
                      key={restaurant.restaurant_id || restaurant.rank}
                      restaurant={restaurant}
                    />
                  ))}
                </div>
              </>
            ) : (
              <div className="text-center py-16 text-gray-400">
                <UtensilsCrossed className="h-16 w-16 mx-auto mb-4 opacity-30" />
                <p className="text-xl font-medium">
                  No restaurants matched your preferences
                </p>
                <p className="text-sm mt-2">
                  Try broadening your filters or changing the location
                </p>
              </div>
            )}
          </div>
        )}

        {/* Empty / initial state */}
        {!loading && !response && !error && (
          <div className="mt-16 flex flex-col items-center justify-center text-gray-300 py-20 border-2 border-dashed border-gray-100 rounded-3xl">
            <UtensilsCrossed className="h-20 w-20 mb-4 opacity-20" />
            <p className="text-xl font-medium">
              Enter your preferences above to see recommendations
            </p>
          </div>
        )}
      </div>
    </main>
  );
}
