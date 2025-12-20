/**
 * Better Auth configuration for the Todo application.
 * Handles authentication with JWT tokens and integrates with the backend API.
 */
import { betterAuth } from "better-auth";
import { nextCookies } from "better-auth/next-js";

const authSecret = process.env.BETTER_AUTH_SECRET || "dev-secret-key-change-in-production";
const authUrl = process.env.BETTER_AUTH_URL || "http://localhost:3000";

export const auth = betterAuth({
  secret: authSecret,
  baseURL: authUrl,
  database: {
    // Better Auth will use cookies for session management
    // Backend API handles user persistence
    type: "sqlite",
    sqlite: {
      database: ":memory:", // In-memory for session state only
    },
  },
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false, // Simplified for baseline
  },
  plugins: [nextCookies()],
});

export type Session = typeof auth.$Infer.Session;
