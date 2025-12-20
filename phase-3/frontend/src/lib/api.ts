/**
 * API client for communicating with the Todo Backend API.
 * Handles authentication, request/response formatting, and error handling.
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Custom error class for API errors.
 */
export class ApiError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    public data?: any
  ) {
    super(`API Error: ${status} ${statusText}`);
    this.name = "ApiError";
  }
}

/**
 * Get the authentication token from localStorage.
 */
function getAuthToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("auth_token");
}

/**
 * Set the authentication token in localStorage.
 */
export function setAuthToken(token: string): void {
  if (typeof window === "undefined") return;
  localStorage.setItem("auth_token", token);
}

/**
 * Remove the authentication token from localStorage.
 */
export function clearAuthToken(): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem("auth_token");
}

/**
 * Make an authenticated API request.
 */
async function fetchApi<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getAuthToken();
  const url = `${API_URL}${endpoint}`;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  // Add Authorization header if token exists
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  // Handle errors
  if (!response.ok) {
    let errorData;
    try {
      errorData = await response.json();
    } catch {
      errorData = { detail: response.statusText };
    }
    throw new ApiError(response.status, response.statusText, errorData);
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return null as T;
  }

  return response.json();
}

// ============================================
// Authentication API
// ============================================

export interface RegisterRequest {
  email: string;
  password: string;
}

export interface RegisterResponse {
  id: string;
  email: string;
  is_active: boolean;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export const authApi = {
  /**
   * Register a new user account.
   */
  register: async (data: RegisterRequest): Promise<RegisterResponse> => {
    return fetchApi<RegisterResponse>("/api/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  /**
   * Login with email and password.
   */
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    const response = await fetchApi<LoginResponse>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    });
    // Store the token
    setAuthToken(response.access_token);
    return response;
  },

  /**
   * Logout the current user.
   */
  logout: async (): Promise<void> => {
    try {
      await fetchApi<void>("/api/auth/logout", {
        method: "POST",
      });
    } finally {
      // Always clear the token, even if the API call fails
      clearAuthToken();
    }
  },

  /**
   * Get the current user's profile.
   */
  getProfile: async (): Promise<UserProfile> => {
    return fetchApi<UserProfile>("/api/auth/me");
  },

  /**
   * Update the current user's profile.
   */
  updateProfile: async (data: UpdateProfileRequest): Promise<UserProfile> => {
    return fetchApi<UserProfile>("/api/auth/me", {
      method: "PUT",
      body: JSON.stringify(data),
    });
  },
};

export interface UserProfile {
  id: string;
  email: string;
  full_name: string | null;
  profile_picture: string | null;
  is_active: boolean;
}

export interface UpdateProfileRequest {
  full_name?: string;
  profile_picture?: string;
}

// ============================================
// Tasks API
// ============================================

export interface Task {
  id: string;
  user_id: string;
  title: string;
  description?: string;
  is_completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateTaskRequest {
  title: string;
  description?: string;
}

export interface UpdateTaskRequest {
  title?: string;
  description?: string;
  is_completed?: boolean;
}

export const tasksApi = {
  /**
   * Get all tasks for the authenticated user.
   */
  getAll: async (): Promise<Task[]> => {
    return fetchApi<Task[]>("/api/tasks");
  },

  /**
   * Get a single task by ID.
   */
  getById: async (taskId: string): Promise<Task> => {
    return fetchApi<Task>(`/api/tasks/${taskId}`);
  },

  /**
   * Create a new task.
   */
  create: async (data: CreateTaskRequest): Promise<Task> => {
    return fetchApi<Task>("/api/tasks", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  /**
   * Update an existing task.
   */
  update: async (taskId: string, data: UpdateTaskRequest): Promise<Task> => {
    return fetchApi<Task>(`/api/tasks/${taskId}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  },

  /**
   * Delete a task.
   */
  delete: async (taskId: string): Promise<void> => {
    return fetchApi<void>(`/api/tasks/${taskId}`, {
      method: "DELETE",
    });
  },

  /**
   * Toggle task completion status.
   */
  toggleComplete: async (taskId: string): Promise<Task> => {
    return fetchApi<Task>(`/api/tasks/${taskId}/complete`, {
      method: "PATCH",
    });
  },
};

// ============================================
// Chat API
// ============================================

import { ChatResponse, ConversationResponse, ConversationSummary } from "../types/chat";

export const chatApi = {
  /**
   * Send a message to the AI assistant.
   */
  sendMessage: async (message: string, conversationId?: string): Promise<ChatResponse> => {
    return fetchApi<ChatResponse>("/api/chat/chat", {
      method: "POST",
      body: JSON.stringify({ message, conversation_id: conversationId }),
    });
  },

  /**
   * Get a specific conversation history.
   */
  getConversation: async (conversationId?: string): Promise<ConversationResponse> => {
    const params = conversationId ? `?conversation_id=${conversationId}` : "";
    return fetchApi<ConversationResponse>(`/api/chat/conversations${params}`);
  },
};

// ============================================
// Conversations API
// ============================================

export const conversationsApi = {
  /**
   * List all conversations for the current user.
   */
  list: async (): Promise<ConversationSummary[]> => {
    return fetchApi<ConversationSummary[]>("/api/conversations");
  },

  /**
   * Create a new conversation.
   */
  create: async (title?: string): Promise<ConversationSummary> => {
    return fetchApi<ConversationSummary>("/api/conversations", {
      method: "POST",
      body: JSON.stringify({ title }),
    });
  },

  /**
   * Get a specific conversation with messages.
   */
  get: async (conversationId: string): Promise<ConversationResponse> => {
    return fetchApi<ConversationResponse>(`/api/conversations/${conversationId}`);
  },

  /**
   * Rename a conversation.
   */
  rename: async (conversationId: string, title: string): Promise<ConversationSummary> => {
    return fetchApi<ConversationSummary>(`/api/conversations/${conversationId}`, {
      method: "PUT",
      body: JSON.stringify({ title }),
    });
  },

  /**
   * Delete a conversation.
   */
  delete: async (conversationId: string): Promise<void> => {
    return fetchApi<void>(`/api/conversations/${conversationId}`, {
      method: "DELETE",
    });
  },
};
