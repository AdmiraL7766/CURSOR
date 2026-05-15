"use client";

import React from "react";
import { Menu, X } from "lucide-react";

export default function Header() {
  const [menuOpen, setMenuOpen] = React.useState(false);

  return (
    <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-sm border-b border-gray-100 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
        {/* Logo */}
        <a href="/" className="text-2xl font-black italic text-[#E23744] select-none">
          zomato{" "}
          <span className="text-gray-400 font-light not-italic text-lg">
            AI
          </span>
        </a>

        {/* Desktop nav */}
        <nav className="hidden md:flex items-center gap-8 text-sm text-gray-500 font-medium">
          <a href="#" className="hover:text-gray-900 transition-colors">
            Investor Relations
          </a>
          <a href="#" className="hover:text-gray-900 transition-colors">
            Add restaurant
          </a>
          <a
            href="#"
            className="hover:text-gray-900 transition-colors"
          >
            Log in
          </a>
          <a
            href="#"
            className="btn-primary !py-1.5 !px-4 !text-sm"
          >
            Sign up
          </a>
        </nav>

        {/* Mobile menu toggle */}
        <button
          className="md:hidden p-2 text-gray-600"
          onClick={() => setMenuOpen(!menuOpen)}
          aria-label="Toggle navigation"
        >
          {menuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
        </button>
      </div>

      {/* Mobile dropdown */}
      {menuOpen && (
        <div className="md:hidden border-t border-gray-100 bg-white px-4 pb-4 pt-2 space-y-3">
          <a href="#" className="block text-sm text-gray-600 hover:text-gray-900">
            Investor Relations
          </a>
          <a href="#" className="block text-sm text-gray-600 hover:text-gray-900">
            Add restaurant
          </a>
          <a href="#" className="block text-sm text-gray-600 hover:text-gray-900">
            Log in
          </a>
          <a href="#" className="btn-primary block text-center text-sm">
            Sign up
          </a>
        </div>
      )}
    </header>
  );
}
