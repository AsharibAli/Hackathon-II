export type Role = 'user' | 'assistant';

export interface Message {
  id: string;
  role: Role;
  content: string;
  created_at: string;
}

export interface Conversation {
  id: string;
  messages: Message[];
  updated_at: string;
}

export interface ChatRequest {
  message: string;
}

export interface ChatResponse {
  message: Message;
}

export interface ConversationResponse {
  id: string;
  messages: Message[];
  updated_at: string;
}
