"use client";

import React, { useState, useEffect, useRef } from "react";
import { Search, MapPin, Star, ChefHat, Tag } from "lucide-react";

interface PreferenceFormProps {
  onSubmit: (data: {
    location: string;
    cuisine: string;
    budget: string;
    min_rating: string;
    top_n: number;
    additional_preferences: string[];
  }) => void;
  loading: boolean;
}

const CUISINES = [
  "Any",
  "North Indian",
  "South Indian",
  "Chinese",
  "Italian",
  "Continental",
  "Mughlai",
  "Fast Food",
  "Cafe",
  "Biryani",
  "Street Food",
];

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function PreferenceForm({ onSubmit, loading }: PreferenceFormProps) {
  const [formData, setFormData] = useState({
    location: "",
    cuisine: "Any",
    budget: "medium",
    min_rating: "3.5",
    top_n: 5,
    additional_preferences: "",
  });

  const [locations, setLocations] = useState<string[]>([]);
  const [filteredLocations, setFilteredLocations] = useState<string[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const suggestionsRef = useRef<HTMLDivElement>(null);

  // Fetch available locations from API on mount
  useEffect(() => {
    fetch(`${API_BASE}/api/v1/locations`)
      .then((res) => res.json())
      .then((data) => setLocations(data.locations ?? []))
      .catch(() => {
        /* silently degrade — freeform input still works */
      });
  }, []);

  // Close suggestions dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (suggestionsRef.current && !suggestionsRef.current.contains(e.target as Node)) {
        setShowSuggestions(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleLocationChange = (value: string) => {
    update("location", value);
    if (value.trim().length > 0 && locations.length > 0) {
      const matches = locations.filter((loc) =>
        loc.toLowerCase().includes(value.toLowerCase())
      );
      setFilteredLocations(matches.slice(0, 8));
      setShowSuggestions(matches.length > 0);
    } else {
      setShowSuggestions(false);
    }
  };

  const selectLocation = (loc: string) => {
    update("location", loc);
    setShowSuggestions(false);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setShowSuggestions(false);
    
    const additional = formData.additional_preferences
      .split(",")
      .map(p => p.trim())
      .filter(p => p.length > 0);

    onSubmit({
      ...formData,
      additional_preferences: additional,
    });
  };

  const update = (field: string, value: string | number) =>
    setFormData((prev) => ({ ...prev, [field]: value }));

  return (
    <form
      onSubmit={handleSubmit}
      className="bg-white p-6 md:p-8 rounded-2xl shadow-xl -mt-12 relative z-10 max-w-6xl mx-auto border border-gray-100"
    >
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-4 items-end">
        {/* Location with autocomplete */}
        <div className="lg:col-span-1 relative" ref={suggestionsRef}>
          <label className="block text-xs font-bold text-gray-400 mb-1.5 uppercase tracking-wider">
            Location
          </label>
          <div className="relative">
            <MapPin className="absolute left-3 top-3 text-[#E23744] h-4 w-4" />
            <input
              id="location-input"
              type="text"
              required
              placeholder="e.g. Bellandur"
              className="input-field pl-10"
              value={formData.location}
              onChange={(e) => handleLocationChange(e.target.value)}
              onFocus={() => {
                if (formData.location.trim() && filteredLocations.length > 0) {
                  setShowSuggestions(true);
                }
              }}
              autoComplete="off"
            />
          </div>
          {/* Location suggestions dropdown */}
          {showSuggestions && filteredLocations.length > 0 && (
            <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-48 overflow-y-auto z-50">
              {filteredLocations.map((loc) => (
                <button
                  key={loc}
                  type="button"
                  className="w-full text-left px-4 py-2.5 text-sm text-gray-700 hover:bg-red-50 hover:text-[#E23744] transition-colors flex items-center gap-2"
                  onClick={() => selectLocation(loc)}
                >
                  <MapPin className="h-3 w-3 text-gray-400 shrink-0" />
                  {loc}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Cuisine */}
        <div className="lg:col-span-1">
          <label className="block text-xs font-bold text-gray-400 mb-1.5 uppercase tracking-wider">
            Cuisine
          </label>
          <div className="relative">
            <ChefHat className="absolute left-3 top-3 text-gray-400 h-4 w-4" />
            <select
              id="cuisine-select"
              className="input-field pl-10 appearance-none bg-white"
              value={formData.cuisine}
              onChange={(e) => update("cuisine", e.target.value)}
            >
              {CUISINES.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Budget */}
        <div className="lg:col-span-1">
          <label className="block text-xs font-bold text-gray-400 mb-1.5 uppercase tracking-wider">
            Budget
          </label>
          <select
            id="budget-select"
            className="input-field appearance-none bg-white"
            value={formData.budget}
            onChange={(e) => update("budget", e.target.value)}
          >
            <option value="low">₹ Pocket Friendly</option>
            <option value="medium">₹₹ Mid Range</option>
            <option value="high">₹₹₹ Luxury</option>
          </select>
        </div>

        {/* Min Rating */}
        <div className="lg:col-span-1">
          <label className="block text-xs font-bold text-gray-400 mb-1.5 uppercase tracking-wider">
            Min Rating
          </label>
          <div className="relative">
            <Star className="absolute left-3 top-3 text-yellow-400 h-4 w-4 fill-yellow-400" />
            <select
              id="rating-select"
              className="input-field pl-10 appearance-none bg-white"
              value={formData.min_rating}
              onChange={(e) => update("min_rating", e.target.value)}
            >
              <option value="0">Any rating</option>
              <option value="3.0">3.0+</option>
              <option value="3.5">3.5+</option>
              <option value="4.0">4.0+</option>
              <option value="4.5">4.5+</option>
            </select>
          </div>
        </div>

        {/* Additional Preferences */}
        <div className="lg:col-span-1">
          <label className="block text-xs font-bold text-gray-400 mb-1.5 uppercase tracking-wider truncate">
            Extras (comma-separated)
          </label>
          <div className="relative">
            <Tag className="absolute left-3 top-3 text-gray-400 h-4 w-4" />
            <input
              id="preferences-input"
              type="text"
              placeholder="e.g. romantic, live music"
              className="input-field pl-10"
              value={formData.additional_preferences}
              onChange={(e) => update("additional_preferences", e.target.value)}
            />
          </div>
        </div>

        {/* Submit */}
        <button
          id="search-button"
          type="submit"
          disabled={loading}
          className="btn-primary flex items-center justify-center gap-2 h-[42px] disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <span className="flex items-center gap-2">
              <span className="h-4 w-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              Searching…
            </span>
          ) : (
            <>
              <Search className="h-4 w-4" />
              Search
            </>
          )}
        </button>
      </div>
    </form>
  );
}
