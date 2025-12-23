export type Role = 'user' | 'assistant';

export interface Message {
  id: string;
  role: Role;
  content: string;
  created_at: string;
}

export interface ConversationSummary {
  id: string;
  title: string | null;
  updated_at: string;
}

export interface Conversation {
  id: string;
  title: string | null;
  messages: Message[];
  updated_at: string;
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
}

export interface ChatResponse {
  message: Message;
  conversation_id: string;
}

export interface ConversationResponse {
  id: string;
  title: string | null;
  messages: Message[];
  updated_at: string;
}
