"use client";

import React from "react";

export default function Footer() {
  const year = new Date().getFullYear();

  return (
    <footer className="bg-[#1C1C1C] text-gray-400 mt-20">
      <div className="max-w-7xl mx-auto px-4 py-12">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-10">
          {/* Column 1 */}
          <div>
            <h4 className="text-white font-bold text-sm mb-4 uppercase tracking-wider">
              About Zomato AI
            </h4>
            <ul className="space-y-2 text-sm">
              <li><a href="#" className="hover:text-white transition-colors">Who We Are</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Blog</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Careers</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Contact</a></li>
            </ul>
          </div>

          {/* Column 2 */}
          <div>
            <h4 className="text-white font-bold text-sm mb-4 uppercase tracking-wider">
              Zomaverse
            </h4>
            <ul className="space-y-2 text-sm">
              <li><a href="#" className="hover:text-white transition-colors">Blinkit</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Feeding India</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Hyperpure</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Zomatoland</a></li>
            </ul>
          </div>

          {/* Column 3 */}
          <div>
            <h4 className="text-white font-bold text-sm mb-4 uppercase tracking-wider">
              For Restaurants
            </h4>
            <ul className="space-y-2 text-sm">
              <li><a href="#" className="hover:text-white transition-colors">Partner With Us</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Apps For You</a></li>
            </ul>
          </div>

          {/* Column 4 */}
          <div>
            <h4 className="text-white font-bold text-sm mb-4 uppercase tracking-wider">
              Learn More
            </h4>
            <ul className="space-y-2 text-sm">
              <li><a href="#" className="hover:text-white transition-colors">Privacy</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Security</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Terms</a></li>
            </ul>
          </div>
        </div>

        <div className="border-t border-gray-700 pt-6 flex flex-col md:flex-row items-center justify-between text-xs">
          <p>© {year} Zomato AI. All rights reserved.</p>
          <p className="mt-2 md:mt-0">
            Built with AI · Powered by Next.js
          </p>
        </div>
      </div>
    </footer>
  );
}
