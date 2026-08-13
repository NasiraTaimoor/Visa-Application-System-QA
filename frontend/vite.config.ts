/// <reference types="vitest/config" />
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: { "@shared": "/src/shared" },
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./tests/setup.ts"],
    projects: [
      { extends: true, test: { name: "unit", include: ["tests/unit/**/*.test.{ts,tsx}"] } },
      { extends: true, test: { name: "ui", include: ["tests/ui/**/*.test.{ts,tsx}"] } },
      { extends: true, test: { name: "e2e", include: ["tests/e2e/**/*.test.{ts,tsx}"] } },
      {
        extends: true,
        test: { name: "accessibility", include: ["tests/accessibility/**/*.test.{ts,tsx}"] },
      },
    ],
  },
});
